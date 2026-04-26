from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Oleksii",
                "phone": "+380982342123",
                "country": "UA",
                "offer_id": 1,
                "affiliate_id": 1,
            }
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Lead name",
        examples=["Oleksii"],
    )
    phone: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Lead phone number",
        examples=["+380982342123"],
    )
    country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Country code in ISO 3166-1 alpha-2 format",
        examples=["UA"],
    )
    offer_id: int = Field(
        ...,
        description="Offer ID selected by the lead",
        examples=[1],
    )
    affiliate_id: int = Field(
        ...,
        description="Affiliate ID. Must match affiliate id from Bearer token",
        examples=[1],
    )

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        value = value.upper()

        if not value.isalpha():
            raise ValueError("Country must be ISO 3166-1 alpha-2 code")

        return value


class LeadAcceptedResponse(BaseModel):
    status: str = Field(
        ...,
        description="Lead acceptance status",
        examples=["accepted"],
    )