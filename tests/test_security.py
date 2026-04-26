import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from core.app.core.security import get_current_affiliate as get_core_current_affiliate
from landings.app.core.security import get_current_affiliate as get_landings_current_affiliate
from scripts.create_token import create_token


class FakeResult:
    def scalar_one_or_none(self):
        return None


class FakeSession:
    async def execute(self, *args, **kwargs):
        return FakeResult()


@pytest.mark.asyncio
async def test_core_rejects_token_with_non_existing_affiliate() -> None:
    token = create_token(affiliate_id=999)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_core_current_affiliate(
            credentials=credentials,
            session=FakeSession(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Affiliate from token does not exist"


@pytest.mark.asyncio
async def test_landings_rejects_token_with_non_existing_affiliate() -> None:
    token = create_token(affiliate_id=999)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_landings_current_affiliate(
            credentials=credentials,
            session=FakeSession(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Affiliate from token does not exist"