from typing import Optional, List
from pandas import DataFrame

from algoralabs.data.sdr import AssetClass, Repository
from algoralabs.decorators.data import data_request, async_data_request
from algoralabs.common.requests import __get_request, __async_get_request
from algoralabs.data.datasets.query import query_dataset, async_query_dataset
from algoralabs.data.sdr.utils import DataFilter, transform_data_filter
from algoralabs.common.functions import to_pandas_with_index, no_transform


def _get_by_date_request_info(asset_class: AssetClass, date: str, repos: Optional[List[Repository]] = None) -> dict:
    if repos is None:
        repos = [Repository.CME, Repository.DTCC, Repository.ICE]

    repos_param = ",".join([repo.name for repo in repos])
    return {
        'endpoint': f"data/sdr/{asset_class.value}/{date}?repository={repos_param}"
    }


@data_request(transformer=lambda data: to_pandas_with_index(data, index='execution_timestamp'))
def get_by_date(asset_class: AssetClass, date: str, repos: Optional[List[Repository]] = None) -> DataFrame:
    """
    Get all SDR data by asset class, date and repositories

    Args:
        asset_class: AssetClass Enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        date: Date in YYYY-MM-DD format (e.g. "2022-01-01")
        repos: (Optional) Repository Enum List (e.g. [CME, DTCC, ICE])

    Returns: Dataframe of data by data
    """
    request_info = _get_by_date_request_info(asset_class, date, repos)
    return __get_request(**request_info)


@async_data_request(transformer=lambda data: to_pandas_with_index(data, index='execution_timestamp'))
async def async_get_by_date(asset_class: AssetClass, date: str, repos: Optional[List[Repository]] = None) -> DataFrame:
    """
    Get all SDR data by asset class, date and repositories

    Args:
        asset_class: AssetClass Enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        date: Date in YYYY-MM-DD format (e.g. "2022-01-01")
        repos: (Optional) Repository Enum List (e.g. [CME, DTCC, ICE])

    Returns: Dataframe of data by data
    """
    request_info = _get_by_date_request_info(asset_class, date, repos)
    return await __async_get_request(**request_info)


def _get_distinct_in_field_request_info(asset_class: AssetClass, field: str) -> dict:
    return {
        'endpoint': f"data/sdr/{asset_class.value}/{field}/distinct"
    }


@data_request(transformer=no_transform)
def get_distinct_in_field(asset_class: AssetClass, field: str) -> List[str]:
    """
    Get all distinct values in field

    Args:
        asset_class: AssetClass Enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        field: One of the following fields:
            action
            asset_id
            asset_id_type
            asset_name
            cleared
            collateralization
            contract_subtype
            contract_type
            day_count_convention
            end_user_exception
            execution_venue
            fixed_payment_currency
            leg_1_asset
            leg_1_average_method
            leg_1_currency
            leg_1_delivery_location
            leg_1_exchange
            leg_1_location
            leg_1_payment_frequency
            leg_1_price_unit
            leg_1_reset_frequency
            leg_1_type
            leg_1_unit
            leg_2_asset
            leg_2_average_method
            leg_2_currency
            leg_2_delivery_location
            leg_2_exchange
            leg_2_location
            leg_2_payment_frequency
            leg_2_price_unit
            leg_2_reset_frequency
            leg_2_type
            leg_2_unit
            option_currency
            option_expiration_frequency
            option_lockout_period
            option_strike_price_currency
            option_style
            option_type
            other_payment_currency
            post_execution_event
            price_adjustment_unit
            repository
            sector
            settlement_currency
            settlement_frequency
            settlement_method
            submission_type
            subsector
            transaction_type
            underlying_unit
            upfront_fee_currency
            upfront_fee_unit

    Returns: List of all distinct values in field
    """
    request_info = _get_distinct_in_field_request_info(asset_class, field)
    return __get_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_get_distinct_in_field(asset_class: AssetClass, field: str) -> List[str]:
    """
    Get all distinct values in field

    Args:
        asset_class: AssetClass Enum (COMMODITY, CREDIT, EQUITY, FOREX, RATES)
        field: One of the following fields:
            action
            asset_id
            asset_id_type
            asset_name
            cleared
            collateralization
            contract_subtype
            contract_type
            day_count_convention
            end_user_exception
            execution_venue
            fixed_payment_currency
            leg_1_asset
            leg_1_average_method
            leg_1_currency
            leg_1_delivery_location
            leg_1_exchange
            leg_1_location
            leg_1_payment_frequency
            leg_1_price_unit
            leg_1_reset_frequency
            leg_1_type
            leg_1_unit
            leg_2_asset
            leg_2_average_method
            leg_2_currency
            leg_2_delivery_location
            leg_2_exchange
            leg_2_location
            leg_2_payment_frequency
            leg_2_price_unit
            leg_2_reset_frequency
            leg_2_type
            leg_2_unit
            option_currency
            option_expiration_frequency
            option_lockout_period
            option_strike_price_currency
            option_style
            option_type
            other_payment_currency
            post_execution_event
            price_adjustment_unit
            repository
            sector
            settlement_currency
            settlement_frequency
            settlement_method
            submission_type
            subsector
            transaction_type
            underlying_unit
            upfront_fee_currency
            upfront_fee_unit

    Returns: List of all distinct values in field
    """
    request_info = _get_distinct_in_field_request_info(asset_class, field)
    return await __async_get_request(**request_info)


def _commodity_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "2880e242-8db4-49e2-aad3-e0339931582e",
        'json': transform_data_filter(filter)
    }


@data_request
def commodity(filter: Optional[DataFilter] = None):
    """
    SDR Commodity dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _commodity_request_info(filter)
    return query_dataset(**request_info)


@async_data_request
async def async_commodity(filter: Optional[DataFilter] = None):
    """
    SDR Commodity dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _commodity_request_info(filter)
    return await async_query_dataset(**request_info)


def _credit_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "04863ce6-b179-420c-bef4-eb71f5391141",
        'json': transform_data_filter(filter)
    }


@data_request
def credit(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Credit dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _credit_request_info(filter)
    return query_dataset(**request_info)


@async_data_request
async def async_credit(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Credit dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _credit_request_info(filter)
    return await async_query_dataset(**request_info)


def _equity_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "0f839686-a878-473b-a8a9-d2de2dcdd42c",
        'json': transform_data_filter(filter)
    }


@data_request
def equity(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Equity dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _equity_request_info(filter)
    return query_dataset(**request_info)


@async_data_request
async def async_equity(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Equity dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _equity_request_info(filter)
    return await async_query_dataset(**request_info)


def _forex_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "f1137a7c-13db-451b-9603-f17dfa8bb147",
        'json': transform_data_filter(filter)
    }


@data_request
def forex(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Forex dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _forex_request_info(filter)
    return query_dataset(**request_info)


@async_data_request
async def async_forex(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Forex dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _forex_request_info(filter)
    return await async_query_dataset(**request_info)


def _rates_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "a812f19c-354c-48e9-b86e-af055c631fcc",
        'json': transform_data_filter(filter)
    }


@data_request
def rates(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Rates dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _rates_request_info(filter)
    return query_dataset(**request_info)


@async_data_request
async def async_rates(filter: Optional[DataFilter] = None) -> DataFrame:
    """
    SDR Rates dataset

    :param filter: Dataset Query FieldFilter
    :return: Dataframe of data
    """
    request_info = _rates_request_info(filter)
    return await async_query_dataset(**request_info)
