"""Application configuration — 12-factor, loaded from env / Docker secrets (PRD §17)."""

import json
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_ALLOWED_MIME_TYPES = (
    "image/png,image/jpeg,image/webp,application/pdf,text/plain,"
    "application/json,application/octet-stream"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = Field(default="dev", alias="ENVIRONMENT")

    # Database / cache
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # JWT
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_secret: str = Field(default="dev-secret-change-me", alias="JWT_SECRET")
    jwt_kid: str = Field(default="dev-1", alias="JWT_KID")
    jwt_private_key: str | None = Field(default=None, alias="JWT_PRIVATE_KEY")
    jwt_public_key: str | None = Field(default=None, alias="JWT_PUBLIC_KEY")
    # Optional keyset for rotation (FR-40). JSON {kid: key}. When set, signing uses
    # JWT_ACTIVE_KID and verification selects the key by the token's `kid` header.
    jwt_keys_raw: str | None = Field(default=None, alias="JWT_KEYS")
    jwt_active_kid: str | None = Field(default=None, alias="JWT_ACTIVE_KID")
    access_token_ttl_seconds: int = Field(default=900, alias="ACCESS_TOKEN_TTL_SECONDS")
    refresh_token_ttl_seconds: int = Field(
        default=1209600, alias="REFRESH_TOKEN_TTL_SECONDS"
    )

    # CORS (comma-separated string in env; parsed via the `cors_origins` property)
    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")

    # Uploads / attachments (M5)
    upload_dir: str = Field(default="/data/attachments", alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=25, alias="MAX_UPLOAD_MB")
    allowed_mime_types_raw: str = Field(
        default=DEFAULT_ALLOWED_MIME_TYPES, alias="ALLOWED_MIME_TYPES"
    )
    attachment_require_clean: bool = Field(
        default=True, alias="ATTACHMENT_REQUIRE_CLEAN"
    )

    # ClamAV (M5)
    clamav_enabled: bool = Field(default=False, alias="CLAMAV_ENABLED")
    clamav_host: str = Field(default="clamav", alias="CLAMAV_HOST")
    clamav_port: int = Field(default=3310, alias="CLAMAV_PORT")

    # Rate limiting (M6)
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_login_ip: int = Field(default=5, alias="RATE_LIMIT_LOGIN_IP")
    rate_limit_login_account: int = Field(
        default=10, alias="RATE_LIMIT_LOGIN_ACCOUNT"
    )
    rate_limit_write_user: int = Field(default=60, alias="RATE_LIMIT_WRITE_USER")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")

    # Security headers (M6)
    security_headers_enabled: bool = Field(
        default=True, alias="SECURITY_HEADERS_ENABLED"
    )

    # Auth policy
    password_min_length: int = Field(default=12, alias="PASSWORD_MIN_LENGTH")
    max_failed_logins: int = Field(default=10, alias="MAX_FAILED_LOGINS")
    lockout_minutes: int = Field(default=15, alias="LOCKOUT_MINUTES")

    # Bootstrap admin
    bootstrap_admin_email: str | None = Field(default=None, alias="BOOTSTRAP_ADMIN_EMAIL")
    bootstrap_admin_username: str | None = Field(
        default=None, alias="BOOTSTRAP_ADMIN_USERNAME"
    )
    bootstrap_admin_password: str | None = Field(
        default=None, alias="BOOTSTRAP_ADMIN_PASSWORD"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def allowed_mime_types(self) -> set[str]:
        return {m.strip() for m in self.allowed_mime_types_raw.split(",") if m.strip()}

    @property
    def jwt_keys(self) -> dict[str, str]:
        """Verification keyset by kid. Falls back to the single-key config."""
        if self.jwt_keys_raw:
            parsed = json.loads(self.jwt_keys_raw)
            return {str(k): str(v) for k, v in parsed.items()}
        return {self.jwt_kid: self.jwt_public_key or self.jwt_secret}

    @property
    def active_kid(self) -> str:
        return self.jwt_active_kid or self.jwt_kid

    @property
    def jwt_signing_key(self) -> str:
        if self.jwt_keys_raw:
            return self.jwt_keys[self.active_kid]
        return self.jwt_private_key or self.jwt_secret

    @property
    def jwt_verification_key(self) -> str:
        return self.jwt_public_key or self.jwt_secret


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
