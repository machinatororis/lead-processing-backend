from jose import jwt

from core.app.core.config import settings
from scripts.create_token import create_token


def test_create_token_contains_affiliate_id() -> None:
    token = create_token(affiliate_id=1)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["id"] == 1


def test_create_token_contains_expiration() -> None:
    token = create_token(affiliate_id=1)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert "exp" in payload