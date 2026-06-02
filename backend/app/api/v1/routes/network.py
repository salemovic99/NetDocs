"""ISP/WAN link and wireless-network endpoints (PRD §10 /isp-links, /wireless-networks)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core import permissions as perms
from app.core.deps import CurrentUser, DbSession, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.network import (
    IspLinkCreate,
    IspLinkRead,
    IspLinkUpdate,
    WirelessCreate,
    WirelessRead,
    WirelessUpdate,
)
from app.services.network_service import IspLinkService, WirelessService

router = APIRouter(tags=["network"])


# --- ISP / WAN links ---
@router.get(
    "/isp-links",
    response_model=Page[IspLinkRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_isp_links(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    site: uuid.UUID | None = None,
    provider: str | None = None,
    status: str | None = None,
    type: str | None = Query(None),
) -> Page[IspLinkRead]:
    items, total = await IspLinkService(session).list(
        params, site_id=site, provider=provider, status=status, connection_type=type
    )
    return Page.create([IspLinkRead.model_validate(i) for i in items], total, params)


@router.post(
    "/isp-links",
    response_model=IspLinkRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_isp_link(
    payload: IspLinkCreate, session: DbSession, user: CurrentUser
) -> IspLinkRead:
    link = await IspLinkService(session).create(payload.model_dump(), actor_id=user.id)
    return IspLinkRead.model_validate(link)


@router.patch(
    "/isp-links/{link_id}",
    response_model=IspLinkRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_isp_link(
    link_id: uuid.UUID, payload: IspLinkUpdate, session: DbSession, user: CurrentUser
) -> IspLinkRead:
    link = await IspLinkService(session).update(
        link_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return IspLinkRead.model_validate(link)


@router.delete(
    "/isp-links/{link_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_isp_link(
    link_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await IspLinkService(session).delete(link_id, actor_id=user.id)


# --- Wireless networks ---
@router.get(
    "/wireless-networks",
    response_model=Page[WirelessRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_wireless(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    site: uuid.UUID | None = None,
    security: str | None = Query(None, alias="security"),
    vlan: int | None = None,
) -> Page[WirelessRead]:
    items, total = await WirelessService(session).list(
        params, site_id=site, security_type=security, vlan_tag=vlan
    )
    return Page.create([WirelessRead.model_validate(w) for w in items], total, params)


@router.post(
    "/wireless-networks",
    response_model=WirelessRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_wireless(
    payload: WirelessCreate, session: DbSession, user: CurrentUser
) -> WirelessRead:
    net = await WirelessService(session).create(payload.model_dump(), actor_id=user.id)
    return WirelessRead.model_validate(net)


@router.patch(
    "/wireless-networks/{net_id}",
    response_model=WirelessRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_wireless(
    net_id: uuid.UUID, payload: WirelessUpdate, session: DbSession, user: CurrentUser
) -> WirelessRead:
    net = await WirelessService(session).update(
        net_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return WirelessRead.model_validate(net)


@router.delete(
    "/wireless-networks/{net_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_wireless(
    net_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await WirelessService(session).delete(net_id, actor_id=user.id)
