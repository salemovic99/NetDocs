"""Optimistic-concurrency helpers (PRD §7: ETag / If-Unmatched -> 409)."""

import hashlib
from datetime import datetime

from app.core.exceptions import ConflictError


def make_etag(updated_at: datetime) -> str:
    """Derive a weak ETag from a row's updated_at timestamp."""
    digest = hashlib.sha256(updated_at.isoformat().encode()).hexdigest()[:16]
    return f'"{digest}"'


def check_etag(updated_at: datetime, if_match: str | None) -> None:
    """Raise 409 if the caller's ETag does not match current state.

    No header supplied => skip the check (concurrency control is opt-in per request).
    """
    if if_match is None:
        return
    current = make_etag(updated_at)
    if if_match.strip() != current:
        raise ConflictError(
            "Resource was modified by another request; reload and retry."
        )
