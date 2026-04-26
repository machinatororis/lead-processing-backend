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
    description=(
        "Returns leads analytics for the authenticated affiliate. "
        "Affiliate is resolved from Bearer JWT token. "
        "Results can be grouped by date or offer and filtered by lead creation date."
    ),
    responses={
        200: {
            "description": "Leads analytics successfully returned",
            "content": {
                "application/json": {
                    "example": {
                        "group_by": "date",
                        "items": [
                            {
                                "group": "2026-04-24",
                                "count": 1,
                                "leads": [
                                    {
                                        "id": 1,
                                        "name": "Oleksii",
                                        "phone": "+380982342123",
                                        "country": "UA",
                                        "offer_id": 1,
                                        "affiliate_id": 1,
                                        "created_at": "2026-04-24T21:21:17.503491Z",
                                    }
                                ],
                            }
                        ],
                    }
                }
            },
        },
        400: {
            "description": "Invalid date range",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "date_from must be less than or equal to date_to"
                    }
                }
            },
        },
        401: {
            "description": "Invalid or missing Bearer token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication token"}
                }
            },
        },
        422: {
            "description": "Validation error for query parameters",
        },
    },
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