"""Auth request/response schemas (PRD §10 /auth/*)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    # Accepts email OR username (PRD FR-20)
    identifier: str = Field(min_length=1, description="email or username")
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserProfile(ORMModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str | None
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None
    roles: list[str] = []

    @field_validator("roles", mode="before")
    @classmethod
    def _roles_to_names(cls, v: object) -> object:
        # Accept either a list of Role ORM objects or already-flattened names.
        if isinstance(v, (list, tuple, set)):
            return [getattr(r, "name", r) for r in v]
        return v


class EffectivePermissions(BaseModel):
    permissions: list[str]


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=settings.password_min_length)


class SessionInfo(BaseModel):
    family: str
    ip: str | None = None
    user_agent: str | None = None
    created_at: str | None = None
    last_used: str | None = None
    current: bool = False
