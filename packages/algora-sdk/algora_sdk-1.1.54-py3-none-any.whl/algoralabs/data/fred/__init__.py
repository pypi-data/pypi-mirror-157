from typing import Optional

from pydantic import Field

from algoralabs.common.base import Base
from algoralabs.common.types import Datetime


class FredQuery(Base):
    api_key: str
    series_id: str
    file_type: str = Field(default='json')
    observation_start: Optional[Datetime] = None
    observation_end: Optional[Datetime] = None
