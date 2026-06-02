"""ISP/WAN link and wireless-network services (PRD §6.7, §6.8)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PageParams
from app.models.network import IspLink, WirelessNetwork
from app.repositories.site import (
    IspLinkRepository,
    SiteRepository,
    WirelessRepository,
)
from app.services.audit_service import AuditService


class IspLinkService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = IspLinkRepository(session)
        self.sites = SiteRepository(session)
        self.audit = AuditService(session)

    async def list(self, params: PageParams, **filters):
        return await self.repo.list_links(params, **filters)

    async def get(self, link_id: uuid.UUID) -> IspLink:
        link = await self.repo.get(link_id)
        if link is None:
            raise NotFoundError("ISP link not found")
        return link

    async def create(self, data: dict, actor_id: uuid.UUID | None) -> IspLink:
        if await self.sites.get(data["site_id"]) is None:
            raise NotFoundError("Site not found")
        link = IspLink(**data, created_by=actor_id, updated_by=actor_id)
        self.repo.add(link)
        await self.repo.flush()
        self.audit.record(
            action="isp_link.create",
            actor_id=actor_id,
            entity_type="isp_links",
            entity_id=link.id,
            diff={"site_id": str(data["site_id"])},
        )
        await self.session.commit()
        return await self.get(link.id)

    async def update(
        self, link_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> IspLink:
        link = await self.get(link_id)
        for field, value in changes.items():
            setattr(link, field, value)
        link.updated_by = actor_id
        self.audit.record(
            action="isp_link.update",
            actor_id=actor_id,
            entity_type="isp_links",
            entity_id=link.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return await self.get(link.id)

    async def delete(self, link_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        link = await self.get(link_id)
        self.audit.record(
            action="isp_link.delete",
            actor_id=actor_id,
            entity_type="isp_links",
            entity_id=link.id,
        )
        await self.repo.delete(link)
        await self.session.commit()


class WirelessService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WirelessRepository(session)
        self.sites = SiteRepository(session)
        self.audit = AuditService(session)

    async def list(self, params: PageParams, **filters):
        return await self.repo.list_networks(params, **filters)

    async def get(self, net_id: uuid.UUID) -> WirelessNetwork:
        net = await self.repo.get(net_id)
        if net is None:
            raise NotFoundError("Wireless network not found")
        return net

    async def create(self, data: dict, actor_id: uuid.UUID | None) -> WirelessNetwork:
        if await self.sites.get(data["site_id"]) is None:
            raise NotFoundError("Site not found")
        net = WirelessNetwork(**data, created_by=actor_id, updated_by=actor_id)
        self.repo.add(net)
        await self.repo.flush()
        self.audit.record(
            action="wireless.create",
            actor_id=actor_id,
            entity_type="wireless_networks",
            entity_id=net.id,
            diff={"ssid": data.get("ssid")},
        )
        await self.session.commit()
        return await self.get(net.id)

    async def update(
        self, net_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> WirelessNetwork:
        net = await self.get(net_id)
        for field, value in changes.items():
            setattr(net, field, value)
        net.updated_by = actor_id
        self.audit.record(
            action="wireless.update",
            actor_id=actor_id,
            entity_type="wireless_networks",
            entity_id=net.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return await self.get(net.id)

    async def delete(self, net_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        net = await self.get(net_id)
        self.audit.record(
            action="wireless.delete",
            actor_id=actor_id,
            entity_type="wireless_networks",
            entity_id=net.id,
        )
        await self.repo.delete(net)
        await self.session.commit()
