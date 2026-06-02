"""Problem knowledge-base service: CRUD, linking, search, archive, audit."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.pagination import PageParams
from app.models.problem import Problem, problem_relations
from app.repositories.problem import ProblemRepository
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.services.audit_service import AuditService

_SCALAR_FIELDS = (
    "title",
    "symptoms",
    "root_cause",
    "resolution",
    "severity",
    "status",
    "category_id",
    "reported_by",
)


class ProblemService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProblemRepository(session)
        self.audit = AuditService(session)

    async def get(self, problem_id: uuid.UUID) -> Problem:
        problem = await self.repo.get(problem_id)
        if problem is None or problem.is_archived:
            raise NotFoundError("Problem not found")
        return problem

    async def search(self, params: PageParams, **filters) -> tuple[list[Problem], int]:
        return await self.repo.search(params, **filters)

    async def create(
        self, payload: ProblemCreate, actor_id: uuid.UUID | None
    ) -> Problem:
        problem = Problem(
            title=payload.title,
            symptoms=payload.symptoms,
            root_cause=payload.root_cause,
            resolution=payload.resolution,
            severity=payload.severity,
            status=payload.status,
            category_id=payload.category_id,
            reported_by=payload.reported_by,
            created_by=actor_id,
            updated_by=actor_id,
        )
        problem.tags = await self.repo.tags_by_ids(payload.tag_ids)
        problem.devices = await self.repo.devices_by_ids(payload.device_ids)
        self.repo.add(problem)
        await self.repo.flush()
        await self._set_relations(problem.id, payload.related_problem_ids)
        self.audit.record(
            action="problem.create",
            actor_id=actor_id,
            entity_type="problems",
            entity_id=problem.id,
            diff={"title": payload.title},
        )
        await self.session.commit()
        return await self.get(problem.id)

    async def update(
        self, problem_id: uuid.UUID, payload: ProblemUpdate, actor_id: uuid.UUID | None
    ) -> Problem:
        problem = await self.get(problem_id)
        changes: dict = {}
        for field in _SCALAR_FIELDS:
            value = getattr(payload, field)
            if value is not None:
                setattr(problem, field, value)
                changes[field] = str(value)

        if payload.tag_ids is not None:
            problem.tags = await self.repo.tags_by_ids(payload.tag_ids)
            changes["tag_ids"] = [str(i) for i in payload.tag_ids]
        if payload.device_ids is not None:
            problem.devices = await self.repo.devices_by_ids(payload.device_ids)
            changes["device_ids"] = [str(i) for i in payload.device_ids]
        if payload.related_problem_ids is not None:
            await self._set_relations(problem.id, payload.related_problem_ids)
            changes["related_problem_ids"] = [
                str(i) for i in payload.related_problem_ids
            ]

        problem.updated_by = actor_id
        self.audit.record(
            action="problem.update",
            actor_id=actor_id,
            entity_type="problems",
            entity_id=problem.id,
            diff=changes,
        )
        await self.session.commit()
        return await self.get(problem.id)

    async def archive(self, problem_id: uuid.UUID, actor_id: uuid.UUID | None) -> None:
        problem = await self.get(problem_id)
        problem.is_archived = True
        problem.updated_by = actor_id
        self.audit.record(
            action="problem.archive",
            actor_id=actor_id,
            entity_type="problems",
            entity_id=problem.id,
        )
        await self.session.commit()

    async def _set_relations(
        self, problem_id: uuid.UUID, related_ids: list[uuid.UUID]
    ) -> None:
        """Replace this problem's relations, kept symmetric/bi-directional (A5)."""
        if problem_id in related_ids:
            raise ValidationError("A problem cannot be related to itself")
        # verify targets exist
        targets = await self.repo.problems_by_ids(related_ids)
        if len(targets) != len(set(related_ids)):
            raise ValidationError("One or more related problems do not exist")

        await self.session.execute(
            delete(problem_relations).where(
                or_(
                    problem_relations.c.problem_id == problem_id,
                    problem_relations.c.related_problem_id == problem_id,
                )
            )
        )
        rows: list[dict] = []
        for rid in set(related_ids):
            rows.append({"problem_id": problem_id, "related_problem_id": rid})
            rows.append({"problem_id": rid, "related_problem_id": problem_id})
        if rows:
            await self.session.execute(insert(problem_relations).values(rows))
