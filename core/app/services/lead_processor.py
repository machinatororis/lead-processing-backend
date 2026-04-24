from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.db.models import Affiliate, Lead, Offer


async def save_lead(
    session: AsyncSession,
    *,
    name: str,
    phone: str,
    country: str,
    offer_id: int,
    affiliate_id: int,
) -> Lead | None:
    offer_result = await session.execute(select(Offer).where(Offer.id == offer_id))
    offer = offer_result.scalar_one_or_none()

    if offer is None:
        return None

    affiliate_result = await session.execute(
        select(Affiliate).where(Affiliate.id == affiliate_id)
    )
    affiliate = affiliate_result.scalar_one_or_none()

    if affiliate is None:
        return None

    lead = Lead(
        name=name,
        phone=phone,
        country=country,
        offer_id=offer_id,
        affiliate_id=affiliate_id,
    )

    session.add(lead)
    await session.commit()
    await session.refresh(lead)

    return lead