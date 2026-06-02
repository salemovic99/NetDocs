"""Read-only audit-log query service (PRD §10 /audit-log)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PageParams
from app.repositories.audit import AuditLogRepository


class AuditQueryService:
    def __init__(self, session: AsyncSession):
        self.repo = AuditLogRepository(session)

    async def list(self, params: PageParams, **filters):
        return await self.repo.list_events(params, **filters)
