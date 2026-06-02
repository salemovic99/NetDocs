"""Generic managed-lookup service for device types, vendors, racks, tags, categories.

Lookups are small admin-managed reference tables; this service gives them uniform
CRUD + audit while keeping the data access in their repositories.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import PageParams
from app.models.base import Base
from app.repositories.base import BaseRepository
from app.repositories.device import (
    DeviceTypeRepository,
    RackRepository,
    VendorRepository,
)
from app.repositories.problem import CategoryRepository, TagRepository
from app.services.audit_service import AuditService


class LookupService:
    def __init__(
        self,
        session: AsyncSession,
        repo: BaseRepository,
        *,
        entity_type: str,
        unique_field: str | None = "name",
    ):
        self.session = session
        self.repo = repo
        self.entity_type = entity_type
        self.unique_field = unique_field
        self.audit = AuditService(session)

    async def list(self, params: PageParams) -> tuple[list[Base], int]:
        return await self.repo.list(params)

    async def get(self, entity_id: uuid.UUID) -> Base:
        entity = await self.repo.get(entity_id)
        if entity is None:
            raise NotFoundError(f"{self.entity_type} not found")
        return entity

    async def create(self, data: dict, actor_id: uuid.UUID | None) -> Base:
        if self.unique_field and self.unique_field in data:
            existing = await self.repo.get_by(
                **{self.unique_field: data[self.unique_field]}
            )
            if existing:
                raise ConflictError(f"{self.entity_type} already exists")
        entity = self.repo.model(**data)
        if hasattr(entity, "created_by"):
            entity.created_by = actor_id
            entity.updated_by = actor_id
        self.repo.add(entity)
        await self.repo.flush()
        self.audit.record(
            action=f"{self.entity_type}.create",
            actor_id=actor_id,
            entity_type=self.entity_type,
            entity_id=entity.id,
            diff={k: str(v) for k, v in data.items()},
        )
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(
        self, entity_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> Base:
        entity = await self.get(entity_id)
        if (
            self.unique_field
            and self.unique_field in changes
            and changes[self.unique_field] != getattr(entity, self.unique_field)
        ):
            existing = await self.repo.get_by(
                **{self.unique_field: changes[self.unique_field]}
            )
            if existing:
                raise ConflictError(f"{self.entity_type} already exists")
        for field, value in changes.items():
            setattr(entity, field, value)
        if hasattr(entity, "updated_by"):
            entity.updated_by = actor_id
        self.audit.record(
            action=f"{self.entity_type}.update",
            actor_id=actor_id,
            entity_type=self.entity_type,
            entity_id=entity.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        entity = await self.get(entity_id)
        self.audit.record(
            action=f"{self.entity_type}.delete",
            actor_id=actor_id,
            entity_type=self.entity_type,
            entity_id=entity.id,
        )
        await self.repo.delete(entity)
        await self.session.commit()


# --- factory helpers wiring each lookup to its repository ---
def device_type_service(session: AsyncSession) -> LookupService:
    return LookupService(
        session, DeviceTypeRepository(session), entity_type="device_types"
    )


def vendor_service(session: AsyncSession) -> LookupService:
    return LookupService(session, VendorRepository(session), entity_type="vendors")


def rack_service(session: AsyncSession) -> LookupService:
    return LookupService(
        session, RackRepository(session), entity_type="racks", unique_field=None
    )


def tag_service(session: AsyncSession) -> LookupService:
    return LookupService(session, TagRepository(session), entity_type="tags")


def category_service(session: AsyncSession) -> LookupService:
    return LookupService(
        session, CategoryRepository(session), entity_type="problems_categories"
    )
