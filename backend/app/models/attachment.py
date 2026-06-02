"""Attachment metadata (PRD §22.10). Upload/download endpoints deferred (M5)."""

import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin

AV_STATUSES = ("pending", "clean", "infected")


class Attachment(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "attachments"
    __table_args__ = (
        CheckConstraint(f"av_status IN {AV_STATUSES}", name="ck_attachments_av_status"),
        CheckConstraint(
            "problem_id IS NOT NULL OR device_id IS NOT NULL",
            name="ck_attachments_target",
        ),
    )

    problem_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE")
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE")
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    av_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
