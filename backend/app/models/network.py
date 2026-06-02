"""ISP/WAN links and wireless networks (PRD §22.6, §22.7)."""

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, UUIDPkMixin


class IspLink(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "isp_links"

    site_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    provider_name: Mapped[str | None] = mapped_column(String(255))
    circuit_id: Mapped[str | None] = mapped_column(String(255))
    public_ip: Mapped[str | None] = mapped_column(INET)
    bandwidth_mbps: Mapped[int | None] = mapped_column(Integer)
    connection_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    site = relationship("Site")


class WirelessNetwork(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "wireless_networks"
    __table_args__ = (
        CheckConstraint(
            "vlan_tag BETWEEN 1 AND 4094", name="ck_wireless_vlan_tag_range"
        ),
    )

    site_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    ssid: Mapped[str] = mapped_column(String(255), nullable=False)
    vlan_tag: Mapped[int | None] = mapped_column(Integer)
    security_type: Mapped[str | None] = mapped_column(String(50))
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    site = relationship("Site")
