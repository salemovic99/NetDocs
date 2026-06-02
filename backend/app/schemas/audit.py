"""Audit log read schema (PRD §10 /audit-log)."""

import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    action: str
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    diff: dict | None = None
    ip_address: str | None = None
    created_at: datetime
