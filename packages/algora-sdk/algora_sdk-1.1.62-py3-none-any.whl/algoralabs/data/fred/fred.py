"""
Module containing methods for interacting with the FRED API
"""
import asyncio
from datetime import date
from typing import Dict, Any

import pandas as pd
from pandas import DataFrame

from algoralabs.common.requests import __async_get_request, __get_request
from algoralabs.data.fred import FredQuery
from algoralabs.decorators.data import data_request, async_data_request


def transform_fred_observations(data: Dict[str, Any]) -> DataFrame:
    return pd.DataFrame(data['observations'])


def _get_series_info(query: FredQuery) -> dict:
    return {
        "endpoint": "/series/observations",
        "url_key": "fred",
        "params": query.dict(exclude_none=True)
    }


@data_request(transformer=transform_fred_observations)
def get_series(query: FredQuery) -> DataFrame:
    """

    """
    request_info = _get_series_info(query)
    return __get_request(**request_info)


@async_data_request(transformer=transform_fred_observations)
async def async_get_series(query: FredQuery) -> DataFrame:
    """

    """
    request_info = _get_series_info(query)
    return await __async_get_request(**request_info)


async def main():
    rf_series = await async_get_series(
        FredQuery(
            api_key='cf546a3e4c455f3e2f295e75acddd6bb',
            series_id='DGS1MO',
            observation_start=date(2022, 1, 1)
        )
    )

    print(rf_series)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
