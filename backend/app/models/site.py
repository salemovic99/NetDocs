"""Sites and rooms (PRD §22.9)."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, UUIDPkMixin


class Site(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    google_map_location: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    timezone: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    rooms: Mapped[list["Room"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class Room(UUIDPkMixin, Base):
    __tablename__ = "rooms"

    site_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255))
    floor: Mapped[str | None] = mapped_column(String(50))
    purpose: Mapped[str | None] = mapped_column(String(100))

    site: Mapped[Site] = relationship(back_populates="rooms")
