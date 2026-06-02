"""Managed-lookup schemas: device types, vendors, racks, tags, problem categories."""

import uuid

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


# --- Device types ---
class DeviceTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class DeviceTypeRead(ORMModel):
    id: uuid.UUID
    name: str


# --- Vendors ---
class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    website: str | None = None
    support_contact: str | None = None


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    website: str | None = None
    support_contact: str | None = None


class VendorRead(ORMModel):
    id: uuid.UUID
    name: str
    website: str | None = None
    support_contact: str | None = None


# --- Racks ---
class RackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    site_id: uuid.UUID | None = None
    height_units: int | None = Field(default=None, ge=1, le=60)
    notes: str | None = None


class RackUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None
    height_units: int | None = Field(default=None, ge=1, le=60)
    notes: str | None = None


class RackRead(ORMModel):
    id: uuid.UUID
    name: str
    site_id: uuid.UUID | None = None
    height_units: int | None = None
    notes: str | None = None


# --- Tags ---
class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagRead(ORMModel):
    id: uuid.UUID
    name: str


# --- Problem categories ---
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CategoryRead(ORMModel):
    id: uuid.UUID
    name: str
