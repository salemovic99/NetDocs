"""User management endpoints (PRD §10 /users)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import permissions as perms
from app.core.deps import CurrentUser, DbSession, RedisClient, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.user import (
    PasswordResetResult,
    UserCreate,
    UserRead,
    UserRolesUpdate,
    UserUpdate,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_permission(perms.USERS_MANAGE))],
)


@router.get("", response_model=Page[UserRead])
async def list_users(
    session: DbSession, params: Annotated[PageParams, Depends(page_params)]
) -> Page[UserRead]:
    items, total = await UserService(session).list_users(params)
    return Page.create([UserRead.model_validate(u) for u in items], total, params)


@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    payload: UserCreate, session: DbSession, actor: CurrentUser
) -> UserRead:
    user = await UserService(session).create(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
        role_names=payload.role_names,
        must_change_password=payload.must_change_password,
        actor_id=actor.id,
    )
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, session: DbSession) -> UserRead:
    return UserRead.model_validate(await UserService(session).get(user_id))


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID, payload: UserUpdate, session: DbSession, actor: CurrentUser
) -> UserRead:
    user = await UserService(session).update(
        user_id, payload.model_dump(exclude_unset=True), actor_id=actor.id
    )
    return UserRead.model_validate(user)


@router.put("/{user_id}/roles", response_model=UserRead)
async def set_user_roles(
    user_id: uuid.UUID,
    payload: UserRolesUpdate,
    session: DbSession,
    actor: CurrentUser,
) -> UserRead:
    user = await UserService(session).set_roles(
        user_id, payload.role_names, actor_id=actor.id
    )
    return UserRead.model_validate(user)


@router.post("/{user_id}/unlock", response_model=UserRead)
async def unlock_user(
    user_id: uuid.UUID, session: DbSession, actor: CurrentUser
) -> UserRead:
    user = await UserService(session).unlock(user_id, actor_id=actor.id)
    return UserRead.model_validate(user)


@router.post("/{user_id}/reset-password", response_model=PasswordResetResult)
async def reset_user_password(
    user_id: uuid.UUID, session: DbSession, redis: RedisClient, actor: CurrentUser
) -> PasswordResetResult:
    user, temp_password = await UserService(session).reset_password(
        user_id, actor_id=actor.id
    )
    # Invalidate the target user's existing sessions after a reset.
    await AuthService(session, redis).revoke_all_sessions(user.id)
    return PasswordResetResult(user_id=user.id, temporary_password=temp_password)


@router.delete("/{user_id}/sessions", status_code=204)
async def revoke_user_sessions(
    user_id: uuid.UUID, session: DbSession, redis: RedisClient, actor: CurrentUser
) -> None:
    await AuthService(session, redis).revoke_all_sessions(user_id)
