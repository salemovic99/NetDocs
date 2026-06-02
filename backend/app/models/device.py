"""Devices and per-switch VLANs (PRD §22.4, §22.5)."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, INET, MACADDR
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, UUIDPkMixin


class Device(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "devices"

    hostname: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(255))
    asset_tag: Mapped[str | None] = mapped_column(String(100))

    device_type_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("device_types.id", ondelete="SET NULL")
    )
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("vendors.id", ondelete="SET NULL")
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL")
    )

    management_ip: Mapped[str | None] = mapped_column(INET)
    mac_address: Mapped[str | None] = mapped_column(MACADDR)

    model: Mapped[str | None] = mapped_column(String(255))
    firmware_version: Mapped[str | None] = mapped_column(String(255))
    os_version: Mapped[str | None] = mapped_column(String(255))

    rack_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("racks.id", ondelete="SET NULL")
    )
    rack_position: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text)

    device_type = relationship("DeviceType", lazy="joined")
    vendor = relationship("Vendor", lazy="joined")
    site = relationship("Site", lazy="joined")
    rack = relationship("Rack", lazy="joined")

    vlans: Mapped[list["Vlan"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    problems = relationship(
        "Problem", secondary="problem_devices", back_populates="devices"
    )


class Vlan(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "vlans"
    __table_args__ = (
        UniqueConstraint("device_id", "vlan_id", name="uq_vlans_device_vlan"),
        CheckConstraint("vlan_id BETWEEN 1 AND 4094", name="ck_vlans_tag_range"),
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    vlan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    subnet: Mapped[str | None] = mapped_column(CIDR)
    gateway: Mapped[str | None] = mapped_column(INET)

    device: Mapped[Device] = relationship(back_populates="vlans")
