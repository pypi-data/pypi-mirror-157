"""
Module containing util methods for interacting with the algoralabs' sdr API
"""
from typing import Optional, Union, Any, Dict

from algoralabs.data.sdr import APIFieldFilter, FieldFilter, LogicalDisplayName, DataFilter


def __transform_filter(filter: Union[FieldFilter, APIFieldFilter]) -> APIFieldFilter:
    if isinstance(filter, APIFieldFilter):
        return filter

    return APIFieldFilter(
        logical_display=LogicalDisplayName(
            logical_name=filter.field,
            display_name=filter.field
        ),
        operator=filter.operator,
        selected_values=filter.selected_values
    )


def transform_data_filter(data_filter: Optional[DataFilter]) -> Optional[Dict[str, Any]]:
    """
    Transforms a data filter to a dict

    Args:
        data_filter: Data filter to convert to a dict

    Returns:
        A dict representation of a data filter
    """
    if data_filter is not None:
        transformed_filter = DataFilter(
            date_range=data_filter.date_range,
            filters=[__transform_filter(f) for f in data_filter.filters]
        )

        return transformed_filter.dict()

    return None
