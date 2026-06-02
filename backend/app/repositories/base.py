"""Generic repository — the only layer that builds queries / touches the session.

Business logic lives in services; this layer is pure data access (PRD: repository pattern).
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.pagination import PageParams
from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Typed CRUD + composable list() with filtering, sort whitelist, pagination."""

    model: type[ModelT]
    #: columns permitted in ``sort`` (maps client name -> column attr name)
    sortable: dict[str, str] = {}
    default_order_by: str = "created_at"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def get_by(self, **filters: Any) -> ModelT | None:
        stmt = select(self.model).filter_by(**filters).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    def _base_select(self) -> Select:
        return select(self.model)

    def _apply_filters(self, stmt: Select, filters: dict[str, Any]) -> Select:
        for key, value in filters.items():
            if value is None:
                continue
            stmt = stmt.where(getattr(self.model, key) == value)
        return stmt

    def _apply_sort(self, stmt: Select, sort: str | None) -> Select:
        column_name = self.default_order_by
        descending = True
        if sort:
            raw = sort.lstrip("-")
            if raw in self.sortable:
                column_name = self.sortable[raw]
                descending = sort.startswith("-")
        column = getattr(self.model, column_name, None)
        if column is None:
            return stmt
        return stmt.order_by(column.desc() if descending else column.asc())

    async def list(
        self,
        params: PageParams,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ModelT], int]:
        stmt = self._apply_filters(self._base_select(), filters or {})
        total = await self._count(stmt)
        stmt = self._apply_sort(stmt, params.sort)
        stmt = stmt.offset(params.offset).limit(params.limit)
        rows = (await self.session.execute(stmt)).unique().scalars().all()
        return list(rows), total

    async def _count(self, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        return int((await self.session.execute(count_stmt)).scalar_one())

    async def list_all(self, **filters: Any) -> list[ModelT]:
        stmt = self._apply_filters(self._base_select(), filters)
        return list((await self.session.execute(stmt)).unique().scalars().all())

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)

    async def flush(self) -> None:
        await self.session.flush()
