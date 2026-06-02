"""initial schema (PRD §22)

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-02
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

UUID = pg.UUID(as_uuid=True)


def _uuid_pk() -> sa.Column:
    return sa.Column(
        "id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
    )


def _ts(name: str) -> sa.Column:
    return sa.Column(
        name, sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")
    )


def _audit_cols() -> list[sa.Column]:
    return [
        sa.Column("created_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("updated_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        _ts("created_at"),
        _ts("updated_at"),
    ]


def upgrade() -> None:
    # --- extensions (PRD prerequisites) ---
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # --- users / roles / permissions ---
    op.create_table(
        "users",
        _uuid_pk(),
        sa.Column("email", pg.CITEXT(), nullable=False, unique=True),
        sa.Column("username", pg.CITEXT(), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "failed_login_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("locked_until", sa.TIMESTAMP(timezone=True)),
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("last_login_at", sa.TIMESTAMP(timezone=True)),
        _ts("created_at"),
        _ts("updated_at"),
    )
    op.create_table(
        "roles",
        _uuid_pk(),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "permissions",
        _uuid_pk(),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            UUID,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            UUID,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            UUID,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            UUID,
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # --- inventory lookups + sites ---
    op.create_table(
        "device_types",
        _uuid_pk(),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "vendors",
        _uuid_pk(),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("website", sa.Text()),
        sa.Column("support_contact", sa.Text()),
    )
    op.create_table(
        "sites",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("google_map_location", sa.Text()),
        sa.Column("city", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("timezone", sa.String(100)),
        sa.Column("notes", sa.Text()),
        *_audit_cols(),
    )
    op.create_table(
        "racks",
        _uuid_pk(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("site_id", UUID, sa.ForeignKey("sites.id", ondelete="SET NULL")),
        sa.Column("height_units", sa.Integer()),
        sa.Column("notes", sa.Text()),
        *_audit_cols(),
    )
    op.create_table(
        "rooms",
        _uuid_pk(),
        sa.Column(
            "site_id",
            UUID,
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255)),
        sa.Column("floor", sa.String(50)),
        sa.Column("purpose", sa.String(100)),
    )

    # --- devices + vlans ---
    op.create_table(
        "devices",
        _uuid_pk(),
        sa.Column("hostname", sa.String(255), nullable=False, unique=True),
        sa.Column("serial_number", sa.String(255)),
        sa.Column("asset_tag", sa.String(100)),
        sa.Column(
            "device_type_id",
            UUID,
            sa.ForeignKey("device_types.id", ondelete="SET NULL"),
        ),
        sa.Column("vendor_id", UUID, sa.ForeignKey("vendors.id", ondelete="SET NULL")),
        sa.Column("site_id", UUID, sa.ForeignKey("sites.id", ondelete="SET NULL")),
        sa.Column("management_ip", pg.INET()),
        sa.Column("mac_address", pg.MACADDR()),
        sa.Column("model", sa.String(255)),
        sa.Column("firmware_version", sa.String(255)),
        sa.Column("os_version", sa.String(255)),
        sa.Column("rack_id", UUID, sa.ForeignKey("racks.id", ondelete="SET NULL")),
        sa.Column("rack_position", sa.Integer()),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text()),
        *_audit_cols(),
    )
    op.create_table(
        "vlans",
        _uuid_pk(),
        sa.Column(
            "device_id",
            UUID,
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("vlan_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("subnet", pg.CIDR()),
        sa.Column("gateway", pg.INET()),
        *_audit_cols(),
        sa.CheckConstraint("vlan_id BETWEEN 1 AND 4094", name="ck_vlans_tag_range"),
        sa.UniqueConstraint("device_id", "vlan_id", name="uq_vlans_device_vlan"),
    )

    # --- isp links + wireless ---
    op.create_table(
        "isp_links",
        _uuid_pk(),
        sa.Column(
            "site_id",
            UUID,
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider_name", sa.String(255)),
        sa.Column("circuit_id", sa.String(255)),
        sa.Column("public_ip", pg.INET()),
        sa.Column("bandwidth_mbps", sa.Integer()),
        sa.Column("connection_type", sa.String(50)),
        sa.Column("status", sa.String(50)),
        sa.Column("notes", sa.Text()),
        *_audit_cols(),
    )
    op.create_table(
        "wireless_networks",
        _uuid_pk(),
        sa.Column(
            "site_id",
            UUID,
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ssid", sa.String(255), nullable=False),
        sa.Column("vlan_tag", sa.Integer()),
        sa.Column("security_type", sa.String(50)),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_audit_cols(),
        sa.CheckConstraint(
            "vlan_tag BETWEEN 1 AND 4094", name="ck_wireless_vlan_tag_range"
        ),
    )

    # --- problems KB ---
    op.create_table(
        "problems_categories",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
    )
    op.create_table(
        "tags",
        _uuid_pk(),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "problems",
        _uuid_pk(),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("symptoms", sa.Text()),
        sa.Column("root_cause", sa.Text()),
        sa.Column("resolution", sa.Text()),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column(
            "category_id",
            UUID,
            sa.ForeignKey("problems_categories.id", ondelete="SET NULL"),
        ),
        sa.Column("reported_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column(
            "is_archived", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "search_vector",
            pg.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('english', coalesce(title,'')),      'A') || "
                "setweight(to_tsvector('english', coalesce(symptoms,'')),   'B') || "
                "setweight(to_tsvector('english', coalesce(root_cause,'')), 'C') || "
                "setweight(to_tsvector('english', coalesce(resolution,'')), 'D')",
                persisted=True,
            ),
        ),
        *_audit_cols(),
        sa.CheckConstraint(
            "severity IN ('low','medium','high','critical')",
            name="ck_problems_severity",
        ),
        sa.CheckConstraint(
            "status IN ('open','resolved','known_issue')", name="ck_problems_status"
        ),
    )
    op.create_table(
        "problem_tags",
        sa.Column(
            "problem_id",
            UUID,
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            UUID,
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "problem_devices",
        sa.Column(
            "problem_id",
            UUID,
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "device_id",
            UUID,
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "problem_relations",
        sa.Column(
            "problem_id",
            UUID,
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "related_problem_id",
            UUID,
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.CheckConstraint(
            "problem_id <> related_problem_id", name="ck_problem_relations_no_self"
        ),
    )
    op.create_table(
        "attachments",
        _uuid_pk(),
        sa.Column("problem_id", UUID, sa.ForeignKey("problems.id", ondelete="CASCADE")),
        sa.Column("device_id", UUID, sa.ForeignKey("devices.id", ondelete="CASCADE")),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("av_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("uploaded_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        _ts("created_at"),
        sa.CheckConstraint(
            "av_status IN ('pending','clean','infected')",
            name="ck_attachments_av_status",
        ),
        sa.CheckConstraint(
            "problem_id IS NOT NULL OR device_id IS NOT NULL",
            name="ck_attachments_target",
        ),
    )

    # --- audit log ---
    op.create_table(
        "audit_log",
        _uuid_pk(),
        sa.Column("actor_id", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", UUID),
        sa.Column("diff", pg.JSONB()),
        sa.Column("ip_address", pg.INET()),
        _ts("created_at"),
    )

    # --- indexes (PRD §9 Indexes) ---
    op.create_index(
        "problems_search_idx", "problems", ["search_vector"], postgresql_using="gin"
    )
    op.create_index(
        "problems_title_trgm",
        "problems",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )
    op.create_index(
        "problems_filter_idx", "problems", ["status", "severity", "created_at"]
    )
    op.create_index(
        "devices_hostname_trgm",
        "devices",
        ["hostname"],
        postgresql_using="gin",
        postgresql_ops={"hostname": "gin_trgm_ops"},
    )
    op.create_index("devices_type_idx", "devices", ["device_type_id"])
    op.create_index("devices_vendor_idx", "devices", ["vendor_id"])
    op.create_index("devices_site_idx", "devices", ["site_id"])
    op.create_index("devices_rack_idx", "devices", ["rack_id"])
    op.create_index("vlans_device_idx", "vlans", ["device_id"])
    op.create_index("isp_links_site_idx", "isp_links", ["site_id"])
    op.create_index("wireless_site_idx", "wireless_networks", ["site_id"])
    op.create_index("rooms_site_idx", "rooms", ["site_id"])
    op.create_index("audit_log_entity_idx", "audit_log", ["entity_type", "entity_id"])
    op.create_index("audit_log_actor_idx", "audit_log", ["actor_id", "created_at"])


def downgrade() -> None:
    for table in (
        "audit_log",
        "attachments",
        "problem_relations",
        "problem_devices",
        "problem_tags",
        "problems",
        "tags",
        "problems_categories",
        "wireless_networks",
        "isp_links",
        "vlans",
        "devices",
        "rooms",
        "racks",
        "sites",
        "vendors",
        "device_types",
        "role_permissions",
        "user_roles",
        "permissions",
        "roles",
        "users",
    ):
        op.drop_table(table)
