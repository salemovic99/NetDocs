"""FastAPI dependencies: DB session, Redis, current user, permission guards."""

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.database import get_session
from app.core.exceptions import (
    AuthenticationError,
    PasswordChangeRequiredError,
    PermissionDeniedError,
)
from app.core.redis import get_redis
from app.models.user import User
from app.repositories.user import UserRepository

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_redis_dep() -> Redis:
    return get_redis()


DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[Redis, Depends(get_redis_dep)]


async def get_current_user(
    session: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer)
    ] = None,
) -> User:
    if credentials is None:
        raise AuthenticationError("Not authenticated")
    try:
        claims = security.decode_token(credentials.credentials)
    except security.JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc
    if claims.get("type") != security.ACCESS_TOKEN_TYPE:
        raise AuthenticationError("Not an access token")

    try:
        user_id = uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Malformed token subject") from exc

    user = await UserRepository(session).get(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# Permission codes that mutate state. Holding one is gated on a fresh password
# (must_change_password must be cleared first) — see PRD §6.10 / §17.
WRITE_CODES = frozenset(
    {
        "problems.write",
        "problems.delete",
        "inventory.manage",
        "tags.manage",
        "users.manage",
        "roles.manage",
        "attachments.upload",
    }
)


def require_permission(code: str):
    """Dependency factory: authorize if the user's effective permissions include `code`.

    Effective permissions are the union across all of the user's roles (PRD §6.6).
    A user flagged `must_change_password` may still read, but is blocked from any
    write/manage capability until they change it.
    """

    async def _guard(user: CurrentUser) -> User:
        if code not in user.effective_permissions:
            raise PermissionDeniedError(f"Missing required permission: {code}")
        if code in WRITE_CODES and user.must_change_password:
            raise PasswordChangeRequiredError(
                "Password change required before performing this action"
            )
        return user

    return _guard


def require_any(*codes: str):
    async def _guard(user: CurrentUser) -> User:
        if not set(codes) & user.effective_permissions:
            raise PermissionDeniedError(
                f"Requires one of: {', '.join(codes)}"
            )
        return user

    return _guard


def client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def if_match_header(
    if_unmatched: Annotated[str | None, Header(alias="If-Unmatched")] = None,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
) -> str | None:
    """Read the optimistic-concurrency ETag from If-Unmatched (PRD §10) or If-Match."""
    return if_unmatched or if_match
