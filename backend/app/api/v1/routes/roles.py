"""Role & permission management endpoints (PRD §10 /roles, /permissions)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import permissions as perms
from app.core.deps import CurrentUser, DbSession, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.user import (
    PermissionRead,
    RoleCreate,
    RolePermissionsUpdate,
    RoleRead,
    RoleUpdate,
)
from app.services.user_service import RoleService

router = APIRouter(tags=["roles"])


@router.get(
    "/roles",
    response_model=Page[RoleRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_roles(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[RoleRead]:
    items, total = await RoleService(session).list_roles(params)
    return Page.create([RoleRead.model_validate(r) for r in items], total, params)


@router.post(
    "/roles",
    response_model=RoleRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.ROLES_MANAGE))],
)
async def create_role(
    payload: RoleCreate, session: DbSession, actor: CurrentUser
) -> RoleRead:
    role = await RoleService(session).create(
        name=payload.name, description=payload.description, actor_id=actor.id
    )
    return RoleRead.model_validate(role)


@router.patch(
    "/roles/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_permission(perms.ROLES_MANAGE))],
)
async def update_role(
    role_id: uuid.UUID, payload: RoleUpdate, session: DbSession, actor: CurrentUser
) -> RoleRead:
    role = await RoleService(session).update(
        role_id, payload.model_dump(exclude_unset=True), actor_id=actor.id
    )
    return RoleRead.model_validate(role)


@router.delete(
    "/roles/{role_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.ROLES_MANAGE))],
)
async def delete_role(
    role_id: uuid.UUID, session: DbSession, actor: CurrentUser
) -> None:
    await RoleService(session).delete(role_id, actor_id=actor.id)


@router.put(
    "/roles/{role_id}/permissions",
    response_model=RoleRead,
    dependencies=[Depends(require_permission(perms.ROLES_MANAGE))],
)
async def set_role_permissions(
    role_id: uuid.UUID,
    payload: RolePermissionsUpdate,
    session: DbSession,
    actor: CurrentUser,
) -> RoleRead:
    role = await RoleService(session).set_permissions(
        role_id, payload.permission_codes, actor_id=actor.id
    )
    return RoleRead.model_validate(role)


@router.get(
    "/permissions",
    response_model=Page[PermissionRead],
    dependencies=[Depends(require_permission(perms.INVENTORY_READ))],
)
async def list_permissions(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[PermissionRead]:
    items, total = await RoleService(session).list_permissions(params)
    return Page.create([PermissionRead.model_validate(p) for p in items], total, params)
