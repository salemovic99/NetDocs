"""Unit tests for JWT keyset rotation (FR-40) and password change schema."""

import importlib
import json

import pytest


def _reload_security_with(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # rebuild the cached settings + security module against the new env
    import app.core.config as config

    config.get_settings.cache_clear()
    config.settings = config.get_settings()
    import app.core.security as security

    importlib.reload(security)
    return security, config


@pytest.fixture(autouse=True)
def _restore():
    """Restore the ORIGINAL settings object identity so modules that did
    `from app.core.config import settings` keep pointing at a valid instance."""
    import app.core.config as config

    original = config.settings
    yield
    config.settings = original
    config.get_settings.cache_clear()
    import app.core.security as security

    importlib.reload(security)


def test_sign_with_active_kid_and_verify_by_kid(monkeypatch):
    keys = {"k1": "secret-one", "k2": "secret-two"}
    security, _ = _reload_security_with(
        monkeypatch,
        JWT_ALGORITHM="HS256",
        JWT_KEYS=json.dumps(keys),
        JWT_ACTIVE_KID="k2",
    )
    token, _ = security.create_access_token("user-1")
    from jose import jwt

    assert jwt.get_unverified_header(token)["kid"] == "k2"
    claims = security.decode_token(token)  # picks k2 by kid
    assert claims["sub"] == "user-1"


def test_old_kid_still_validates_during_overlap(monkeypatch):
    # Sign a token with only k1 active...
    security, _ = _reload_security_with(
        monkeypatch,
        JWT_ALGORITHM="HS256",
        JWT_KEYS=json.dumps({"k1": "secret-one"}),
        JWT_ACTIVE_KID="k1",
    )
    old_token, _ = security.create_access_token("user-1")

    # ...then rotate: k2 active, but k1 kept in the verification keyset.
    security, _ = _reload_security_with(
        monkeypatch,
        JWT_KEYS=json.dumps({"k1": "secret-one", "k2": "secret-two"}),
        JWT_ACTIVE_KID="k2",
    )
    claims = security.decode_token(old_token)
    assert claims["sub"] == "user-1"
