"""Upload validation & hardening (PRD §6.4 FR-17/FR-19, §12).

- MIME allow-list (configurable) + extension agreement
- magic-byte sniff for common binary types
- SVG explicitly rejected (stored-XSS risk, §12)
- filename sanitization, size cap
"""

import os
import re

from app.core.config import settings
from app.core.exceptions import ValidationError

# Extensions explicitly never accepted (active content / stored XSS).
BLOCKED_EXTENSIONS = {"svg", "svgz", "html", "htm", "xhtml", "js", "exe", "sh", "bat"}

# Canonical extension per allowed MIME type.
MIME_EXTENSIONS: dict[str, set[str]] = {
    "image/png": {"png"},
    "image/jpeg": {"jpg", "jpeg"},
    "image/webp": {"webp"},
    "application/pdf": {"pdf"},
    "text/plain": {"txt", "log", "conf", "cfg", "ini", "yaml", "yml"},
    "application/json": {"json"},
    "application/octet-stream": set(),  # generic configs/binaries; no ext constraint
}

# Magic-byte signatures for binary types we can sniff.
_MAGIC: dict[str, list[bytes]] = {
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/webp": [b"RIFF"],  # followed by WEBP at offset 8
    "application/pdf": [b"%PDF-"],
}

_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """Strip path components and unsafe characters; never empty."""
    name = os.path.basename(filename or "").strip()
    name = _FILENAME_RE.sub("_", name).strip("._") or "file"
    return name[:255]


def extension_of(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lstrip(".").lower()


def _sniff_ok(mime: str, content: bytes) -> bool:
    signatures = _MAGIC.get(mime)
    if not signatures:
        return True  # nothing to sniff (text/json/octet-stream)
    if mime == "image/webp":
        return content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    return any(content.startswith(sig) for sig in signatures)


def validate_upload(
    filename: str, content_type: str | None, content: bytes
) -> tuple[str, str, str]:
    """Validate an upload. Returns (safe_filename, mime_type, extension).

    Raises ValidationError on any policy violation.
    """
    safe_name = sanitize_filename(filename)
    ext = extension_of(safe_name)

    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(f"File type '.{ext}' is not allowed")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) == 0:
        raise ValidationError("Empty file")
    if len(content) > max_bytes:
        raise ValidationError(f"File exceeds maximum size of {settings.max_upload_mb} MB")

    mime = (content_type or "application/octet-stream").split(";")[0].strip().lower()
    if mime == "image/svg+xml":
        raise ValidationError("SVG uploads are not allowed")
    if mime not in settings.allowed_mime_types:
        raise ValidationError(f"MIME type '{mime}' is not allowed")

    # Extension must agree with the declared MIME (when that MIME constrains it).
    allowed_exts = MIME_EXTENSIONS.get(mime)
    if allowed_exts and ext and ext not in allowed_exts:
        raise ValidationError(
            f"Extension '.{ext}' does not match content type '{mime}'"
        )

    if not _sniff_ok(mime, content):
        raise ValidationError("File content does not match its declared type")

    return safe_name, mime, ext
