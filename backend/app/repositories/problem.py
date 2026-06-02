"""Problem repository — filtering, FTS ranking, and link resolution."""

import uuid
from datetime import datetime

from sqlalchemy import Select, func, select

from app.core.pagination import PageParams
from app.models.device import Device
from app.models.problem import (
    Problem,
    ProblemCategory,
    Tag,
    problem_devices,
    problem_tags,
)
from app.repositories.base import BaseRepository


class ProblemRepository(BaseRepository[Problem]):
    model = Problem
    sortable = {
        "created_at": "created_at",
        "updated_at": "updated_at",
        "title": "title",
    }

    def _base_select(self) -> Select:
        return select(Problem)

    async def search(
        self,
        params: PageParams,
        *,
        q: str | None = None,
        category_id: uuid.UUID | None = None,
        severity: str | None = None,
        status: str | None = None,
        tag_id: uuid.UUID | None = None,
        device_id: uuid.UUID | None = None,
        site_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        include_archived: bool = False,
    ) -> tuple[list[Problem], int]:
        stmt = select(Problem)
        rank = None

        if not include_archived:
            stmt = stmt.where(Problem.is_archived.is_(False))
        if category_id is not None:
            stmt = stmt.where(Problem.category_id == category_id)
        if severity is not None:
            stmt = stmt.where(Problem.severity == severity)
        if status is not None:
            stmt = stmt.where(Problem.status == status)
        if date_from is not None:
            stmt = stmt.where(Problem.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Problem.created_at <= date_to)
        if tag_id is not None:
            stmt = stmt.where(
                Problem.id.in_(
                    select(problem_tags.c.problem_id).where(
                        problem_tags.c.tag_id == tag_id
                    )
                )
            )
        if device_id is not None:
            stmt = stmt.where(
                Problem.id.in_(
                    select(problem_devices.c.problem_id).where(
                        problem_devices.c.device_id == device_id
                    )
                )
            )
        if site_id is not None:
            stmt = stmt.where(
                Problem.id.in_(
                    select(problem_devices.c.problem_id)
                    .join(Device, Device.id == problem_devices.c.device_id)
                    .where(Device.site_id == site_id)
                )
            )
        if q:
            tsquery = func.websearch_to_tsquery("english", q)
            stmt = stmt.where(Problem.search_vector.op("@@")(tsquery))
            rank = func.ts_rank(Problem.search_vector, tsquery)

        total = await self._count(stmt)

        # Sort: relevance when searching (default), else by params/whitelist.
        if q and (params.sort is None or params.sort == "relevance"):
            stmt = stmt.order_by(rank.desc(), Problem.created_at.desc())
        else:
            stmt = self._apply_sort(stmt, params.sort)

        stmt = stmt.offset(params.offset).limit(params.limit)
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total

    # --- link resolution helpers ---
    async def tags_by_ids(self, ids: list[uuid.UUID]) -> list[Tag]:
        if not ids:
            return []
        return list(
            (await self.session.execute(select(Tag).where(Tag.id.in_(ids)))).scalars()
        )

    async def devices_by_ids(self, ids: list[uuid.UUID]) -> list[Device]:
        if not ids:
            return []
        return list(
            (
                await self.session.execute(select(Device).where(Device.id.in_(ids)))
            ).scalars()
        )

    async def problems_by_ids(self, ids: list[uuid.UUID]) -> list[Problem]:
        if not ids:
            return []
        return list(
            (
                await self.session.execute(select(Problem).where(Problem.id.in_(ids)))
            ).scalars()
        )


class TagRepository(BaseRepository[Tag]):
    model = Tag
    sortable = {"name": "name"}
    default_order_by = "name"

    async def get_by_name(self, name: str) -> Tag | None:
        return await self.get_by(name=name)


class CategoryRepository(BaseRepository[ProblemCategory]):
    model = ProblemCategory
    sortable = {"name": "name"}
    default_order_by = "name"

    async def get_by_name(self, name: str) -> ProblemCategory | None:
        return await self.get_by(name=name)
