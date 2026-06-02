"""Site and room schemas (PRD §10 /sites, /rooms; §22.9)."""

import uuid

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


# --- Rooms ---
class RoomCreate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    floor: str | None = Field(default=None, max_length=50)
    purpose: str | None = Field(default=None, max_length=100)


class RoomUpdate(RoomCreate):
    pass


class RoomRead(ORMModel):
    id: uuid.UUID
    site_id: uuid.UUID
    name: str | None = None
    floor: str | None = None
    purpose: str | None = None


# --- Sites ---
class SiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    google_map_location: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class SiteUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    google_map_location: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class SiteRead(ORMModel):
    id: uuid.UUID
    name: str
    google_map_location: str | None = None
    city: str | None = None
    country: str | None = None
    timezone: str | None = None
    notes: str | None = None


class SiteDetailRead(SiteRead):
    """Aggregated site view (FR-35): everything located at the site."""

    rooms: list["RoomRead"] = []
    devices: list = []
    racks: list = []
    isp_links: list = []
    wireless_networks: list = []
