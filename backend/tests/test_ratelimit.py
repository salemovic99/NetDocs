"""Unit tests for the Redis fixed-window rate limiter (via fakeredis)."""

import fakeredis.aioredis
import pytest

from app.core import ratelimit


@pytest.fixture()
def redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


async def test_allows_up_to_limit(redis):
    results = [await ratelimit.hit(redis, "k", 3, 60) for _ in range(3)]
    assert all(allowed for allowed, _ in results)


async def test_blocks_over_limit(redis):
    for _ in range(3):
        await ratelimit.hit(redis, "k", 3, 60)
    allowed, retry_after = await ratelimit.hit(redis, "k", 3, 60)
    assert not allowed
    assert retry_after >= 1


async def test_separate_keys_independent(redis):
    await ratelimit.hit(redis, "a", 1, 60)
    allowed, _ = await ratelimit.hit(redis, "b", 1, 60)
    assert allowed


async def test_fails_open_without_redis():
    allowed, retry_after = await ratelimit.hit(None, "k", 1, 60)
    assert allowed and retry_after == 0
