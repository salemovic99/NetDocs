"""User and role administration services (PRD §6.5, §10 /users, /roles)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.pagination import PageParams
from app.core.permissions import PERMISSION_CATALOG
from app.models.user import Role, User
from app.repositories.user import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from app.services.audit_service import AuditService


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)
        self.audit = AuditService(session)

    async def list_users(self, params: PageParams) -> tuple[list[User], int]:
        return await self.users.list(params)

    async def get(self, user_id: uuid.UUID) -> User:
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def create(
        self,
        *,
        email: str,
        username: str,
        password: str,
        full_name: str | None,
        role_names: list[str],
        must_change_password: bool,
        actor_id: uuid.UUID | None,
    ) -> User:
        if await self.users.get_by(email=email):
            raise ConflictError("Email already in use")
        if await self.users.get_by(username=username):
            raise ConflictError("Username already in use")

        roles = await self.roles.get_by_names(role_names)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            password_hash=security.hash_password(password),
            must_change_password=must_change_password,
            roles=roles,
        )
        self.users.add(user)
        await self.users.flush()
        self.audit.record(
            action="user.create",
            actor_id=actor_id,
            entity_type="users",
            entity_id=user.id,
            diff={"email": email, "username": username, "roles": role_names},
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(
        self, user_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> User:
        user = await self.get(user_id)
        for field, value in changes.items():
            if value is not None:
                setattr(user, field, value)
        self.audit.record(
            action="user.update",
            actor_id=actor_id,
            entity_type="users",
            entity_id=user.id,
            diff=changes,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def unlock(self, user_id: uuid.UUID, actor_id: uuid.UUID | None) -> User:
        """Clear lockout + failed-login counter (PRD §6.10 FR-37 admin unlock)."""
        user = await self.get(user_id)
        user.failed_login_count = 0
        user.locked_until = None
        self.audit.record(
            action="user.unlock",
            actor_id=actor_id,
            entity_type="users",
            entity_id=user.id,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def reset_password(
        self, user_id: uuid.UUID, actor_id: uuid.UUID | None
    ) -> tuple[User, str]:
        """Admin-initiated reset (FR-41): set a one-time temp password, force change.

        Returns (user, temporary_password). The caller surfaces the temp password
        to the admin exactly once and should revoke the user's sessions.
        """
        import secrets

        user = await self.get(user_id)
        temp_password = secrets.token_urlsafe(16)
        user.password_hash = security.hash_password(temp_password)
        user.must_change_password = True
        user.failed_login_count = 0
        user.locked_until = None
        self.audit.record(
            action="user.reset_password",
            actor_id=actor_id,
            entity_type="users",
            entity_id=user.id,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user, temp_password

    async def set_roles(
        self, user_id: uuid.UUID, role_names: list[str], actor_id: uuid.UUID | None
    ) -> User:
        user = await self.get(user_id)
        roles = await self.roles.get_by_names(role_names)
        found = {r.name for r in roles}
        missing = set(role_names) - found
        if missing:
            raise ValidationError(f"Unknown roles: {', '.join(sorted(missing))}")
        user.roles = roles
        self.audit.record(
            action="user.set_roles",
            actor_id=actor_id,
            entity_type="users",
            entity_id=user.id,
            diff={"roles": role_names},
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.roles = RoleRepository(session)
        self.permissions = PermissionRepository(session)
        self.audit = AuditService(session)

    async def list_roles(self, params: PageParams) -> tuple[list[Role], int]:
        return await self.roles.list(params)

    async def list_permissions(self, params: PageParams):
        return await self.permissions.list(params)

    async def get(self, role_id: uuid.UUID) -> Role:
        role = await self.roles.get(role_id)
        if role is None:
            raise NotFoundError("Role not found")
        return role

    async def create(
        self, *, name: str, description: str | None, actor_id: uuid.UUID | None
    ) -> Role:
        if await self.roles.get_by_name(name):
            raise ConflictError("Role name already exists")
        role = Role(name=name, description=description, is_system=False)
        self.roles.add(role)
        await self.roles.flush()
        self.audit.record(
            action="role.create",
            actor_id=actor_id,
            entity_type="roles",
            entity_id=role.id,
            diff={"name": name},
        )
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def update(
        self, role_id: uuid.UUID, changes: dict, actor_id: uuid.UUID | None
    ) -> Role:
        role = await self.get(role_id)
        if role.is_system and "name" in changes and changes["name"]:
            raise ValidationError("Cannot rename a system role")
        for field, value in changes.items():
            if value is not None:
                setattr(role, field, value)
        self.audit.record(
            action="role.update",
            actor_id=actor_id,
            entity_type="roles",
            entity_id=role.id,
            diff=changes,
        )
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def delete(self, role_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        role = await self.get(role_id)
        if role.is_system:
            raise ValidationError("Cannot delete a system role")
        self.audit.record(
            action="role.delete",
            actor_id=actor_id,
            entity_type="roles",
            entity_id=role.id,
        )
        await self.roles.delete(role)
        await self.session.commit()

    async def set_permissions(
        self, role_id: uuid.UUID, codes: list[str], actor_id: uuid.UUID | None
    ) -> Role:
        role = await self.get(role_id)
        unknown = [c for c in codes if c not in PERMISSION_CATALOG]
        if unknown:
            raise ValidationError(f"Unknown permissions: {', '.join(unknown)}")
        role.permissions = await self.permissions.get_by_codes(codes)
        self.audit.record(
            action="role.set_permissions",
            actor_id=actor_id,
            entity_type="roles",
            entity_id=role.id,
            diff={"permissions": codes},
        )
        await self.session.commit()
        await self.session.refresh(role)
        return role
