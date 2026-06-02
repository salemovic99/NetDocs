"""Attachment schemas (PRD §10 attachments)."""

import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class AttachmentRead(ORMModel):
    id: uuid.UUID
    problem_id: uuid.UUID | None = None
    device_id: uuid.UUID | None = None
    filename: str
    mime_type: str
    size_bytes: int
    av_status: str
    uploaded_by: uuid.UUID | None = None
    created_at: datetime
