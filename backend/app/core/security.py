"""Password hashing (argon2id) and JWT sign/verify with `kid` header (PRD §6.10)."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings

_hasher = PasswordHasher()  # argon2id by default

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


# --- Passwords ---------------------------------------------------------------


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:
        return False


# --- JWT ---------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(UTC)


def _create_token(
    subject: str, token_type: str, ttl_seconds: int, extra: dict[str, Any] | None = None
) -> tuple[str, str]:
    """Return (encoded_jwt, jti)."""
    jti = uuid.uuid4().hex
    claims: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    if extra:
        claims.update(extra)
    token = jwt.encode(
        claims,
        settings.jwt_signing_key,
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.active_kid},
    )
    return token, jti


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, str]:
    return _create_token(
        subject, ACCESS_TOKEN_TYPE, settings.access_token_ttl_seconds, extra
    )


def create_refresh_token(
    subject: str, family_id: str, extra: dict[str, Any] | None = None
) -> tuple[str, str]:
    payload = {"family": family_id, **(extra or {})}
    return _create_token(
        subject, REFRESH_TOKEN_TYPE, settings.refresh_token_ttl_seconds, payload
    )


def _verification_key_for(token: str) -> str:
    """Pick the verification key by the token's `kid` header (FR-40 rotation).

    Falls back to the single-key config when the kid is unknown / absent.
    """
    try:
        kid = jwt.get_unverified_header(token).get("kid")
    except JWTError:
        kid = None
    keys = settings.jwt_keys
    if kid and kid in keys:
        return keys[kid]
    return settings.jwt_verification_key


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises jose.JWTError on failure."""
    return jwt.decode(
        token,
        _verification_key_for(token),
        algorithms=[settings.jwt_algorithm],
    )


__all__ = [
    "ACCESS_TOKEN_TYPE",
    "REFRESH_TOKEN_TYPE",
    "JWTError",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "needs_rehash",
    "verify_password",
]
