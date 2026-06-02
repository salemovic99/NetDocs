"""Shared test config. Unit tests need no DB; integration tests are gated."""

import os
import tempfile

import pytest

# Ensure config can load without a real .env during unit tests.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://netdocs:netdocs@localhost:5432/netdocs"
)
os.environ.setdefault("JWT_SECRET", "test-secret-please-change")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
# Deterministic integration tests: no rate limiting, AV off, writable upload dir.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("CLAMAV_ENABLED", "false")
os.environ.setdefault(
    "UPLOAD_DIR", os.path.join(tempfile.gettempdir(), "netdocs-test-uploads")
)


RUN_DB_TESTS = os.environ.get("RUN_DB_TESTS") == "1"

requires_db = pytest.mark.skipif(
    not RUN_DB_TESTS, reason="integration test; set RUN_DB_TESTS=1 and a reachable DB"
)
