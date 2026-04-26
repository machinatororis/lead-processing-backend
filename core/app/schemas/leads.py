from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GroupBy = Literal["date", "offer"]


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Lead ID", examples=[1])
    name: str = Field(..., description="Lead name", examples=["Oleksii"])
    phone: str = Field(..., description="Lead phone number", examples=["+380982342123"])
    country: str = Field(..., description="Country code in ISO 3166-1 alpha-2 format", examples=["UA"])
    offer_id: int = Field(..., description="Offer ID", examples=[1])
    affiliate_id: int = Field(..., description="Affiliate ID", examples=[1])
    created_at: datetime = Field(..., description="Lead creation datetime in database")


class LeadsGroupResponse(BaseModel):
    group: str = Field(
        ...,
        description="Group key. Date in YYYY-MM-DD format or offer identifier with name",
        examples=["2026-04-24"],
    )
    count: int = Field(..., description="Number of leads in this group", examples=[1])
    leads: list[LeadResponse] = Field(..., description="List of leads in this group")


class LeadsAnalyticsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "group_by": "date",
                "items": [
                    {
                        "group": "2026-04-24",
                        "count": 1,
                        "leads": [
                            {
                                "id": 1,
                                "name": "Oleksii",
                                "phone": "+380982342123",
                                "country": "UA",
                                "offer_id": 1,
                                "affiliate_id": 1,
                                "created_at": "2026-04-24T21:21:17.503491Z",
                            }
                        ],
                    }
                ],
            }
        }
    )

    group_by: GroupBy = Field(..., description="Selected grouping mode", examples=["date"])
    items: list[LeadsGroupResponse] = Field(..., description="Grouped analytics items")