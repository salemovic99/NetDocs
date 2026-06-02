"""Managed-lookup endpoints: device types, vendors, racks, tags, problem categories."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import permissions as perms
from app.core.deps import CurrentUser, DbSession, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.lookups import (
    CategoryCreate,
    CategoryRead,
    DeviceTypeCreate,
    DeviceTypeRead,
    RackCreate,
    RackRead,
    RackUpdate,
    TagCreate,
    TagRead,
    VendorCreate,
    VendorRead,
    VendorUpdate,
)
from app.services import lookup_service

router = APIRouter(tags=["lookups"])


# --- Device types ---
@router.get(
    "/device-types",
    response_model=Page[DeviceTypeRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_device_types(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[DeviceTypeRead]:
    items, total = await lookup_service.device_type_service(session).list(params)
    return Page.create([DeviceTypeRead.model_validate(i) for i in items], total, params)


@router.post(
    "/device-types",
    response_model=DeviceTypeRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_device_type(
    payload: DeviceTypeCreate, session: DbSession, user: CurrentUser
) -> DeviceTypeRead:
    entity = await lookup_service.device_type_service(session).create(
        payload.model_dump(), actor_id=user.id
    )
    return DeviceTypeRead.model_validate(entity)


@router.patch(
    "/device-types/{type_id}",
    response_model=DeviceTypeRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_device_type(
    type_id: uuid.UUID, payload: DeviceTypeCreate, session: DbSession, user: CurrentUser
) -> DeviceTypeRead:
    entity = await lookup_service.device_type_service(session).update(
        type_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return DeviceTypeRead.model_validate(entity)


@router.delete(
    "/device-types/{type_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_device_type(
    type_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await lookup_service.device_type_service(session).delete(type_id, actor_id=user.id)


# --- Vendors ---
@router.get(
    "/vendors",
    response_model=Page[VendorRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_vendors(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[VendorRead]:
    items, total = await lookup_service.vendor_service(session).list(params)
    return Page.create([VendorRead.model_validate(i) for i in items], total, params)


@router.post(
    "/vendors",
    response_model=VendorRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_vendor(
    payload: VendorCreate, session: DbSession, user: CurrentUser
) -> VendorRead:
    entity = await lookup_service.vendor_service(session).create(
        payload.model_dump(), actor_id=user.id
    )
    return VendorRead.model_validate(entity)


@router.patch(
    "/vendors/{vendor_id}",
    response_model=VendorRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_vendor(
    vendor_id: uuid.UUID, payload: VendorUpdate, session: DbSession, user: CurrentUser
) -> VendorRead:
    entity = await lookup_service.vendor_service(session).update(
        vendor_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return VendorRead.model_validate(entity)


@router.delete(
    "/vendors/{vendor_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_vendor(
    vendor_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await lookup_service.vendor_service(session).delete(vendor_id, actor_id=user.id)


# --- Racks ---
@router.get(
    "/racks",
    response_model=Page[RackRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_racks(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[RackRead]:
    items, total = await lookup_service.rack_service(session).list(params)
    return Page.create([RackRead.model_validate(i) for i in items], total, params)


@router.post(
    "/racks",
    response_model=RackRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def create_rack(
    payload: RackCreate, session: DbSession, user: CurrentUser
) -> RackRead:
    entity = await lookup_service.rack_service(session).create(
        payload.model_dump(), actor_id=user.id
    )
    return RackRead.model_validate(entity)


@router.patch(
    "/racks/{rack_id}",
    response_model=RackRead,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def update_rack(
    rack_id: uuid.UUID, payload: RackUpdate, session: DbSession, user: CurrentUser
) -> RackRead:
    entity = await lookup_service.rack_service(session).update(
        rack_id, payload.model_dump(exclude_unset=True), actor_id=user.id
    )
    return RackRead.model_validate(entity)


@router.delete(
    "/racks/{rack_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.INVENTORY_MANAGE))],
)
async def delete_rack(
    rack_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await lookup_service.rack_service(session).delete(rack_id, actor_id=user.id)


# --- Tags ---
@router.get(
    "/tags",
    response_model=Page[TagRead],
    dependencies=[Depends(require_permission(perms.PROBLEMS_READ))],
)
async def list_tags(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[TagRead]:
    items, total = await lookup_service.tag_service(session).list(params)
    return Page.create([TagRead.model_validate(i) for i in items], total, params)


@router.post(
    "/tags",
    response_model=TagRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.TAGS_MANAGE))],
)
async def create_tag(
    payload: TagCreate, session: DbSession, user: CurrentUser
) -> TagRead:
    entity = await lookup_service.tag_service(session).create(
        payload.model_dump(), actor_id=user.id
    )
    return TagRead.model_validate(entity)


@router.delete(
    "/tags/{tag_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.TAGS_MANAGE))],
)
async def delete_tag(tag_id: uuid.UUID, session: DbSession, user: CurrentUser) -> None:
    await lookup_service.tag_service(session).delete(tag_id, actor_id=user.id)


# --- Problem categories ---
@router.get(
    "/problem-categories",
    response_model=Page[CategoryRead],
    dependencies=[Depends(require_permission(perms.PROBLEMS_READ))],
)
async def list_categories(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[CategoryRead]:
    items, total = await lookup_service.category_service(session).list(params)
    return Page.create([CategoryRead.model_validate(i) for i in items], total, params)


@router.post(
    "/problem-categories",
    response_model=CategoryRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.TAGS_MANAGE))],
)
async def create_category(
    payload: CategoryCreate, session: DbSession, user: CurrentUser
) -> CategoryRead:
    entity = await lookup_service.category_service(session).create(
        payload.model_dump(), actor_id=user.id
    )
    return CategoryRead.model_validate(entity)


@router.delete(
    "/problem-categories/{category_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.TAGS_MANAGE))],
)
async def delete_category(
    category_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await lookup_service.category_service(session).delete(category_id, actor_id=user.id)
