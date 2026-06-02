"""Inventory lookups + rack (PRD §22.4): device_types, vendors, racks."""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, UUIDPkMixin


class DeviceType(UUIDPkMixin, Base):
    __tablename__ = "device_types"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Vendor(UUIDPkMixin, Base):
    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    website: Mapped[str | None] = mapped_column(Text)
    support_contact: Mapped[str | None] = mapped_column(Text)


class Rack(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "racks"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL")
    )
    height_units: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    site = relationship("Site")
