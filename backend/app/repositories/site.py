"""Site / room and ISP / wireless repositories."""

import uuid

from sqlalchemy import Select, select

from app.core.pagination import PageParams
from app.models.device import Device
from app.models.inventory import Rack
from app.models.network import IspLink, WirelessNetwork
from app.models.site import Room, Site
from app.repositories.base import BaseRepository


class SiteRepository(BaseRepository[Site]):
    model = Site
    sortable = {"name": "name", "created_at": "created_at", "city": "city"}
    default_order_by = "name"

    async def list_sites(
        self, params: PageParams, *, q: str | None = None
    ) -> tuple[list[Site], int]:
        stmt: Select = select(Site)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(Site.name.ilike(like) | Site.city.ilike(like))
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort).offset(params.offset).limit(
            params.limit
        )
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total

    # --- aggregation for site detail (FR-35) ---
    async def rooms(self, site_id: uuid.UUID) -> list[Room]:
        return list(
            (
                await self.session.execute(
                    select(Room).where(Room.site_id == site_id).order_by(Room.name)
                )
            ).scalars()
        )

    async def devices(self, site_id: uuid.UUID) -> list[Device]:
        return list(
            (
                await self.session.execute(
                    select(Device).where(Device.site_id == site_id)
                )
            ).unique().scalars()
        )

    async def racks(self, site_id: uuid.UUID) -> list[Rack]:
        return list(
            (
                await self.session.execute(
                    select(Rack).where(Rack.site_id == site_id)
                )
            ).scalars()
        )

    async def isp_links(self, site_id: uuid.UUID) -> list[IspLink]:
        return list(
            (
                await self.session.execute(
                    select(IspLink).where(IspLink.site_id == site_id)
                )
            ).scalars()
        )

    async def wireless(self, site_id: uuid.UUID) -> list[WirelessNetwork]:
        return list(
            (
                await self.session.execute(
                    select(WirelessNetwork).where(WirelessNetwork.site_id == site_id)
                )
            ).scalars()
        )


class RoomRepository(BaseRepository[Room]):
    model = Room
    sortable = {"name": "name"}
    default_order_by = "name"


class IspLinkRepository(BaseRepository[IspLink]):
    model = IspLink
    sortable = {"created_at": "created_at", "provider_name": "provider_name"}

    async def list_links(
        self,
        params: PageParams,
        *,
        site_id: uuid.UUID | None = None,
        provider: str | None = None,
        status: str | None = None,
        connection_type: str | None = None,
    ) -> tuple[list[IspLink], int]:
        stmt: Select = select(IspLink)
        if site_id is not None:
            stmt = stmt.where(IspLink.site_id == site_id)
        if provider is not None:
            stmt = stmt.where(IspLink.provider_name.ilike(f"%{provider}%"))
        if status is not None:
            stmt = stmt.where(IspLink.status == status)
        if connection_type is not None:
            stmt = stmt.where(IspLink.connection_type == connection_type)
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort).offset(params.offset).limit(
            params.limit
        )
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total


class WirelessRepository(BaseRepository[WirelessNetwork]):
    model = WirelessNetwork
    sortable = {"created_at": "created_at", "ssid": "ssid"}
    default_order_by = "ssid"

    async def list_networks(
        self,
        params: PageParams,
        *,
        site_id: uuid.UUID | None = None,
        security_type: str | None = None,
        vlan_tag: int | None = None,
    ) -> tuple[list[WirelessNetwork], int]:
        stmt: Select = select(WirelessNetwork)
        if site_id is not None:
            stmt = stmt.where(WirelessNetwork.site_id == site_id)
        if security_type is not None:
            stmt = stmt.where(WirelessNetwork.security_type == security_type)
        if vlan_tag is not None:
            stmt = stmt.where(WirelessNetwork.vlan_tag == vlan_tag)
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort).offset(params.offset).limit(
            params.limit
        )
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total
