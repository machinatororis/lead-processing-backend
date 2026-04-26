import pytest
from pydantic import ValidationError

from landings.app.schemas.leads import LeadCreate


def test_lead_create_valid_data() -> None:
    lead = LeadCreate(
        name="Oleksii",
        phone="+380982342123",
        country="UA",
        offer_id=1,
        affiliate_id=1,
    )

    assert lead.name == "Oleksii"
    assert lead.phone == "+380982342123"
    assert lead.country == "UA"
    assert lead.offer_id == 1
    assert lead.affiliate_id == 1


def test_lead_create_normalizes_country_to_uppercase() -> None:
    lead = LeadCreate(
        name="Oleksii",
        phone="+380982342123",
        country="ua",
        offer_id=1,
        affiliate_id=1,
    )

    assert lead.country == "UA"


def test_lead_create_rejects_invalid_country_code() -> None:
    with pytest.raises(ValidationError):
        LeadCreate(
            name="Oleksii",
            phone="+380982342123",
            country="U1",
            offer_id=1,
            affiliate_id=1,
        )


def test_lead_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        LeadCreate(
            name="",
            phone="+380982342123",
            country="UA",
            offer_id=1,
            affiliate_id=1,
        )