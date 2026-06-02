"""Redis-backed session/refresh-token family store (PRD §6.10 FR-38/FR-39).

Each login starts a session keyed by a `family` id. The session tracks the single
currently-valid refresh `jti`. On refresh the jti rotates; presenting a stale jti
for a known family is treated as **token reuse** and revokes the whole family.
"""

import time

from redis.asyncio import Redis

from app.core.config import settings

_SESSION_KEY = "session:{family}"
_USER_INDEX = "user_sessions:{user_id}"


class SessionStore:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(
        self,
        *,
        family: str,
        user_id: str,
        jti: str,
        ip: str | None,
        user_agent: str | None,
    ) -> None:
        now = str(int(time.time()))
        mapping = {
            "user_id": user_id,
            "current_jti": jti,
            "created_at": now,
            "last_used": now,
            "ip": ip or "",
            "user_agent": (user_agent or "")[:256],
        }
        ttl = settings.refresh_token_ttl_seconds
        skey = _SESSION_KEY.format(family=family)
        await self.redis.hset(skey, mapping=mapping)
        await self.redis.expire(skey, ttl)
        ukey = _USER_INDEX.format(user_id=user_id)
        await self.redis.sadd(ukey, family)
        await self.redis.expire(ukey, ttl)

    async def get(self, family: str) -> dict | None:
        data = await self.redis.hgetall(_SESSION_KEY.format(family=family))
        return data or None

    async def rotate(self, family: str, new_jti: str) -> None:
        skey = _SESSION_KEY.format(family=family)
        await self.redis.hset(
            skey, mapping={"current_jti": new_jti, "last_used": str(int(time.time()))}
        )
        await self.redis.expire(skey, settings.refresh_token_ttl_seconds)

    async def revoke(self, family: str) -> None:
        skey = _SESSION_KEY.format(family=family)
        data = await self.redis.hgetall(skey)
        if data and (user_id := data.get("user_id")):
            await self.redis.srem(_USER_INDEX.format(user_id=user_id), family)
        await self.redis.delete(skey)

    async def revoke_all(self, user_id: str) -> int:
        ukey = _USER_INDEX.format(user_id=user_id)
        families = await self.redis.smembers(ukey)
        for family in families:
            await self.redis.delete(_SESSION_KEY.format(family=family))
        await self.redis.delete(ukey)
        return len(families)

    async def list_for_user(self, user_id: str) -> list[dict]:
        ukey = _USER_INDEX.format(user_id=user_id)
        families = await self.redis.smembers(ukey)
        sessions: list[dict] = []
        for family in families:
            data = await self.redis.hgetall(_SESSION_KEY.format(family=family))
            if data:
                sessions.append({"family": family, **data})
            else:
                await self.redis.srem(ukey, family)
        return sessions
