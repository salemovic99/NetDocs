"""Liveness / readiness / metrics probes (PRD §13)."""

import logging
import os

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Response
from sqlalchemy import text

from app.core.deps import DbSession, RedisClient
from app.core.metrics import metrics_response

logger = logging.getLogger("netdocs.health")
router = APIRouter(tags=["health"])

_ALEMBIC_INI = os.path.join(os.getcwd(), "alembic.ini")


@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


def _expected_head() -> str | None:
    try:
        cfg = Config(_ALEMBIC_INI)
        return ScriptDirectory.from_config(cfg).get_current_head()
    except Exception:  # pragma: no cover
        return None


async def _migrations_current(session: DbSession) -> bool:
    """True when the DB's alembic version matches the latest migration head."""
    head = _expected_head()
    if head is None:
        return False
    try:
        conn = await session.connection()
        current = await conn.run_sync(
            lambda sync_conn: MigrationContext.configure(sync_conn).get_current_revision()
        )
        return current == head
    except Exception:  # pragma: no cover
        return False


@router.get("/readyz")
async def readyz(session: DbSession, redis: RedisClient) -> dict:
    checks = {"database": False, "redis": False, "migrations_current": False}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass
    try:
        checks["redis"] = bool(await redis.ping())
    except Exception:
        pass
    if checks["database"]:
        checks["migrations_current"] = await _migrations_current(session)
    ready = all(checks.values())
    return {"status": "ready" if ready else "degraded", "checks": checks}


@router.get("/metrics")
async def metrics() -> Response:
    return metrics_response()
