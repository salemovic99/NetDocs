"""Shared pagination primitives (PRD §7: default page_size=25, max 100)."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


class PageParams(BaseModel):
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    sort: str | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    sort: str | None = Query(None),
) -> PageParams:
    """FastAPI dependency providing validated pagination/sort params."""
    return PageParams(page=page, page_size=page_size, sort=sort)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @classmethod
    def create(
        cls, items: list[T], total: int, params: PageParams
    ) -> "Page[T]":
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )
