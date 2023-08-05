""" Function to get data from live database """
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_PV
from nowcasting_datamodel.models.pv import (
    PVSystem,
    PVSystemSQL,
    PVYield,
    PVYieldSQL,
    pv_output,
    solar_sheffield_passiv,
)
from nowcasting_datamodel.read.read_pv import get_pv_systems, get_pv_yield

from nowcasting_dataset.data_sources.pv.utils import encode_label

logger = logging.getLogger(__name__)


def get_metadata_from_database(providers: List[str] = None) -> pd.DataFrame:
    """
    Get metadata from database

    Returns: pandas data frame with the following columns
        - latitude
        - longitude
        - kwp
        The index is the pv_system_id
    """

    if providers is None:
        providers = [pv_output, solar_sheffield_passiv]

    # make database connection
    url = os.getenv("DB_URL_PV")
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    pv_system_all_df = []
    for provider in providers:

        with db_connection.get_session() as session:
            # read pv systems
            pv_systems: List[PVSystemSQL] = get_pv_systems(session=session, provider=provider)

            # format locations
            pv_systems_df = pd.DataFrame(
                [(PVSystem.from_orm(pv_system)).__dict__ for pv_system in pv_systems]
            )

        if len(pv_systems_df) == 0:
            return pd.DataFrame(
                columns=["pv_system_id", "latitude", "longitude", "installed_capacity_kw"]
            )

        pv_systems_df.index = encode_label(pv_systems_df["pv_system_id"], label=provider)
        pv_systems_df = pv_systems_df[["latitude", "longitude", "installed_capacity_kw"]]

        pv_system_all_df.append(pv_systems_df)

    pv_system_all_df = pd.concat(pv_system_all_df)

    return pv_system_all_df


def get_pv_power_from_database(
    history_duration: timedelta,
    interpolate_minutes: int,
    load_extra_minutes: int,
    load_extra_minutes_and_keep: Optional[int] = 30,
    providers: List[str] = None,
) -> pd.DataFrame:
    """
    Get pv power from database

    Args:
        history_duration: a timedelta of how many minutes to load in the past
        interpolate_minutes: how many minutes we should interpolate the data froward for
        load_extra_minutes: the extra minutes we should load, in order to load more data.
            This is because some data from a site lags significantly behind 'now'.
            These extra minutes are not kept but used to interpolate results.
        load_extra_minutes_and_keep: extra minutes to load, but also keep this data.
        providers: optional list of providers

    Returns:pandas data frame with the following columns pv systems indexes
    The index is the datetime

    """

    logger.info("Loading PV data from database")
    logger.debug(f"{history_duration=} {interpolate_minutes=} {load_extra_minutes=}")

    if providers is None:
        providers = [pv_output, solar_sheffield_passiv]

    extra_duration = timedelta(minutes=load_extra_minutes)
    now = pd.to_datetime(datetime.now(tz=timezone.utc)).ceil("5T")
    start_utc = now - history_duration - timedelta(minutes=load_extra_minutes_and_keep)
    start_utc_extra = start_utc - extra_duration

    # create empty dataframe with 5 mins periods
    empty_df = pd.DataFrame(index=pd.date_range(start=start_utc_extra, end=now, freq="5T"))

    # make database connection
    url = os.getenv("DB_URL_PV")
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    with db_connection.get_session() as session:
        pv_yields: List[PVYieldSQL] = get_pv_yield(
            session=session, start_utc=start_utc_extra, correct_data=True, providers=providers
        )

        logger.debug(f"Found {len(pv_yields)} PV yields from the database")

        pv_yields_df = pd.DataFrame(
            [(PVYield.from_orm(pv_yield)).__dict__ for pv_yield in pv_yields]
        )

    if len(pv_yields_df) == 0:
        logger.warning("Found no pv yields, this might cause an error")
    else:
        logger.debug(f"Found {len(pv_yields_df)} pv yields")

    if len(pv_yields_df) == 0:
        return pd.DataFrame(columns=["pv_system_id"])

    # get the system id from 'pv_system_id=xxxx provider=.....'
    pv_yields_df["pv_system_id"] = (
        pv_yields_df["pv_system"].astype(str).str.split(" ").str[0].str.split("=").str[-1]
    )

    pv_yields_df["provider"] = (
        pv_yields_df["pv_system"]
        .astype(str)
        .str.split(" ")
        .str[1]
        .str.split("=")
        .str[1]
        .str.replace("'", "")
    )

    # encode pv system id
    for provider in pv_output, solar_sheffield_passiv:
        idx = pv_yields_df["provider"] == provider

        pv_yields_df.loc[idx, "pv_system_id"] = encode_label(
            pv_yields_df.loc[idx, "pv_system_id"], label=provider
        )

    # pivot on
    pv_yields_df = pv_yields_df[["datetime_utc", "pv_system_id", "solar_generation_kw"]]
    pv_yields_df.drop_duplicates(
        ["datetime_utc", "pv_system_id", "solar_generation_kw"], keep="last", inplace=True
    )
    pv_yields_df = pv_yields_df.pivot(
        index="datetime_utc", columns="pv_system_id", values="solar_generation_kw"
    )

    # we are going interpolate using 'quadratic' method and we need at least 3 data points,
    # Lets make sure we have double that, therefore we drop system with less than 6 nans
    N = len(pv_yields_df)
    pv_yields_df = pv_yields_df.loc[:, pv_yields_df.notnull().sum() >= 6]
    logger.debug(f"Have dropped {len(pv_yields_df) - N} PV systems, as they don't have enough data")

    # interpolate in between, maximum 'live_interpolate_minutes' mins
    # note data is in 5 minutes chunks
    pv_yields_df = empty_df.join(pv_yields_df)
    limit = int(interpolate_minutes / 5)
    if limit > 0:
        try:
            pv_yields_df.interpolate(limit=limit, inplace=True, method="quadratic")
        except Exception as e:
            logger.exception(e)
            logger.debug(pv_yields_df)
            raise Exception(f"Could not do interpolate with limit {limit}")

    # filter out the extra minutes loaded
    logger.debug(f"{len(pv_yields_df)} of datetimes before filter on {start_utc}")
    pv_yields_df = pv_yields_df[pv_yields_df.index >= start_utc]
    logger.debug(f"{len(pv_yields_df)} of datetimes after filter on {start_utc}")

    return pv_yields_df
