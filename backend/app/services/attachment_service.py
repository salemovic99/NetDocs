"""Attachment service: validated upload, AV-gated download, delete (PRD §6.4, §12)."""

from __future__ import annotations

import logging
import uuid

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import files, storage
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.models.attachment import Attachment
from app.models.device import Device
from app.models.problem import Problem
from app.repositories.attachment import AttachmentRepository
from app.services.audit_service import AuditService

logger = logging.getLogger("netdocs.attachments")

AV_SCAN_QUEUE = "av:scan"


class AttachmentService:
    def __init__(self, session: AsyncSession, redis: Redis | None = None):
        self.session = session
        self.redis = redis
        self.repo = AttachmentRepository(session)
        self.audit = AuditService(session)

    async def _enqueue_scan(self, attachment_id: uuid.UUID) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.lpush(AV_SCAN_QUEUE, str(attachment_id))
        except Exception:  # pragma: no cover - degrade gracefully
            logger.warning("redis unavailable; AV scan not enqueued", exc_info=True)

    async def _upload(
        self,
        *,
        problem_id: uuid.UUID | None,
        device_id: uuid.UUID | None,
        filename: str,
        content_type: str | None,
        content: bytes,
        actor_id: uuid.UUID | None,
    ) -> Attachment:
        safe_name, mime, ext = files.validate_upload(filename, content_type, content)
        storage_key = storage.save(content, ext)

        clamav = settings.clamav_enabled
        attachment = Attachment(
            problem_id=problem_id,
            device_id=device_id,
            filename=safe_name,
            storage_key=storage_key,
            mime_type=mime,
            size_bytes=len(content),
            av_status="pending" if clamav else "clean",
            uploaded_by=actor_id,
        )
        self.repo.add(attachment)
        await self.repo.flush()
        if clamav:
            await self._enqueue_scan(attachment.id)
        self.audit.record(
            action="attachment.upload",
            actor_id=actor_id,
            entity_type="attachments",
            entity_id=attachment.id,
            diff={"filename": safe_name, "mime": mime, "size": len(content)},
        )
        await self.session.commit()
        await self.session.refresh(attachment)
        return attachment

    async def upload_to_problem(
        self,
        problem_id: uuid.UUID,
        filename: str,
        content_type: str | None,
        content: bytes,
        actor_id: uuid.UUID | None,
    ) -> Attachment:
        if await self.session.get(Problem, problem_id) is None:
            raise NotFoundError("Problem not found")
        return await self._upload(
            problem_id=problem_id,
            device_id=None,
            filename=filename,
            content_type=content_type,
            content=content,
            actor_id=actor_id,
        )

    async def upload_to_device(
        self,
        device_id: uuid.UUID,
        filename: str,
        content_type: str | None,
        content: bytes,
        actor_id: uuid.UUID | None,
    ) -> Attachment:
        if await self.session.get(Device, device_id) is None:
            raise NotFoundError("Device not found")
        return await self._upload(
            problem_id=None,
            device_id=device_id,
            filename=filename,
            content_type=content_type,
            content=content,
            actor_id=actor_id,
        )

    async def list_for_problem(self, problem_id: uuid.UUID) -> list[Attachment]:
        return await self.repo.list_for_problem(problem_id)

    async def list_for_device(self, device_id: uuid.UUID) -> list[Attachment]:
        return await self.repo.list_for_device(device_id)

    async def get(self, attachment_id: uuid.UUID) -> Attachment:
        attachment = await self.repo.get(attachment_id)
        if attachment is None:
            raise NotFoundError("Attachment not found")
        return attachment

    async def prepare_download(
        self, attachment_id: uuid.UUID, actor_id: uuid.UUID | None
    ) -> Attachment:
        """Authorize + AV-gate, returning the row to stream from disk."""
        attachment = await self.get(attachment_id)
        if attachment.av_status == "infected":
            raise ConflictError("File failed antivirus scan")
        if settings.attachment_require_clean and attachment.av_status != "clean":
            raise ConflictError("File is pending antivirus scan; try again shortly")
        if not storage.exists(attachment.storage_key):
            raise NotFoundError("Stored file is missing")
        self.audit.record(
            action="attachment.download",
            actor_id=actor_id,
            entity_type="attachments",
            entity_id=attachment.id,
        )
        await self.session.commit()
        return attachment

    async def delete(
        self, attachment_id: uuid.UUID, actor_id: uuid.UUID | None
    ) -> None:
        attachment = await self.get(attachment_id)
        storage.delete(attachment.storage_key)
        self.audit.record(
            action="attachment.delete",
            actor_id=actor_id,
            entity_type="attachments",
            entity_id=attachment.id,
        )
        await self.repo.delete(attachment)
        await self.session.commit()
