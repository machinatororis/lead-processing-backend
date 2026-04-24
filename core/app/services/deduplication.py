import hashlib

from redis.asyncio import Redis

DEDUP_TTL_SECONDS = 600


def build_dedup_key(
    *,
    name: str,
    phone: str,
    offer_id: int,
    affiliate_id: int,
) -> str:
    raw_key = f"{name.strip().lower()}:{phone.strip()}:{offer_id}:{affiliate_id}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"lead_dedup:{digest}"


async def is_duplicate_lead(
    redis_client: Redis,
    *,
    name: str,
    phone: str,
    offer_id: int,
    affiliate_id: int,
) -> bool:
    dedup_key = build_dedup_key(
        name=name,
        phone=phone,
        offer_id=offer_id,
        affiliate_id=affiliate_id,
    )

    was_set = await redis_client.set(
        dedup_key,
        "1",
        ex=DEDUP_TTL_SECONDS,
        nx=True,
    )

    return not bool(was_set)