"""Site and room services + site-detail aggregate (PRD §6.9, FR-32..FR-35)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PageParams
from app.models.site import Room, Site
from app.repositories.site import RoomRepository, SiteRepository
from app.schemas.site import SiteCreate, SiteUpdate
from app.services.audit_service import AuditService


class SiteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SiteRepository(session)
        self.rooms = RoomRepository(session)
        self.audit = AuditService(session)

    async def list(self, params: PageParams, *, q: str | None = None):
        return await self.repo.list_sites(params, q=q)

    async def get(self, site_id: uuid.UUID) -> Site:
        site = await self.repo.get(site_id)
        if site is None:
            raise NotFoundError("Site not found")
        return site

    async def get_detail(self, site_id: uuid.UUID) -> dict:
        site = await self.get(site_id)
        return {
            "site": site,
            "rooms": await self.repo.rooms(site_id),
            "devices": await self.repo.devices(site_id),
            "racks": await self.repo.racks(site_id),
            "isp_links": await self.repo.isp_links(site_id),
            "wireless_networks": await self.repo.wireless(site_id),
        }

    async def create(self, payload: SiteCreate, actor_id: uuid.UUID | None) -> Site:
        site = Site(**payload.model_dump(), created_by=actor_id, updated_by=actor_id)
        self.repo.add(site)
        await self.repo.flush()
        self.audit.record(
            action="site.create",
            actor_id=actor_id,
            entity_type="sites",
            entity_id=site.id,
            diff={"name": payload.name},
        )
        await self.session.commit()
        return await self.get(site.id)

    async def update(
        self, site_id: uuid.UUID, payload: SiteUpdate, actor_id: uuid.UUID | None
    ) -> Site:
        site = await self.get(site_id)
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(site, field, value)
        site.updated_by = actor_id
        self.audit.record(
            action="site.update",
            actor_id=actor_id,
            entity_type="sites",
            entity_id=site.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return await self.get(site.id)

    async def delete(self, site_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        site = await self.get(site_id)
        self.audit.record(
            action="site.delete",
            actor_id=actor_id,
            entity_type="sites",
            entity_id=site.id,
        )
        await self.repo.delete(site)
        await self.session.commit()

    # --- Rooms ---
    async def list_rooms(self, site_id: uuid.UUID) -> list[Room]:
        await self.get(site_id)
        return await self.repo.rooms(site_id)

    async def add_room(
        self, site_id: uuid.UUID, data: dict, actor_id: uuid.UUID | None
    ) -> Room:
        await self.get(site_id)
        room = Room(site_id=site_id, **data)
        self.rooms.add(room)
        await self.rooms.flush()
        self.audit.record(
            action="room.create",
            actor_id=actor_id,
            entity_type="rooms",
            entity_id=room.id,
            diff={"site_id": str(site_id), **{k: str(v) for k, v in data.items()}},
        )
        await self.session.commit()
        return room

    async def update_room(
        self, room_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> Room:
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        for field, value in changes.items():
            setattr(room, field, value)
        self.audit.record(
            action="room.update",
            actor_id=actor_id,
            entity_type="rooms",
            entity_id=room.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return room

    async def delete_room(self, room_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        self.audit.record(
            action="room.delete",
            actor_id=actor_id,
            entity_type="rooms",
            entity_id=room.id,
        )
        await self.rooms.delete(room)
        await self.session.commit()
