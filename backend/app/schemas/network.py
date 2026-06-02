"""ISP/WAN link and wireless network schemas (PRD §6.7, §6.8)."""

import uuid

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator

from app.schemas.common import ORMModel


def _validate_ip(v: str | None) -> str | None:
    if v is not None:
        IPvAnyAddress(v)
    return v


# --- ISP / WAN links ---
class IspLinkCreate(BaseModel):
    site_id: uuid.UUID
    provider_name: str | None = Field(default=None, max_length=255)
    circuit_id: str | None = Field(default=None, max_length=255)
    public_ip: str | None = None
    bandwidth_mbps: int | None = Field(default=None, ge=0)
    connection_type: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=50)
    notes: str | None = None

    @field_validator("public_ip")
    @classmethod
    def _check_ip(cls, v: str | None) -> str | None:
        return _validate_ip(v)


class IspLinkUpdate(BaseModel):
    site_id: uuid.UUID | None = None
    provider_name: str | None = None
    circuit_id: str | None = None
    public_ip: str | None = None
    bandwidth_mbps: int | None = Field(default=None, ge=0)
    connection_type: str | None = None
    status: str | None = None
    notes: str | None = None

    @field_validator("public_ip")
    @classmethod
    def _check_ip(cls, v: str | None) -> str | None:
        return _validate_ip(v)


class IspLinkRead(ORMModel):
    id: uuid.UUID
    site_id: uuid.UUID
    provider_name: str | None = None
    circuit_id: str | None = None
    public_ip: str | None = None
    bandwidth_mbps: int | None = None
    connection_type: str | None = None
    status: str | None = None
    notes: str | None = None


# --- Wireless networks ---
class WirelessCreate(BaseModel):
    site_id: uuid.UUID
    ssid: str = Field(min_length=1, max_length=255)
    vlan_tag: int | None = Field(default=None, ge=1, le=4094)
    security_type: str | None = Field(default=None, max_length=50)
    hidden: bool = False


class WirelessUpdate(BaseModel):
    site_id: uuid.UUID | None = None
    ssid: str | None = Field(default=None, max_length=255)
    vlan_tag: int | None = Field(default=None, ge=1, le=4094)
    security_type: str | None = None
    hidden: bool | None = None


class WirelessRead(ORMModel):
    id: uuid.UUID
    site_id: uuid.UUID
    ssid: str
    vlan_tag: int | None = None
    security_type: str | None = None
    hidden: bool
