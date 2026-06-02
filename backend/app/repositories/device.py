"""Device / VLAN and inventory-lookup repositories."""

import uuid

from sqlalchemy import Select, or_, select

from app.core.pagination import PageParams
from app.models.device import Device, Vlan
from app.models.inventory import DeviceType, Rack, Vendor
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    model = Device
    sortable = {"created_at": "created_at", "hostname": "hostname", "status": "status"}

    async def list_devices(
        self,
        params: PageParams,
        *,
        q: str | None = None,
        device_type_id: uuid.UUID | None = None,
        vendor_id: uuid.UUID | None = None,
        site_id: uuid.UUID | None = None,
        rack_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> tuple[list[Device], int]:
        stmt: Select = select(Device)
        if device_type_id is not None:
            stmt = stmt.where(Device.device_type_id == device_type_id)
        if vendor_id is not None:
            stmt = stmt.where(Device.vendor_id == vendor_id)
        if site_id is not None:
            stmt = stmt.where(Device.site_id == site_id)
        if rack_id is not None:
            stmt = stmt.where(Device.rack_id == rack_id)
        if status is not None:
            stmt = stmt.where(Device.status == status)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Device.hostname.ilike(like),
                    Device.serial_number.ilike(like),
                    Device.asset_tag.ilike(like),
                    Device.management_ip.op("::text").ilike(like),
                )
            )
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort).offset(params.offset).limit(
            params.limit
        )
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total

    async def get_by_hostname(self, hostname: str) -> Device | None:
        return await self.get_by(hostname=hostname)


class VlanRepository(BaseRepository[Vlan]):
    model = Vlan
    sortable = {"vlan_id": "vlan_id"}
    default_order_by = "vlan_id"

    async def list_for_device(self, device_id: uuid.UUID) -> list[Vlan]:
        stmt = (
            select(Vlan)
            .where(Vlan.device_id == device_id)
            .order_by(Vlan.vlan_id.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_by_device_and_tag(
        self, device_id: uuid.UUID, vlan_id: int
    ) -> Vlan | None:
        return await self.get_by(device_id=device_id, vlan_id=vlan_id)


class DeviceTypeRepository(BaseRepository[DeviceType]):
    model = DeviceType
    sortable = {"name": "name"}
    default_order_by = "name"

    async def get_by_name(self, name: str) -> DeviceType | None:
        return await self.get_by(name=name)


class VendorRepository(BaseRepository[Vendor]):
    model = Vendor
    sortable = {"name": "name"}
    default_order_by = "name"

    async def get_by_name(self, name: str) -> Vendor | None:
        return await self.get_by(name=name)


class RackRepository(BaseRepository[Rack]):
    model = Rack
    sortable = {"name": "name", "created_at": "created_at"}
    default_order_by = "name"
