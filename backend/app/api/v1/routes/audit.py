"""Audit-log read endpoint (PRD §10 /audit-log; requires audit.read)."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core import permissions as perms
from app.core.deps import DbSession, require_permission
from app.core.pagination import Page, PageParams, page_params
from app.schemas.audit import AuditLogRead
from app.services.audit_query_service import AuditQueryService

router = APIRouter(tags=["audit"])


@router.get(
    "/audit-log",
    response_model=Page[AuditLogRead],
    dependencies=[Depends(require_permission(perms.AUDIT_READ))],
)
async def list_audit_log(
    session: DbSession,
    params: Annotated[PageParams, Depends(page_params)],
    actor: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
) -> Page[AuditLogRead]:
    items, total = await AuditQueryService(session).list(
        params,
        actor_id=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
    )
    return Page.create([AuditLogRead.model_validate(a) for a in items], total, params)
