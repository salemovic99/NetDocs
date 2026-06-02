"""Audit service — records every write and auth/permission event (PRD §13, §22.11)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def record(
        self,
        *,
        action: str,
        actor_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        diff: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Stage an audit row. Flushed/committed within the caller's transaction."""
        entry = AuditLog(
            action=action,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            diff=diff,
            ip_address=ip_address,
        )
        self.session.add(entry)
        return entry
