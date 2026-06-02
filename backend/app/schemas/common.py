"""Shared schema base + reusable read models."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for response models read from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class NamedRef(ORMModel):
    """Compact reference for nested lookups (id + name)."""

    id: uuid.UUID
    name: str


class TimestampedRead(ORMModel):
    created_at: datetime
    updated_at: datetime
