"""First-run bootstrap: create the initial Network Admin (PRD §17).

RBAC (permissions, roles, grants) is seeded by Alembic migration 0002. This step
creates the bootstrap admin from env vars if it does not already exist, requiring a
password change on first login. Idempotent and safe to run on every boot.
"""

import asyncio
import logging

from sqlalchemy import func, select

from app.core import security
from app.core.config import settings
from app.core.database import SessionFactory
from app.models.user import Role, User

logger = logging.getLogger("netdocs.seed")

BOOTSTRAP_ROLE = "Network Admin"


async def bootstrap_admin() -> None:
    if not (
        settings.bootstrap_admin_email
        and settings.bootstrap_admin_username
        and settings.bootstrap_admin_password
    ):
        logger.info("bootstrap admin env not set; skipping")
        return

    async with SessionFactory() as session:
        # Only bootstrap when there are no users at all (true first run).
        existing = (await session.execute(select(func.count(User.id)))).scalar_one()
        if existing:
            logger.info("users already present; skipping bootstrap admin")
            return

        role = (
            await session.execute(select(Role).where(Role.name == BOOTSTRAP_ROLE))
        ).scalar_one_or_none()
        if role is None:
            logger.warning(
                "role %s missing; run migrations before bootstrap", BOOTSTRAP_ROLE
            )
            return

        admin = User(
            email=settings.bootstrap_admin_email,
            username=settings.bootstrap_admin_username,
            full_name="Bootstrap Administrator",
            password_hash=security.hash_password(settings.bootstrap_admin_password),
            must_change_password=True,
            roles=[role],
        )
        session.add(admin)
        await session.commit()
        logger.info("bootstrap admin '%s' created", admin.username)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(bootstrap_admin())
