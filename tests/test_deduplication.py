from core.app.services.deduplication import build_dedup_key


def test_build_dedup_key_returns_same_key_for_same_lead_data() -> None:
    key_1 = build_dedup_key(
        name="Oleksii",
        phone="+380982342123",
        offer_id=1,
        affiliate_id=1,
    )
    key_2 = build_dedup_key(
        name="Oleksii",
        phone="+380982342123",
        offer_id=1,
        affiliate_id=1,
    )

    assert key_1 == key_2


def test_build_dedup_key_normalizes_name_spaces_and_case() -> None:
    key_1 = build_dedup_key(
        name=" Oleksii ",
        phone="+380982342123",
        offer_id=1,
        affiliate_id=1,
    )
    key_2 = build_dedup_key(
        name="oleksii",
        phone="+380982342123",
        offer_id=1,
        affiliate_id=1,
    )

    assert key_1 == key_2


def test_build_dedup_key_returns_different_key_for_different_phone() -> None:
    key_1 = build_dedup_key(
        name="Oleksii",
        phone="+380982342123",
        offer_id=1,
        affiliate_id=1,
    )
    key_2 = build_dedup_key(
        name="Oleksii",
        phone="+380982342124",
        offer_id=1,
        affiliate_id=1,
    )

    assert key_1 != key_2