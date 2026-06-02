"""Problem knowledge-base domain: tags, categories, problems + joins (PRD §22.8, §22.10)."""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, UUIDPkMixin

SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("open", "resolved", "known_issue")

_SEARCH_VECTOR_EXPR = (
    "setweight(to_tsvector('english', coalesce(title,'')),      'A') || "
    "setweight(to_tsvector('english', coalesce(symptoms,'')),   'B') || "
    "setweight(to_tsvector('english', coalesce(root_cause,'')), 'C') || "
    "setweight(to_tsvector('english', coalesce(resolution,'')), 'D')"
)

problem_tags = Table(
    "problem_tags",
    Base.metadata,
    Column(
        "problem_id",
        PgUUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        PgUUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

problem_devices = Table(
    "problem_devices",
    Base.metadata,
    Column(
        "problem_id",
        PgUUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "device_id",
        PgUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

problem_relations = Table(
    "problem_relations",
    Base.metadata,
    Column(
        "problem_id",
        PgUUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "related_problem_id",
        PgUUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    CheckConstraint(
        "problem_id <> related_problem_id", name="ck_problem_relations_no_self"
    ),
)


class Tag(UUIDPkMixin, Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class ProblemCategory(UUIDPkMixin, Base):
    __tablename__ = "problems_categories"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class Problem(UUIDPkMixin, AuditMixin, Base):
    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint(
            f"severity IN {SEVERITIES}", name="ck_problems_severity"
        ),
        CheckConstraint(f"status IN {STATUSES}", name="ck_problems_status"),
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    symptoms: Mapped[str | None] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text)
    resolution: Mapped[str | None] = mapped_column(Text)  # Markdown
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("problems_categories.id", ondelete="SET NULL"),
    )
    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR, Computed(_SEARCH_VECTOR_EXPR, persisted=True)
    )

    category = relationship("ProblemCategory", lazy="joined")
    tags: Mapped[list[Tag]] = relationship(secondary=problem_tags, lazy="selectin")
    devices = relationship(
        "Device", secondary=problem_devices, back_populates="problems", lazy="selectin"
    )
    related_problems = relationship(
        "Problem",
        secondary=problem_relations,
        primaryjoin=lambda: Problem.id == problem_relations.c.problem_id,
        secondaryjoin=lambda: Problem.id == problem_relations.c.related_problem_id,
        lazy="selectin",
    )
