"""
Module containing methods for interacting with the IEX stocks API
"""
from typing import List, Union, Dict
from pandas import DataFrame

from algoralabs.data.iex.utils import __base_request, __async_base_request
from algoralabs.common.functions import no_transform, transform_one_or_many
from algoralabs.decorators.data import data_request, async_data_request


def _symbols_request_info() -> dict:
    return {
        "extension": f"ref-data/symbols"
    }


@data_request
def symbols() -> DataFrame:
    """
    Wrapper for IEX's API to get symbols that IEX Cloud supports for intraday price updates.

    Reference: https://iexcloud.io/docs/api/#symbols

    Returns:
         IEX supported symbols
    """
    request_info = _symbols_request_info()
    return __base_request(**request_info)


@async_data_request
async def async_symbols() -> DataFrame:
    """
    Async wrapper for IEX's API to get symbols that IEX Cloud supports for intraday price updates.

    Reference: https://iexcloud.io/docs/api/#symbols

    Returns:
        IEX supported symbols
    """
    request_info = _symbols_request_info()
    return await __async_base_request(**request_info)


def _historical_prices_request_info(*symbol: str, **kwargs) -> dict:
    request_info = {
        'range': '1m',
        'sort': 'asc'
    }
    request_info.update(kwargs)

    if len(symbol) > 1:
        request_info.update({
            'extension': "stock/market/batch",
            'symbols': ','.join(symbol),
            'types': 'chart'
        })
    else:
        request_info.update({'extension': f"time-series/HISTORICAL_PRICES/{symbol[0]}"})

    return request_info


@data_request(transformer=lambda d: transform_one_or_many(d, 'chart'))
def historical_prices(*symbol: str, **kwargs) -> Union[DataFrame, Dict[str, DataFrame]]:
    """
    Wrapper for IEX's Historical Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
         symbol: (*str) Stock symbol(s), such as "AAPL" or "AAPL", "FB"
         **kwargs: Optional args to pass to the IEX API

    Returns:
        Historical prices for the symbol(s) requested
    """
    # default query params
    request_info = _historical_prices_request_info(*symbol, **kwargs)
    return __base_request(**request_info)


@async_data_request(transformer=lambda d: transform_one_or_many(d, 'chart'))
async def async_historical_prices(*symbol: str, **kwargs) -> Union[DataFrame, Dict[str, DataFrame]]:
    """
    Async wrapper for IEX's Historical Prices via Time Series API

    Reference: https://iexcloud.io/docs/api/#time-series-endpoint

    Args:
         symbol: (*str) Stock symbol(s), such as "AAPL" or "AAPL", "FB"
         **kwargs: Optional args to pass to the IEX API

    Returns:
        Historical prices for the symbol(s) requested
    """
    # default query params
    request_info = _historical_prices_request_info(*symbol, **kwargs)
    return await __async_base_request(**request_info)


def _news_request_info(symbol: str, kwargs):
    request_info = {
        "extension": f"time-series/news/{symbol}"
    }
    request_info.update(kwargs)
    return request_info


@data_request
def news(symbol: str, **kwargs) -> DataFrame:
    """
    Wrapper for IEX's API to get news for given symbol
    Reference: https://iexcloud.io/docs/api/#news

    Args:
        symbol: (str) Stock symbol, such as AAPL
        **kwargs: Optional args to pass to the IEX API

    Returns:
        News for the symbol requested
    """
    request_info = _news_request_info(symbol, kwargs)
    return __base_request(**request_info)


@async_data_request
async def async_news(symbol: str, **kwargs) -> DataFrame:
    """
    Async wrapper for IEX's API to get news for given symbol
    Reference: https://iexcloud.io/docs/api/#news

    Args:
        symbol: (str) Stock symbol, such as AAPL
        **kwargs: Optional args to pass to the IEX API

    Returns:
        News for the symbol requested
    """
    request_info = _news_request_info(symbol, kwargs)
    return await __async_base_request(**request_info)


def _peer_group_request_info(symbol: str) -> dict:
    return {
        "extension": f"stock/{symbol}/peers"
    }


@data_request(transformer=no_transform)
def peer_group(symbol: str) -> List[str]:
    """
    Wrapper for IEX's API to get stock peers

    Reference: https://iexcloud.io/docs/api/#peers

    Args:
        symbol: (str) Stock symbol, such as AAPL

    Returns:
         List of symbols
    """
    request_info = _peer_group_request_info(symbol)
    return __base_request(**request_info)


@async_data_request(transformer=no_transform)
async def async_peer_group(symbol: str) -> List[str]:
    """
    Async wrapper for IEX's API to get stock peers

    Reference: https://iexcloud.io/docs/api/#peers

    Args:
        symbol: (str) Stock symbol, such as AAPL

    Returns:
         List of symbols
    """
    request_info = _peer_group_request_info(symbol)
    return await __async_base_request(**request_info)


