"""Attachment repository."""

import uuid

from sqlalchemy import select

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    model = Attachment
    sortable = {"created_at": "created_at", "filename": "filename"}

    async def list_for_problem(self, problem_id: uuid.UUID) -> list[Attachment]:
        stmt = (
            select(Attachment)
            .where(Attachment.problem_id == problem_id)
            .order_by(Attachment.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_for_device(self, device_id: uuid.UUID) -> list[Attachment]:
        stmt = (
            select(Attachment)
            .where(Attachment.device_id == device_id)
            .order_by(Attachment.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def all_storage_keys(self) -> set[str]:
        stmt = select(Attachment.storage_key)
        return set((await self.session.execute(stmt)).scalars().all())
