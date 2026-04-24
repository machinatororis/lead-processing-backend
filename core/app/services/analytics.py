from collections import defaultdict
from datetime import date, datetime, time
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.app.db.models import Lead


GroupBy = Literal["date", "offer"]


async def get_leads_analytics(
    session: AsyncSession,
    *,
    affiliate_id: int,
    date_from: date,
    date_to: date,
    group: GroupBy,
) -> list[dict]:
    start_datetime = datetime.combine(date_from, time.min)
    end_datetime = datetime.combine(date_to, time.max)

    result = await session.execute(
        select(Lead)
        .options(selectinload(Lead.offer))
        .where(
            Lead.affiliate_id == affiliate_id,
            Lead.created_at >= start_datetime,
            Lead.created_at <= end_datetime,
        )
        .order_by(Lead.created_at.asc())
    )

    leads = result.scalars().all()

    grouped: dict[str, list[Lead]] = defaultdict(list)

    for lead in leads:
        if group == "date":
            key = lead.created_at.date().isoformat()
        else:
            offer_name = lead.offer.name if lead.offer else f"Offer {lead.offer_id}"
            key = f"{lead.offer_id}: {offer_name}"

        grouped[key].append(lead)

    return [
        {
            "group": key,
            "count": len(group_leads),
            "leads": group_leads,
        }
        for key, group_leads in grouped.items()
    ]