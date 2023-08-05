"""
Module containing methods for interacting with the IEX energy API
"""
from pandas import DataFrame

from algoralabs.data.iex.utils import __base_request, __async_base_request
from algoralabs.decorators.data import data_request, async_data_request


def __build_params(**kwargs) -> dict:
    # default query params
    params = {
        'range': '1m',
        'sort': 'asc'
    }

    params.update(kwargs)
    return params


@data_request
def historical_oil_prices(symbol: str, **kwargs) -> DataFrame:
    """
    Wrapper for IEX's Historical Energy Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
        symbol: "DCOILWTICO" or "DCOILBRENTEU"
        **kwargs: Optional args to pass to the IEX API

    Returns:
        Historical oil prices for the provided symbol
    """
    params = __build_params(**kwargs)
    return __base_request(f"time-series/energy/{symbol}", **params)


@async_data_request
async def async_historical_oil_prices(symbol: str, **kwargs) -> DataFrame:
    """
    Async wrapper for IEX's Historical Energy Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
        symbol: "DCOILWTICO" or "DCOILBRENTEU"
        **kwargs: Optional args to pass to the IEX API

    Returns:
        Historical oil prices for the provided symbol
    """
    # default query params
    params = __build_params(**kwargs)
    return await __async_base_request(f"time-series/energy/{symbol}", **params)