"""User, role and permission schemas (PRD §10 /users, /roles, /permissions)."""

import uuid

from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.schemas.common import ORMModel, TimestampedRead


# --- Permissions ---
class PermissionRead(ORMModel):
    id: uuid.UUID
    code: str
    description: str | None = None


# --- Roles ---
class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = None


class RoleRead(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    is_system: bool
    permissions: list[PermissionRead] = []


class RolePermissionsUpdate(BaseModel):
    permission_codes: list[str]


# --- Users ---
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=100)
    full_name: str | None = None
    password: str = Field(min_length=settings.password_min_length)
    role_names: list[str] = []
    must_change_password: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, max_length=100)
    full_name: str | None = None
    is_active: bool | None = None


class UserRolesUpdate(BaseModel):
    role_names: list[str]


class PasswordResetResult(BaseModel):
    user_id: uuid.UUID
    temporary_password: str


class UserRead(TimestampedRead):
    id: uuid.UUID
    email: str
    username: str
    full_name: str | None = None
    is_active: bool
    must_change_password: bool
    roles: list[RoleRead] = []
