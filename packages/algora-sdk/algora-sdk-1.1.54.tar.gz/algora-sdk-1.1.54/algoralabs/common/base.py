"""
Module containing the base implementation classes for passing on inherited attributes
"""
from abc import ABC
from datetime import date
from enum import Enum
from pydantic import BaseModel

from algoralabs.common.functions import date_to_timestamp


class BaseEnum(str, Enum):
    """
    This is the class for all enums to inherit from

    Note: Inheriting from str is necessary to correctly serialize output of enum
    """
    pass


class Base(ABC, BaseModel):
    """
    This is an abstract class for all pydantic models to inherit from
    """
    class Config:
        # Use enum values when using .dict() on object
        use_enum_values = True

        # Converts dates to timestamps
        json_encoders = {
            date: date_to_timestamp
        }
