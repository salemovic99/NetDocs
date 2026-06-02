"""End-to-end API tests (gated by RUN_DB_TESTS=1; needs Postgres + Redis).

Exercises the PRD verification flow: auth, RBAC denial, KB create + FTS search,
device linkage, and optimistic-concurrency 409.
"""

import uuid

import pytest
import pytest_asyncio

from tests.conftest import requires_db

pytestmark = [requires_db, pytest.mark.asyncio]


async def _migrate_and_seed():
    from alembic.config import Config
    from sqlalchemy import select

    from alembic import command
    from app.core import security
    from app.core.database import SessionFactory
    from app.models.user import Role, User

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")

    async with SessionFactory() as session:
        admin = (
            await session.execute(select(User).where(User.username == "admin"))
        ).scalar_one_or_none()
        if admin is None:
            role = (
                await session.execute(
                    select(Role).where(Role.name == "Network Admin")
                )
            ).scalar_one()
            admin = User(
                email="admin@example.com",
                username="admin",
                password_hash=security.hash_password("ChangeMe123!456"),
                roles=[role],
            )
            session.add(admin)
            await session.commit()


@pytest_asyncio.fixture()
async def client():
    from httpx import ASGITransport, AsyncClient

    from app.main import create_app

    await _migrate_and_seed()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _login(client, identifier, password):
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


async def test_login_me_and_permissions(client):
    token = await _login(client, "admin", "ChangeMe123!456")
    headers = {"authorization": f"Bearer {token}"}
    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    perms = await client.get("/api/v1/auth/me/permissions", headers=headers)
    assert "problems.write" in perms.json()["permissions"]


async def test_rbac_viewer_cannot_create_problem(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}

    uname = f"viewer_{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/users",
        headers=ah,
        json={
            "email": f"{uname}@example.com",
            "username": uname,
            "password": "ViewerPass123!",
            "role_names": ["Viewer"],
            "must_change_password": False,
        },
    )
    assert r.status_code == 201, r.text

    viewer = await _login(client, uname, "ViewerPass123!")
    vh = {"authorization": f"Bearer {viewer}"}
    denied = await client.post(
        "/api/v1/problems", headers=vh, json={"title": "nope"}
    )
    assert denied.status_code == 403
    allowed = await client.post(
        "/api/v1/problems", headers=ah, json={"title": "Admin can create"}
    )
    assert allowed.status_code == 201


async def test_kb_create_search_and_device_link(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}

    cat = await client.post(
        "/api/v1/problem-categories", headers=ah, json={"name": f"VPN-{uuid.uuid4().hex[:6]}"}
    )
    device = await client.post(
        "/api/v1/devices",
        headers=ah,
        json={"hostname": f"sw-{uuid.uuid4().hex[:6]}", "management_ip": "10.0.0.1"},
    )
    assert device.status_code == 201, device.text
    device_id = device.json()["id"]

    created = await client.post(
        "/api/v1/problems",
        headers=ah,
        json={
            "title": "Anyconnect VPN drops every 30 minutes",
            "symptoms": "tunnel resets, reauth loop",
            "category_id": cat.json()["id"],
            "device_ids": [device_id],
        },
    )
    assert created.status_code == 201, created.text

    found = await client.get("/api/v1/problems?q=anyconnect+vpn", headers=ah)
    assert found.status_code == 200
    titles = [p["title"] for p in found.json()["items"]]
    assert any("Anyconnect" in t for t in titles)

    dev = await client.get(f"/api/v1/devices/{device_id}", headers=ah)
    assert dev.status_code == 200


async def test_optimistic_concurrency_conflict(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}
    created = await client.post(
        "/api/v1/problems", headers=ah, json={"title": "Race me"}
    )
    pid = created.json()["id"]
    got = await client.get(f"/api/v1/problems/{pid}", headers=ah)
    etag = got.headers["ETag"]

    ok = await client.patch(
        f"/api/v1/problems/{pid}",
        headers={**ah, "If-Unmatched": etag},
        json={"title": "First write"},
    )
    assert ok.status_code == 200
    conflict = await client.patch(
        f"/api/v1/problems/{pid}",
        headers={**ah, "If-Unmatched": etag},  # stale
        json={"title": "Second write"},
    )
    assert conflict.status_code == 409


# --- M5: attachments ---
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


async def test_attachment_upload_download_and_svg_rejected(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}
    created = await client.post(
        "/api/v1/problems", headers=ah, json={"title": "Has evidence"}
    )
    pid = created.json()["id"]

    up = await client.post(
        f"/api/v1/problems/{pid}/attachments",
        headers=ah,
        files={"file": ("log.png", PNG_BYTES, "image/png")},
    )
    assert up.status_code == 201, up.text
    att = up.json()
    # CLAMAV disabled in test env -> marked clean immediately, so download works.
    assert att["av_status"] == "clean"

    dl = await client.get(f"/api/v1/attachments/{att['id']}", headers=ah)
    assert dl.status_code == 200
    assert dl.headers["content-disposition"].startswith("attachment")
    assert dl.content == PNG_BYTES

    bad = await client.post(
        f"/api/v1/problems/{pid}/attachments",
        headers=ah,
        files={"file": ("x.svg", b"<svg></svg>", "image/svg+xml")},
    )
    assert bad.status_code == 422


# --- M6: security hardening ---
async def test_change_password_clears_flag(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}
    uname = f"hd_{uuid.uuid4().hex[:8]}"
    await client.post(
        "/api/v1/users",
        headers=ah,
        json={
            "email": f"{uname}@example.com",
            "username": uname,
            "password": "InitialPass123!",
            "role_names": ["Helpdesk"],
            "must_change_password": True,
        },
    )
    tok = await _login(client, uname, "InitialPass123!")
    uh = {"authorization": f"Bearer {tok}"}

    # must_change_password blocks writes...
    blocked = await client.post("/api/v1/problems", headers=uh, json={"title": "x"})
    assert blocked.status_code == 403
    assert blocked.json()["code"] == "password_change_required"

    # ...until the password is changed.
    chg = await client.post(
        "/api/v1/auth/change-password",
        headers=uh,
        json={"current_password": "InitialPass123!", "new_password": "BrandNewPass123!"},
    )
    assert chg.status_code == 204
    tok2 = await _login(client, uname, "BrandNewPass123!")
    ok = await client.post(
        "/api/v1/problems",
        headers={"authorization": f"Bearer {tok2}"},
        json={"title": "now allowed"},
    )
    assert ok.status_code == 201


async def test_refresh_reuse_revokes_family(client):
    login = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "admin", "password": "ChangeMe123!456"},
    )
    refresh = login.json()["refresh_token"]

    first = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert first.status_code == 200  # rotates; old token now stale

    reuse = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert reuse.status_code == 401  # reuse detected -> family revoked

    # the rotated (newer) token is now also dead because the family was revoked
    newer = first.json()["refresh_token"]
    after = await client.post("/api/v1/auth/refresh", json={"refresh_token": newer})
    assert after.status_code == 401


async def test_admin_unlock(client):
    admin = await _login(client, "admin", "ChangeMe123!456")
    ah = {"authorization": f"Bearer {admin}"}
    uname = f"lock_{uuid.uuid4().hex[:8]}"
    created = await client.post(
        "/api/v1/users",
        headers=ah,
        json={
            "email": f"{uname}@example.com",
            "username": uname,
            "password": "LockPass123!456",
            "role_names": ["Viewer"],
            "must_change_password": False,
        },
    )
    uid = created.json()["id"]
    unlocked = await client.post(f"/api/v1/users/{uid}/unlock", headers=ah)
    assert unlocked.status_code == 200
