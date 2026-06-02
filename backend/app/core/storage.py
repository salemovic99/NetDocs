"""Local-volume attachment storage (PRD §6.4, FR-18).

Files are stored under UPLOAD_DIR with a non-guessable, server-generated key
(never a client-supplied name), sharded into two-level subdirectories to keep
directory sizes manageable. Download is access-controlled at the service layer.
"""

import os
import uuid
from collections.abc import Iterator

from app.core.config import settings


def new_storage_key(ext: str | None = None) -> str:
    """Generate a non-guessable storage key, optionally with an extension."""
    key = uuid.uuid4().hex
    if ext:
        ext = ext.lstrip(".").lower()
        if ext:
            key = f"{key}.{ext}"
    return key


def _path(storage_key: str) -> str:
    # Shard by the first 4 hex chars: ab/cd/<key>
    base = storage_key.split(".")[0]
    return os.path.join(settings.upload_dir, base[:2], base[2:4], storage_key)


def save(content: bytes, ext: str | None = None) -> str:
    """Persist bytes to disk; return the storage key."""
    storage_key = new_storage_key(ext)
    dest = _path(storage_key)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(content)
    return storage_key


def open_stream(storage_key: str, chunk_size: int = 64 * 1024) -> Iterator[bytes]:
    """Yield the file's bytes in chunks for streaming responses."""
    with open(_path(storage_key), "rb") as fh:
        while chunk := fh.read(chunk_size):
            yield chunk


def exists(storage_key: str) -> bool:
    return os.path.isfile(_path(storage_key))


def delete(storage_key: str) -> None:
    try:
        os.remove(_path(storage_key))
    except FileNotFoundError:
        pass


def absolute_path(storage_key: str) -> str:
    return _path(storage_key)
