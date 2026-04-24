import json

from redis.asyncio import Redis

from landings.app.core.config import settings
from landings.app.schemas.leads import LeadCreate


redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def push_lead_to_queue(lead: LeadCreate) -> None:
    await redis_client.lpush(
        settings.redis_leads_queue,
        json.dumps(lead.model_dump()),
    )