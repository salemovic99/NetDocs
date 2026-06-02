"""Problem (knowledge-base entry) schemas (PRD §6.1, §22.10)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.problem import SEVERITIES, STATUSES
from app.schemas.common import ORMModel
from app.schemas.lookups import CategoryRead, TagRead


class ProblemDeviceRef(ORMModel):
    id: uuid.UUID
    hostname: str


class ProblemRelatedRef(ORMModel):
    id: uuid.UUID
    title: str
    status: str


class ProblemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    symptoms: str | None = None
    root_cause: str | None = None
    resolution: str | None = None
    severity: str = "medium"
    status: str = "open"
    category_id: uuid.UUID | None = None
    reported_by: uuid.UUID | None = None
    tag_ids: list[uuid.UUID] = []
    device_ids: list[uuid.UUID] = []
    related_problem_ids: list[uuid.UUID] = []

    @field_validator("severity")
    @classmethod
    def _check_severity(cls, v: str) -> str:
        if v not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        return v

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str) -> str:
        if v not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        return v


class ProblemUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    symptoms: str | None = None
    root_cause: str | None = None
    resolution: str | None = None
    severity: str | None = None
    status: str | None = None
    category_id: uuid.UUID | None = None
    reported_by: uuid.UUID | None = None
    tag_ids: list[uuid.UUID] | None = None
    device_ids: list[uuid.UUID] | None = None
    related_problem_ids: list[uuid.UUID] | None = None

    @field_validator("severity")
    @classmethod
    def _check_severity(cls, v: str | None) -> str | None:
        if v is not None and v not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        return v

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str | None) -> str | None:
        if v is not None and v not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        return v


class ProblemRead(ORMModel):
    id: uuid.UUID
    title: str
    symptoms: str | None = None
    root_cause: str | None = None
    resolution: str | None = None
    severity: str
    status: str
    is_archived: bool
    category: CategoryRead | None = None
    reported_by: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = []
    devices: list[ProblemDeviceRef] = []
    related_problems: list[ProblemRelatedRef] = []
