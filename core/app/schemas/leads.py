from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


GroupBy = Literal["date", "offer"]


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    country: str
    offer_id: int
    affiliate_id: int
    created_at: datetime


class LeadsGroupResponse(BaseModel):
    group: str
    count: int
    leads: list[LeadResponse]


class LeadsAnalyticsResponse(BaseModel):
    group_by: GroupBy
    items: list[LeadsGroupResponse]