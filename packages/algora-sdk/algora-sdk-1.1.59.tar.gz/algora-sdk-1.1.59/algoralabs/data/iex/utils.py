"""
Module containing util methods for IEX interaction
"""
from algoralabs.common.requests import __get_request, __async_get_request


def __build_url(extension: str) -> str:
    return f"data/datasets/query/iex/{extension}"


def __base_request(extension: str, **kwargs):
    """
    Base request util for IEX API calls

    Args:
        extension: URI extension
        **kwargs: request query params

    Returns:
        IEX repsponse
    """
    return __get_request(endpoint=__build_url(extension), params=kwargs)


async def __async_base_request(extension: str, **kwargs):
    """
    Async base request util for IEX API calls

    Args:
        extension: URI extension
        **kwargs: request query params

    Returns:
        IEX repsponse
    """
    return await __async_get_request(endpoint=__build_url(extension), params=kwargs)
