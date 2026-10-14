from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class DonationBase(BaseModel):
    full_amount: Optional[int] = Field(None, gt=0)
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    full_amount: int = Field(..., gt=0)


class DonationCreateDB(DonationBase):
    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationUpdateDB(DonationBase):
    model_config = ConfigDict(extra='allow')


class DonationDB(DonationBase):
    id: int
    create_date: datetime
    user_id: Optional[int] = None
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
