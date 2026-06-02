"""User / role / permission repositories."""

from sqlalchemy import or_, select

from app.models.user import Permission, Role, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User
    sortable = {"created_at": "created_at", "username": "username", "email": "email"}

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Look up by email OR username (PRD FR-20; CITEXT = case-insensitive)."""
        stmt = (
            select(User)
            .where(or_(User.email == identifier, User.username == identifier))
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()


class RoleRepository(BaseRepository[Role]):
    model = Role
    sortable = {"name": "name"}
    default_order_by = "name"

    async def get_by_name(self, name: str) -> Role | None:
        return await self.get_by(name=name)

    async def get_by_names(self, names: list[str]) -> list[Role]:
        if not names:
            return []
        stmt = select(Role).where(Role.name.in_(names))
        return list((await self.session.execute(stmt)).scalars().all())


class PermissionRepository(BaseRepository[Permission]):
    model = Permission
    sortable = {"code": "code"}
    default_order_by = "code"

    async def get_by_codes(self, codes: list[str]) -> list[Permission]:
        if not codes:
            return []
        stmt = select(Permission).where(Permission.code.in_(codes))
        return list((await self.session.execute(stmt)).scalars().all())
