"""Audit-log repository (append-only)."""

import uuid
from datetime import datetime

from sqlalchemy import Select, select

from app.core.pagination import PageParams
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
    sortable = {"created_at": "created_at"}

    async def list_events(
        self,
        params: PageParams,
        *,
        actor_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[AuditLog], int]:
        stmt: Select = select(AuditLog)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if entity_type is not None:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if date_from is not None:
            stmt = stmt.where(AuditLog.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(AuditLog.created_at <= date_to)
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort).offset(params.offset).limit(
            params.limit
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total
