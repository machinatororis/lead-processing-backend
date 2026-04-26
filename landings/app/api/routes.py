from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.db.models import Affiliate, Offer
from core.app.db.session import get_db_session
from landings.app.core.security import get_current_affiliate
from landings.app.schemas.leads import LeadAcceptedResponse, LeadCreate
from landings.app.services.redis_queue import push_lead_to_queue

router = APIRouter()


@router.post(
    "/lead",
    response_model=LeadAcceptedResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept lead from landing page",
    description=(
        "Accepts a lead from a landing page, validates affiliate ownership "
        "using Bearer JWT token, checks that the offer exists and pushes "
        "the lead payload to Redis queue for background processing."
    ),
    responses={
        200: {
            "description": "Lead accepted and pushed to Redis queue",
            "content": {
                "application/json": {
                    "example": {"status": "accepted"}
                }
            },
        },
        400: {
            "description": "Invalid request data or offer does not exist",
            "content": {
                "application/json": {
                    "example": {"detail": "Offer does not exist"}
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
        403: {
            "description": "affiliate_id does not match token affiliate id",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "affiliate_id does not match token affiliate id"
                    }
                }
            },
        },
    },
)
async def create_lead(
    lead: LeadCreate,
    current_affiliate: Annotated[Affiliate, Depends(get_current_affiliate)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LeadAcceptedResponse:
    if lead.affiliate_id != current_affiliate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="affiliate_id does not match token affiliate id",
        )

    offer_result = await session.execute(
        select(Offer).where(Offer.id == lead.offer_id)
    )
    offer = offer_result.scalar_one_or_none()

    if offer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer does not exist",
        )

    await push_lead_to_queue(lead)

    return LeadAcceptedResponse(status="accepted")