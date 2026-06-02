"""Unit tests for local attachment storage (tmpdir-backed)."""

from app.core import storage


def test_save_open_delete(monkeypatch, tmp_path):
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))

    key = storage.save(b"hello bytes", "txt")
    assert key.endswith(".txt")
    assert storage.exists(key)
    assert b"".join(storage.open_stream(key)) == b"hello bytes"

    storage.delete(key)
    assert not storage.exists(key)


def test_keys_are_unique(monkeypatch, tmp_path):
    from app.core.config import settings

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    keys = {storage.save(b"x", "png") for _ in range(5)}
    assert len(keys) == 5
