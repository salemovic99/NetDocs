"""seed permission catalog + built-in roles and grants (PRD §6.6, §17)

Revision ID: 0002_seed_rbac
Revises: 0001_initial
Create Date: 2026-06-02
"""

import sqlalchemy as sa

from alembic import op
from app.core.permissions import PERMISSION_CATALOG, SYSTEM_ROLES

revision = "0002_seed_rbac"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # permissions
    for code, description in PERMISSION_CATALOG.items():
        bind.execute(
            sa.text(
                "INSERT INTO permissions (code, description) VALUES (:code, :desc) "
                "ON CONFLICT (code) DO NOTHING"
            ),
            {"code": code, "desc": description},
        )

    # roles + grants
    for name, spec in SYSTEM_ROLES.items():
        bind.execute(
            sa.text(
                "INSERT INTO roles (name, description, is_system) "
                "VALUES (:name, :desc, TRUE) ON CONFLICT (name) DO NOTHING"
            ),
            {"name": name, "desc": spec["description"]},
        )
        for code in spec["permissions"]:
            bind.execute(
                sa.text(
                    "INSERT INTO role_permissions (role_id, permission_id) "
                    "SELECT r.id, p.id FROM roles r, permissions p "
                    "WHERE r.name = :name AND p.code = :code "
                    "ON CONFLICT DO NOTHING"
                ),
                {"name": name, "code": code},
            )


def downgrade() -> None:
    bind = op.get_bind()
    names = list(SYSTEM_ROLES.keys())
    bind.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE role_id IN "
            "(SELECT id FROM roles WHERE name = ANY(:names))"
        ),
        {"names": names},
    )
    bind.execute(
        sa.text("DELETE FROM roles WHERE name = ANY(:names)"), {"names": names}
    )
    bind.execute(
        sa.text("DELETE FROM permissions WHERE code = ANY(:codes)"),
        {"codes": list(PERMISSION_CATALOG.keys())},
    )
