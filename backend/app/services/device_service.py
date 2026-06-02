"""Device and VLAN services (PRD §6.2, FR-5..FR-11)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import PageParams
from app.models.device import Device, Vlan
from app.repositories.device import DeviceRepository, VlanRepository
from app.schemas.device import DeviceCreate, DeviceUpdate, VlanCreate, VlanUpdate
from app.services.audit_service import AuditService


class DeviceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DeviceRepository(session)
        self.audit = AuditService(session)

    async def list(self, params: PageParams, **filters) -> tuple[list[Device], int]:
        return await self.repo.list_devices(params, **filters)

    async def get(self, device_id: uuid.UUID) -> Device:
        device = await self.repo.get(device_id)
        if device is None:
            raise NotFoundError("Device not found")
        return device

    async def create(
        self, payload: DeviceCreate, actor_id: uuid.UUID | None
    ) -> Device:
        if await self.repo.get_by_hostname(payload.hostname):
            raise ConflictError("Hostname already exists")
        device = Device(
            **payload.model_dump(), created_by=actor_id, updated_by=actor_id
        )
        self.repo.add(device)
        await self.repo.flush()
        self.audit.record(
            action="device.create",
            actor_id=actor_id,
            entity_type="devices",
            entity_id=device.id,
            diff={"hostname": payload.hostname},
        )
        await self.session.commit()
        return await self.get(device.id)

    async def update(
        self, device_id: uuid.UUID, payload: DeviceUpdate, actor_id: uuid.UUID | None
    ) -> Device:
        device = await self.get(device_id)
        changes = payload.model_dump(exclude_unset=True)
        if "hostname" in changes and changes["hostname"] != device.hostname:
            if await self.repo.get_by_hostname(changes["hostname"]):
                raise ConflictError("Hostname already exists")
        for field, value in changes.items():
            setattr(device, field, value)
        device.updated_by = actor_id
        self.audit.record(
            action="device.update",
            actor_id=actor_id,
            entity_type="devices",
            entity_id=device.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return await self.get(device.id)

    async def delete(self, device_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        device = await self.get(device_id)
        self.audit.record(
            action="device.delete",
            actor_id=actor_id,
            entity_type="devices",
            entity_id=device.id,
        )
        await self.repo.delete(device)
        await self.session.commit()


class VlanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = VlanRepository(session)
        self.devices = DeviceRepository(session)
        self.audit = AuditService(session)

    async def list_for_device(self, device_id: uuid.UUID) -> list[Vlan]:
        if await self.devices.get(device_id) is None:
            raise NotFoundError("Device not found")
        return await self.repo.list_for_device(device_id)

    async def get(self, vlan_id: uuid.UUID) -> Vlan:
        vlan = await self.repo.get(vlan_id)
        if vlan is None:
            raise NotFoundError("VLAN not found")
        return vlan

    async def add(
        self, device_id: uuid.UUID, payload: VlanCreate, actor_id: uuid.UUID | None
    ) -> Vlan:
        if await self.devices.get(device_id) is None:
            raise NotFoundError("Device not found")
        if await self.repo.get_by_device_and_tag(device_id, payload.vlan_id):
            raise ConflictError("VLAN tag already exists on this device")
        vlan = Vlan(
            device_id=device_id,
            **payload.model_dump(),
            created_by=actor_id,
            updated_by=actor_id,
        )
        self.repo.add(vlan)
        await self.repo.flush()
        self.audit.record(
            action="vlan.create",
            actor_id=actor_id,
            entity_type="vlans",
            entity_id=vlan.id,
            diff={"device_id": str(device_id), "vlan_id": payload.vlan_id},
        )
        await self.session.commit()
        return await self.get(vlan.id)

    async def update(
        self, vlan_id: uuid.UUID, payload: VlanUpdate, actor_id: uuid.UUID | None
    ) -> Vlan:
        vlan = await self.get(vlan_id)
        changes = payload.model_dump(exclude_unset=True)
        if "vlan_id" in changes and changes["vlan_id"] != vlan.vlan_id:
            existing = await self.repo.get_by_device_and_tag(
                vlan.device_id, changes["vlan_id"]
            )
            if existing:
                raise ConflictError("VLAN tag already exists on this device")
        for field, value in changes.items():
            setattr(vlan, field, value)
        vlan.updated_by = actor_id
        self.audit.record(
            action="vlan.update",
            actor_id=actor_id,
            entity_type="vlans",
            entity_id=vlan.id,
            diff={k: str(v) for k, v in changes.items()},
        )
        await self.session.commit()
        return await self.get(vlan.id)

    async def delete(self, vlan_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        vlan = await self.get(vlan_id)
        self.audit.record(
            action="vlan.delete",
            actor_id=actor_id,
            entity_type="vlans",
            entity_id=vlan.id,
        )
        await self.repo.delete(vlan)
        await self.session.commit()
