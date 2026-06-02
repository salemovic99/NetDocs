"""Unit tests for password hashing and JWT (no DB)."""

import pytest

from app.core import security


def test_password_hash_roundtrip():
    h = security.hash_password("CorrectHorse12!")
    assert h != "CorrectHorse12!"
    assert security.verify_password("CorrectHorse12!", h)
    assert not security.verify_password("wrong", h)


def test_verify_handles_garbage_hash():
    assert not security.verify_password("x", "not-a-real-hash")


def test_access_token_roundtrip():
    token, jti = security.create_access_token("user-123")
    claims = security.decode_token(token)
    assert claims["sub"] == "user-123"
    assert claims["type"] == security.ACCESS_TOKEN_TYPE
    assert claims["jti"] == jti


def test_refresh_token_carries_family():
    token, _ = security.create_refresh_token("user-1", "fam-1")
    claims = security.decode_token(token)
    assert claims["type"] == security.REFRESH_TOKEN_TYPE
    assert claims["family"] == "fam-1"


def test_decode_rejects_tampered_token():
    token, _ = security.create_access_token("u")
    with pytest.raises(security.JWTError):
        security.decode_token(token + "tamper")
