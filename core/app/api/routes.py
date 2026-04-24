from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.core.security import get_current_affiliate
from core.app.db.models import Affiliate
from core.app.db.session import get_db_session
from core.app.schemas.leads import LeadsAnalyticsResponse
from core.app.services.analytics import get_leads_analytics

router = APIRouter()


@router.get(
    "/leads",
    response_model=LeadsAnalyticsResponse,
    summary="Get affiliate leads analytics",
)
async def get_leads(
    current_affiliate: Annotated[Affiliate, Depends(get_current_affiliate)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    date_from: Annotated[date, Query(description="Start date, inclusive")],
    date_to: Annotated[date, Query(description="End date, inclusive")],
    group: Annotated[Literal["date", "offer"], Query(description="Group by date or offer")],
) -> LeadsAnalyticsResponse:
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be less than or equal to date_to",
        )

    items = await get_leads_analytics(
        session,
        affiliate_id=current_affiliate.id,
        date_from=date_from,
        date_to=date_to,
        group=group,
    )

    return LeadsAnalyticsResponse(
        group_by=group,
        items=items,
    )