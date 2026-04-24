from pydantic import BaseModel, Field, field_validator


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=5, max_length=50)
    country: str = Field(min_length=2, max_length=2)
    offer_id: int
    affiliate_id: int

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        value = value.upper()

        if not value.isalpha():
            raise ValueError("Country must be ISO 3166-1 alpha-2 code")

        return value


class LeadAcceptedResponse(BaseModel):
    status: str