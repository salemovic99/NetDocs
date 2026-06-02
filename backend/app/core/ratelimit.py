"""Redis-backed fixed-window rate limiting (PRD §7 rate limits)."""

import logging

from redis.asyncio import Redis

logger = logging.getLogger("netdocs.ratelimit")


async def hit(
    redis: Redis | None, key: str, limit: int, window_seconds: int
) -> tuple[bool, int]:
    """Register one hit against `key`. Returns (allowed, retry_after_seconds).

    Fixed-window counter: first hit in a window sets the TTL. Fails open if Redis
    is unavailable (availability over strict enforcement), matching the app's
    best-effort Redis pattern elsewhere.
    """
    if redis is None:
        return True, 0
    redis_key = f"ratelimit:{key}"
    try:
        count = await redis.incr(redis_key)
        if count == 1:
            await redis.expire(redis_key, window_seconds)
        if count > limit:
            ttl = await redis.ttl(redis_key)
            return False, max(ttl, 1)
        return True, 0
    except Exception:  # pragma: no cover - degrade gracefully
        logger.warning("redis unavailable; rate limit not enforced", exc_info=True)
        return True, 0
