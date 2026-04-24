from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.db.models import Affiliate
from core.app.db.session import get_db_session
from landings.app.core.config import settings

bearer_scheme = HTTPBearer()


async def get_current_affiliate(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Affiliate:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    affiliate_id = payload.get("id")

    if affiliate_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload does not contain affiliate id",
        )

    result = await session.execute(
        select(Affiliate).where(Affiliate.id == int(affiliate_id))
    )
    affiliate = result.scalar_one_or_none()

    if affiliate is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Affiliate from token does not exist",
        )

    return affiliate