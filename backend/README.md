# NetDocs Backend

FastAPI backend for **NetDocs** — the self-hosted Network & IT Problems Documentation
Platform (see `../PRD.md`). Built with a layered, repository-pattern architecture.

## Architecture

Strict one-directional dependency flow — **separation of concerns**:

```
api/v1/routes  →  services  →  repositories  →  models
   (HTTP)         (business)     (queries)       (ORM)
   schemas (Pydantic DTOs) cross every layer for I/O
```

- **routes** — parse/validate input, call a service, serialize the response. No queries.
- **services** — business rules, transaction boundaries, audit-log writes, stamping
  `created_by`/`updated_by`, optimistic-concurrency checks.
- **repositories** — the only layer that builds queries / touches the `AsyncSession`
  (generic `BaseRepository` + per-aggregate repos). No business logic.
- **models** — SQLAlchemy 2.0 ORM; **schemas** — Pydantic v2 request/response models.

```
app/
  core/        config, database, redis, security, deps, pagination, logging,
               exceptions, concurrency, permissions
  models/      ORM models (PRD §22)
  schemas/     Pydantic DTOs
  repositories/ data access (repository pattern)
  services/    business logic
  api/v1/      routers + thin route handlers
  db/seed.py   first-run bootstrap admin
alembic/       versioned migrations (0001 schema, 0002 RBAC seed)
tests/         pytest suite
```

## Tech stack

FastAPI · async SQLAlchemy 2.0 + asyncpg · PostgreSQL (pgcrypto/citext/pg_trgm) ·
Alembic · Redis · JWT (`kid`, HS256 dev / RS256 prod) · argon2id · Pydantic v2.

## Run with Docker (one command)

The Compose stack lives at the **project root** (`../docker-compose.yml`) and covers
both backend and frontend:

```bash
cd ..                         # project root
docker compose up --build                       # db + redis + api
docker compose --profile frontend up --build    # + frontend (needs frontend/Dockerfile)
```

This starts Postgres + Redis + the API. The API container runs `alembic upgrade head`
(schema + RBAC seed) and then boots; on first run it creates the bootstrap **Network
Admin** from `BOOTSTRAP_ADMIN_*` (must change password on first login).

- API docs (OpenAPI/Swagger): http://localhost:8000/docs
- Liveness: `GET /healthz` · Readiness: `GET /readyz`

## Run locally (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
# point DATABASE_URL/REDIS_URL at running Postgres + Redis, then:
alembic upgrade head
python -m app.db.seed          # create bootstrap admin
uvicorn app.main:app --reload
```

## Auth quick start

```bash
# log in as the bootstrap admin
curl -s localhost:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"identifier":"admin","password":"ChangeMe123!456"}'
# -> { access_token, refresh_token, must_change_password: true }

curl -s localhost:8000/api/v1/auth/me -H "authorization: Bearer <access_token>"
curl -s localhost:8000/api/v1/auth/me/permissions -H "authorization: Bearer <access_token>"
```

## Permissions

Authorization is permission-based: a user's effective permissions are the **union**
across all assigned roles. The catalog and the built-in role grants (§6.6) live in
`app/core/permissions.py` and are seeded by migration `0002_seed_rbac`. Endpoints guard
with `require_permission("problems.write")` etc.

## Tests

```bash
pytest                 # unit tests (no DB needed)
RUN_DB_TESTS=1 pytest  # also runs Postgres integration tests (needs DATABASE_URL)
```

## Implemented

**M1–M4:** auth (login/refresh/logout/me), RBAC, full CRUD for problems (FTS + trigram
search, filters, archive, related/tags/devices linking, optimistic concurrency), devices +
per-switch VLANs, sites + rooms + site aggregate, ISP/WAN links, wireless networks, inventory
lookups, tags/categories, user & role/permission management, audit log, health/readiness.

**M5 — Attachments & AV:** validated multipart upload (MIME allow-list, magic-byte sniff,
SVG blocked, size cap, sanitized names, non-guessable keys) on problems & devices;
access-controlled streaming download (`Content-Disposition: attachment`); ClamAV scanning via a
background `worker` (`python -m app.worker.main`) with download gated on `av_status=clean`;
orphan-file cleanup. See `app/core/storage.py`, `app/core/files.py`, `app/worker/main.py`.

**M6 — Security hardening:** Redis rate limiting (login 5/min/IP + 10/min/account, writes
60/min/user → 429 + `Retry-After`); refresh-token **reuse detection** with family revocation +
session visibility (`/auth/sessions`, `/users/{id}/sessions`); JWT **key rotation** (`kid`
keyset, `JWT_KEYS`/`JWT_ACTIVE_KID`); password change (`/auth/change-password`) + admin reset
(`/users/{id}/reset-password`) + unlock (`/users/{id}/unlock`); `must_change_password` blocks
writes until cleared; security-headers middleware (CSP/HSTS/nosniff/frame-ancestors).

**M7 — Observability & ops:** Prometheus `/metrics` + request metrics middleware; `/readyz`
checks DB + Redis + **migrations current**; backup/restore scripts (`scripts/backup.sh`,
`scripts/restore.sh`) and `docs/OPERATIONS.md` (cron, PITR guidance, retention, DR drill).

**Still deferred (future):** SMTP-based self-service reset, Grafana dashboards, multi-node HA.
