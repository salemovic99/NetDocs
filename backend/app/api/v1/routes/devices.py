"""Device + VLAN endpoints (PRD §10 /devices, /vlans)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.core import permissions as perms
from app.core.concurrency import check_etag, make_etag
from app.core.deps import CurrentUser, DbSession, if_match_header, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.device import (
    DeviceCreate,
    DeviceRead,
    DeviceUpdate,
    VlanCreate,
    VlanRead,
    VlanUpdate,
)
from app.services.device_service import DeviceService, VlanService

router = APIRouter(tags=["devices"])


# --- Devices ---
@router.get(
    "/devices",
    response_model=Page[DeviceRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_devices(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    q: str | None = None,
    device_type: uuid.UUID | None = None,
    vendor: uuid.UUID | None = None,
    site: uuid.UUID | None = None,
    rack: uuid.UUID | None = None,
    status: str | None = None,
) -> Page[DeviceRead]:
    items, total = await DeviceService(session).list(
        params,
        q=q,
        device_type_id=device_type,
        vendor_id=vendor,
        site_id=site,
        rack_id=rack,
        status=status,
    )
    return Page.create([DeviceRead.model_validate(d) for d in items], total, params)


@router.post(
    "/devices",
    response_model=DeviceRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_device(
    payload: DeviceCreate, session: DbSession, user: CurrentUser
) -> DeviceRead:
    device = await DeviceService(session).create(payload, actor_id=user.id)
    return DeviceRead.model_validate(device)


@router.get(
    "/devices/{device_id}",
    response_model=DeviceRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def get_device(
    device_id: uuid.UUID, session: DbSession, response: Response
) -> DeviceRead:
    device = await DeviceService(session).get(device_id)
    response.headers["ETag"] = make_etag(device.updated_at)
    return DeviceRead.model_validate(device)


@router.patch(
    "/devices/{device_id}",
    response_model=DeviceRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_device(
    device_id: uuid.UUID,
    payload: DeviceUpdate,
    session: DbSession,
    user: CurrentUser,
    response: Response,
    if_match: Annotated[str | None, Depends(if_match_header)] = None,
) -> DeviceRead:
    service = DeviceService(session)
    current = await service.get(device_id)
    check_etag(current.updated_at, if_match)
    device = await service.update(device_id, payload, actor_id=user.id)
    response.headers["ETag"] = make_etag(device.updated_at)
    return DeviceRead.model_validate(device)


@router.delete(
    "/devices/{device_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_device(
    device_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await DeviceService(session).delete(device_id, actor_id=user.id)


# --- VLANs (per switch) ---
@router.get(
    "/devices/{device_id}/vlans",
    response_model=list[VlanRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_vlans(device_id: uuid.UUID, session: DbSession) -> list[VlanRead]:
    vlans = await VlanService(session).list_for_device(device_id)
    return [VlanRead.model_validate(v) for v in vlans]


@router.post(
    "/devices/{device_id}/vlans",
    response_model=VlanRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def add_vlan(
    device_id: uuid.UUID,
    payload: VlanCreate,
    session: DbSession,
    user: CurrentUser,
) -> VlanRead:
    vlan = await VlanService(session).add(device_id, payload, actor_id=user.id)
    return VlanRead.model_validate(vlan)


@router.patch(
    "/vlans/{vlan_id}",
    response_model=VlanRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_vlan(
    vlan_id: uuid.UUID,
    payload: VlanUpdate,
    session: DbSession,
    user: CurrentUser,
) -> VlanRead:
    vlan = await VlanService(session).update(vlan_id, payload, actor_id=user.id)
    return VlanRead.model_validate(vlan)


@router.delete(
    "/vlans/{vlan_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_vlan(
    vlan_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await VlanService(session).delete(vlan_id, actor_id=user.id)
