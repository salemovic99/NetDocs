"""Unit tests for upload validation (PRD §6.4, §12)."""

import pytest

from app.core import files
from app.core.exceptions import ValidationError

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 32
PDF = b"%PDF-1.7\n" + b"\x00" * 32


def test_accepts_valid_png():
    name, mime, ext = files.validate_upload("diagram.png", "image/png", PNG)
    assert mime == "image/png" and ext == "png" and name == "diagram.png"


def test_rejects_svg():
    with pytest.raises(ValidationError):
        files.validate_upload("x.svg", "image/svg+xml", b"<svg></svg>")


def test_rejects_blocked_extension():
    with pytest.raises(ValidationError):
        files.validate_upload("evil.html", "text/plain", b"<html>")


def test_rejects_disallowed_mime():
    with pytest.raises(ValidationError):
        files.validate_upload("a.bin", "application/x-msdownload", b"MZ")


def test_extension_mime_mismatch():
    with pytest.raises(ValidationError):
        files.validate_upload("photo.png", "application/pdf", PDF)


def test_magic_byte_mismatch():
    with pytest.raises(ValidationError):
        files.validate_upload("photo.png", "image/png", b"not-a-png")


def test_oversize_rejected(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "max_upload_mb", 0)
    with pytest.raises(ValidationError):
        files.validate_upload("a.txt", "text/plain", b"hello world")


def test_filename_sanitized():
    assert files.sanitize_filename("../../etc/passwd") == "passwd"
    assert files.sanitize_filename("  weird name!.txt ") == "weird_name_.txt"
