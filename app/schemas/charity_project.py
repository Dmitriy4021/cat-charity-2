from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import (
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    DESCRIPTION_MIN_LENGTH
)


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    description: Optional[str] = Field(
        None,
        min_length=DESCRIPTION_MIN_LENGTH
    )
    full_amount: Optional[int] = Field(None, gt=0)

    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(
        ...,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    description: str = Field(
        ...,
        min_length=DESCRIPTION_MIN_LENGTH
    )
    full_amount: int = Field(..., gt=0)


class CharityProjectCreateDB(CharityProjectBase):
    model_config = ConfigDict(extra='allow')


class CharityProjectUpdate(CharityProjectBase):
    pass

    @field_validator('name', 'description')
    @classmethod
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError(f'Параметр {value} не может быть пустой')
        return value
