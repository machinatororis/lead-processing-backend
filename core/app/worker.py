import asyncio
import json
import logging
import sys
from typing import Any

from redis.asyncio import Redis

from core.app.core.config import settings
from core.app.db.session import async_session_factory
from core.app.services.deduplication import is_duplicate_lead
from core.app.services.lead_processor import save_lead


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def parse_lead(raw_value: str) -> dict[str, Any]:
    data = json.loads(raw_value)

    required_fields = {"name", "phone", "country", "offer_id", "affiliate_id"}
    missing_fields = required_fields - data.keys()

    if missing_fields:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing_fields))}")

    return data


async def process_raw_lead(raw_value: str) -> None:
    try:
        data = parse_lead(raw_value)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Invalid lead payload skipped: %s", exc)
        return

    is_duplicate = await is_duplicate_lead(
        redis_client,
        name=data["name"],
        phone=data["phone"],
        offer_id=int(data["offer_id"]),
        affiliate_id=int(data["affiliate_id"]),
    )

    if is_duplicate:
        logger.info("Duplicate lead skipped: %s", data)
        return

    async with async_session_factory() as session:
        lead = await save_lead(
            session,
            name=data["name"],
            phone=data["phone"],
            country=data["country"],
            offer_id=int(data["offer_id"]),
            affiliate_id=int(data["affiliate_id"]),
        )

    if lead is None:
        logger.warning("Lead skipped because offer or affiliate does not exist: %s", data)
        return

    logger.info("Lead saved: id=%s", lead.id)


async def run_worker() -> None:
    logger.info("Core worker started. Queue: %s", settings.redis_leads_queue)

    while True:
        item = await redis_client.brpop(settings.redis_leads_queue, timeout=5)

        if item is None:
            continue

        _, raw_value = item
        await process_raw_lead(raw_value)


if __name__ == "__main__":
    asyncio.run(run_worker())