"""Authentication service: login, token rotation w/ reuse detection, sessions.

Token model (PRD §6.10): short-lived access JWT + rotating refresh JWT. Each refresh
token carries a `jti` and `family`. The active jti per family is tracked in Redis
(`SessionStore`); presenting a stale jti for a known family is **reuse** and revokes
the whole family (FR-38). Sessions are visible/revocable (FR-39). When Redis is
absent the service degrades to stateless rotation (dev/test).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.sessions import SessionStore
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.audit_service import AuditService

logger = logging.getLogger("netdocs.auth")


class AuthService:
    def __init__(self, session: AsyncSession, redis: Redis | None = None):
        self.session = session
        self.redis = redis
        self.users = UserRepository(session)
        self.audit = AuditService(session)
        self.sessions = SessionStore(redis) if redis is not None else None

    # --- Flows ---
    async def login(
        self,
        identifier: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, User]:
        user = await self.users.get_by_identifier(identifier)
        now = datetime.now(UTC)

        if user is None:
            self.audit.record(
                action="auth.login_failed",
                diff={"identifier": identifier, "reason": "unknown_user"},
                ip_address=ip_address,
            )
            await self.session.commit()
            raise AuthenticationError("Invalid credentials")

        if user.locked_until and user.locked_until > now:
            self.audit.record(
                action="auth.login_locked", actor_id=user.id, ip_address=ip_address
            )
            await self.session.commit()
            raise AuthenticationError("Account temporarily locked")

        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        if not security.verify_password(password, user.password_hash):
            user.failed_login_count += 1
            if user.failed_login_count >= settings.max_failed_logins:
                user.locked_until = now + timedelta(minutes=settings.lockout_minutes)
            self.audit.record(
                action="auth.login_failed",
                actor_id=user.id,
                diff={"failed_count": user.failed_login_count},
                ip_address=ip_address,
            )
            await self.session.commit()
            raise AuthenticationError("Invalid credentials")

        # success
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = now
        if security.needs_rehash(user.password_hash):
            user.password_hash = security.hash_password(password)

        access, _ = security.create_access_token(str(user.id))
        family_id = uuid.uuid4().hex
        refresh, jti = security.create_refresh_token(str(user.id), family_id)
        if self.sessions is not None:
            await self.sessions.create(
                family=family_id,
                user_id=str(user.id),
                jti=jti,
                ip=ip_address,
                user_agent=user_agent,
            )

        self.audit.record(action="auth.login", actor_id=user.id, ip_address=ip_address)
        await self.session.commit()
        return access, refresh, user

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        try:
            claims = security.decode_token(refresh_token)
        except security.JWTError as exc:
            raise AuthenticationError("Invalid refresh token") from exc

        if claims.get("type") != security.REFRESH_TOKEN_TYPE:
            raise AuthenticationError("Not a refresh token")

        subject = claims["sub"]
        jti = claims.get("jti", "")
        family = claims.get("family", uuid.uuid4().hex)

        if self.sessions is not None:
            stored = await self.sessions.get(family)
            if stored is None:
                raise AuthenticationError("Session expired or revoked")
            if stored.get("current_jti") != jti:
                # Reuse of an already-rotated token -> revoke the whole family (FR-38).
                await self.sessions.revoke(family)
                self.audit.record(
                    action="auth.refresh_reuse",
                    actor_id=uuid.UUID(subject),
                    entity_type="users",
                    entity_id=uuid.UUID(subject),
                    diff={"family": family},
                )
                await self.session.commit()
                raise AuthenticationError("Refresh token reuse detected; session revoked")

        access, _ = security.create_access_token(subject)
        new_refresh, new_jti = security.create_refresh_token(subject, family)
        if self.sessions is not None:
            await self.sessions.rotate(family, new_jti)
        return access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        try:
            claims = security.decode_token(refresh_token)
        except security.JWTError:
            return  # idempotent
        if self.sessions is not None and (family := claims.get("family")):
            await self.sessions.revoke(family)

    async def list_sessions(self, user_id: uuid.UUID) -> list[dict]:
        if self.sessions is None:
            return []
        return await self.sessions.list_for_user(str(user_id))

    async def revoke_session(self, user_id: uuid.UUID, family: str) -> None:
        if self.sessions is None:
            return
        stored = await self.sessions.get(family)
        if stored and stored.get("user_id") == str(user_id):
            await self.sessions.revoke(family)

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        if self.sessions is None:
            return 0
        return await self.sessions.revoke_all(str(user_id))

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not security.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        user.password_hash = security.hash_password(new_password)
        user.must_change_password = False
        self.audit.record(
            action="auth.password_change",
            actor_id=user.id,
            entity_type="users",
            entity_id=user.id,
        )
        await self.session.commit()
        # Invalidate other sessions after a password change.
        await self.revoke_all_sessions(user.id)

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self.users.get(user_id)
