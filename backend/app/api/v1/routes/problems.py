"""Problem knowledge-base endpoints (PRD §10 /problems)."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.core import permissions as perms
from app.core.concurrency import check_etag, make_etag
from app.core.deps import CurrentUser, DbSession, if_match_header, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.problem import ProblemCreate, ProblemRead, ProblemUpdate
from app.services.problem_service import ProblemService

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get(
    "",
    response_model=Page[ProblemRead],
    dependencies=[Depends(require_permission(perms.PROBLEMS_READ))],
)
async def list_problems(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    q: str | None = Query(None, description="full-text search query"),
    tag: uuid.UUID | None = None,
    category: uuid.UUID | None = None,
    severity: str | None = None,
    status: str | None = None,
    device: uuid.UUID | None = None,
    site: uuid.UUID | None = None,
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
) -> Page[ProblemRead]:
    items, total = await ProblemService(session).search(
        params,
        q=q,
        tag_id=tag,
        category_id=category,
        severity=severity,
        status=status,
        device_id=device,
        site_id=site,
        date_from=date_from,
        date_to=date_to,
    )
    return Page.create([ProblemRead.model_validate(p) for p in items], total, params)


@router.post(
    "",
    response_model=ProblemRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.PROBLEMS_WRITE))],
)
async def create_problem(
    payload: ProblemCreate, session: DbSession, user: CurrentUser
) -> ProblemRead:
    problem = await ProblemService(session).create(payload, actor_id=user.id)
    return ProblemRead.model_validate(problem)


@router.get(
    "/{problem_id}",
    response_model=ProblemRead,
    dependencies=[Depends(require_permission(perms.PROBLEMS_READ))],
)
async def get_problem(
    problem_id: uuid.UUID, session: DbSession, response: Response
) -> ProblemRead:
    problem = await ProblemService(session).get(problem_id)
    response.headers["ETag"] = make_etag(problem.updated_at)
    return ProblemRead.model_validate(problem)


@router.patch(
    "/{problem_id}",
    response_model=ProblemRead,
    dependencies=[Depends(require_permission(perms.PROBLEMS_WRITE))],
)
async def update_problem(
    problem_id: uuid.UUID,
    payload: ProblemUpdate,
    session: DbSession,
    user: CurrentUser,
    response: Response,
    if_match: Annotated[str | None, Depends(if_match_header)] = None,
) -> ProblemRead:
    service = ProblemService(session)
    current = await service.get(problem_id)
    check_etag(current.updated_at, if_match)
    problem = await service.update(problem_id, payload, actor_id=user.id)
    response.headers["ETag"] = make_etag(problem.updated_at)
    return ProblemRead.model_validate(problem)


@router.delete(
    "/{problem_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.PROBLEMS_DELETE))],
)
async def archive_problem(
    problem_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await ProblemService(session).archive(problem_id, actor_id=user.id)


# Attachment endpoints for problems live in app/api/v1/routes/attachments.py (M5).
