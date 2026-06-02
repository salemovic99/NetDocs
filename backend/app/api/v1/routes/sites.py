"""Site + room endpoints incl. site-detail aggregate (PRD §10 /sites, /rooms)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import permissions as perms
from app.core.deps import CurrentUser, DbSession, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.device import DeviceRead
from app.schemas.lookups import RackRead
from app.schemas.network import IspLinkRead, WirelessRead
from app.schemas.site import (
    RoomCreate,
    RoomRead,
    RoomUpdate,
    SiteCreate,
    SiteDetailRead,
    SiteRead,
    SiteUpdate,
)
from app.services.site_service import SiteService

router = APIRouter(tags=["sites"])

SiteDetailRead.model_rebuild()


@router.get(
    "/sites",
    response_model=Page[SiteRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_sites(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    q: str | None = None,
) -> Page[SiteRead]:
    items, total = await SiteService(session).list(params, q=q)
    return Page.create([SiteRead.model_validate(s) for s in items], total, params)


@router.post(
    "/sites",
    response_model=SiteRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_site(
    payload: SiteCreate, session: DbSession, user: CurrentUser
) -> SiteRead:
    site = await SiteService(session).create(payload, actor_id=user.id)
    return SiteRead.model_validate(site)


@router.get(
    "/sites/{site_id}",
    response_model=SiteDetailRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def get_site(site_id: uuid.UUID, session: DbSession) -> SiteDetailRead:
    data = await SiteService(session).get_detail(site_id)
    detail = SiteDetailRead.model_validate(data["site"])
    detail.rooms = [RoomRead.model_validate(r) for r in data["rooms"]]
    detail.devices = [DeviceRead.model_validate(d) for d in data["devices"]]
    detail.racks = [RackRead.model_validate(r) for r in data["racks"]]
    detail.isp_links = [IspLinkRead.model_validate(i) for i in data["isp_links"]]
    detail.wireless_networks = [
        WirelessRead.model_validate(w) for w in data["wireless_networks"]
    ]
    return detail


@router.patch(
    "/sites/{site_id}",
    response_model=SiteRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_site(
    site_id: uuid.UUID, payload: SiteUpdate, session: DbSession, user: CurrentUser
) -> SiteRead:
    site = await SiteService(session).update(site_id, payload, actor_id=user.id)
    return SiteRead.model_validate(site)


@router.delete(
    "/sites/{site_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_site(
    site_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await SiteService(session).delete(site_id, actor_id=user.id)


# --- Rooms ---
@router.get(
    "/sites/{site_id}/rooms",
    response_model=list[RoomRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_rooms(site_id: uuid.UUID, session: DbSession) -> list[RoomRead]:
    rooms = await SiteService(session).list_rooms(site_id)
    return [RoomRead.model_validate(r) for r in rooms]


@router.post(
    "/sites/{site_id}/rooms",
    response_model=RoomRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def add_room(
    site_id: uuid.UUID, payload: RoomCreate, session: DbSession, user: CurrentUser
) -> RoomRead:
    room = await SiteService(session).add_room(
        site_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return RoomRead.model_validate(room)


@router.patch(
    "/rooms/{room_id}",
    response_model=RoomRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_room(
    room_id: uuid.UUID, payload: RoomUpdate, session: DbSession, user: CurrentUser
) -> RoomRead:
    room = await SiteService(session).update_room(
        room_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return RoomRead.model_validate(room)


@router.delete(
    "/rooms/{room_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_room(
    room_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await SiteService(session).delete_room(room_id, actor_id=user.id)
