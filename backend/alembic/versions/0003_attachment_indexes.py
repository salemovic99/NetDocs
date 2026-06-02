"""attachment FK indexes (PRD §9)

Revision ID: 0003_attachment_indexes
Revises: 0002_seed_rbac
Create Date: 2026-06-02
"""

from alembic import op

revision = "0003_attachment_indexes"
down_revision = "0002_seed_rbac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("attachments_problem_idx", "attachments", ["problem_id"])
    op.create_index("attachments_device_idx", "attachments", ["device_id"])


def downgrade() -> None:
    op.drop_index("attachments_device_idx", table_name="attachments")
    op.drop_index("attachments_problem_idx", table_name="attachments")
