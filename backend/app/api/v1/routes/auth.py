"""Auth endpoints (PRD §10 /auth/*)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.core import ratelimit
from app.core.config import settings
from app.core.deps import CurrentUser, DbSession, RedisClient, client_ip
from app.core.exceptions import RateLimitedError
from app.schemas.auth import (
    ChangePasswordRequest,
    EffectivePermissions,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SessionInfo,
    TokenResponse,
    UserProfile,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: DbSession,
    redis: RedisClient,
    ip: Annotated[str | None, Depends(client_ip)],
    user_agent: Annotated[str | None, Header()] = None,
) -> TokenResponse:
    # Per-account login throttle (PRD §7: 10/min/account); per-IP is in middleware.
    if settings.rate_limit_enabled:
        allowed, retry_after = await ratelimit.hit(
            redis,
            f"login:account:{payload.identifier.lower()}",
            settings.rate_limit_login_account,
            settings.rate_limit_window_seconds,
        )
        if not allowed:
            raise RateLimitedError("Too many login attempts", retry_after=retry_after)

    service = AuthService(session, redis)
    access, refresh, user = await service.login(
        payload.identifier, payload.password, ip_address=ip, user_agent=user_agent
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        must_change_password=user.must_change_password,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest, session: DbSession, redis: RedisClient
) -> TokenResponse:
    access, new_refresh = await AuthService(session, redis).refresh(
        payload.refresh_token
    )
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
async def logout(
    payload: LogoutRequest, session: DbSession, redis: RedisClient
) -> None:
    await AuthService(session, redis).logout(payload.refresh_token)


@router.get("/me", response_model=UserProfile)
async def me(user: CurrentUser) -> UserProfile:
    profile = UserProfile.model_validate(user)
    profile.roles = [r.name for r in user.roles]
    return profile


@router.get("/me/permissions", response_model=EffectivePermissions)
async def my_permissions(user: CurrentUser) -> EffectivePermissions:
    return EffectivePermissions(permissions=sorted(user.effective_permissions))


@router.post("/change-password", status_code=204)
async def change_password(
    payload: ChangePasswordRequest,
    session: DbSession,
    redis: RedisClient,
    user: CurrentUser,
) -> None:
    await AuthService(session, redis).change_password(
        user, payload.current_password, payload.new_password
    )


@router.get("/sessions", response_model=list[SessionInfo])
async def list_sessions(
    session: DbSession, redis: RedisClient, user: CurrentUser
) -> list[SessionInfo]:
    rows = await AuthService(session, redis).list_sessions(user.id)
    return [SessionInfo(**row) for row in rows]


@router.delete("/sessions/{family}", status_code=204)
async def revoke_session(
    family: str, session: DbSession, redis: RedisClient, user: CurrentUser
) -> None:
    await AuthService(session, redis).revoke_session(user.id, family)
