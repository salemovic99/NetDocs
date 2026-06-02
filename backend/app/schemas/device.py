"""Device and VLAN schemas with IP/MAC/CIDR validation (PRD FR-5, FR-10, FR-11)."""

import re
import uuid

from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork, field_validator

from app.schemas.common import ORMModel
from app.schemas.lookups import DeviceTypeRead, RackRead, VendorRead
from app.schemas.site import SiteRead

_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
DEVICE_STATUSES = ("active", "spare", "retired")


def _validate_mac(v: str | None) -> str | None:
    if v is None:
        return v
    if not _MAC_RE.match(v):
        raise ValueError("mac_address must be a valid MAC (e.g. aa:bb:cc:dd:ee:ff)")
    return v


def _validate_ip(v: str | None) -> str | None:
    if v is None:
        return v
    IPvAnyAddress(v)  # raises if invalid
    return v


# --- VLANs ---
class VlanCreate(BaseModel):
    vlan_id: int = Field(ge=1, le=4094)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    subnet: str | None = None
    gateway: str | None = None

    @field_validator("subnet")
    @classmethod
    def _check_subnet(cls, v: str | None) -> str | None:
        if v is not None:
            IPvAnyNetwork(v)
        return v

    @field_validator("gateway")
    @classmethod
    def _check_gateway(cls, v: str | None) -> str | None:
        return _validate_ip(v)


class VlanUpdate(BaseModel):
    vlan_id: int | None = Field(default=None, ge=1, le=4094)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    subnet: str | None = None
    gateway: str | None = None

    @field_validator("subnet")
    @classmethod
    def _check_subnet(cls, v: str | None) -> str | None:
        if v is not None:
            IPvAnyNetwork(v)
        return v

    @field_validator("gateway")
    @classmethod
    def _check_gateway(cls, v: str | None) -> str | None:
        return _validate_ip(v)


class VlanRead(ORMModel):
    id: uuid.UUID
    device_id: uuid.UUID
    vlan_id: int
    name: str | None = None
    description: str | None = None
    subnet: str | None = None
    gateway: str | None = None


# --- Devices ---
class DeviceBase(BaseModel):
    serial_number: str | None = Field(default=None, max_length=255)
    asset_tag: str | None = Field(default=None, max_length=100)
    device_type_id: uuid.UUID | None = None
    vendor_id: uuid.UUID | None = None
    site_id: uuid.UUID | None = None
    management_ip: str | None = None
    mac_address: str | None = None
    model: str | None = Field(default=None, max_length=255)
    firmware_version: str | None = Field(default=None, max_length=255)
    os_version: str | None = Field(default=None, max_length=255)
    rack_id: uuid.UUID | None = None
    rack_position: int | None = Field(default=None, ge=0)
    status: str = "active"
    notes: str | None = None

    @field_validator("management_ip")
    @classmethod
    def _check_ip(cls, v: str | None) -> str | None:
        return _validate_ip(v)

    @field_validator("mac_address")
    @classmethod
    def _check_mac(cls, v: str | None) -> str | None:
        return _validate_mac(v)

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str) -> str:
        if v not in DEVICE_STATUSES:
            raise ValueError(f"status must be one of {DEVICE_STATUSES}")
        return v


class DeviceCreate(DeviceBase):
    hostname: str = Field(min_length=1, max_length=255)


class DeviceUpdate(BaseModel):
    hostname: str | None = Field(default=None, max_length=255)
    serial_number: str | None = None
    asset_tag: str | None = None
    device_type_id: uuid.UUID | None = None
    vendor_id: uuid.UUID | None = None
    site_id: uuid.UUID | None = None
    management_ip: str | None = None
    mac_address: str | None = None
    model: str | None = None
    firmware_version: str | None = None
    os_version: str | None = None
    rack_id: uuid.UUID | None = None
    rack_position: int | None = Field(default=None, ge=0)
    status: str | None = None
    notes: str | None = None

    @field_validator("management_ip")
    @classmethod
    def _check_ip(cls, v: str | None) -> str | None:
        return _validate_ip(v)

    @field_validator("mac_address")
    @classmethod
    def _check_mac(cls, v: str | None) -> str | None:
        return _validate_mac(v)

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str | None) -> str | None:
        if v is not None and v not in DEVICE_STATUSES:
            raise ValueError(f"status must be one of {DEVICE_STATUSES}")
        return v


class DeviceRead(ORMModel):
    id: uuid.UUID
    hostname: str
    serial_number: str | None = None
    asset_tag: str | None = None
    management_ip: str | None = None
    mac_address: str | None = None
    model: str | None = None
    firmware_version: str | None = None
    os_version: str | None = None
    rack_position: int | None = None
    status: str
    notes: str | None = None
    device_type: DeviceTypeRead | None = None
    vendor: VendorRead | None = None
    site: SiteRead | None = None
    rack: RackRead | None = None
