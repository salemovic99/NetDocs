"""Attachment endpoints (PRD §10, §6.4): upload/list/download/delete."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.core import permissions as perms
from app.core import storage
from app.core.deps import CurrentUser, DbSession, RedisClient, require_permission
from app.schemas.attachment import AttachmentRead
from app.services.attachment_service import AttachmentService

router = APIRouter(tags=["attachments"])


@router.post(
    "/problems/{problem_id}/attachments",
    response_model=AttachmentRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_UPLOAD))],
)
async def upload_problem_attachment(
    problem_id: uuid.UUID,
    session: DbSession,
    redis: RedisClient,
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
) -> AttachmentRead:
    content = await file.read()
    attachment = await AttachmentService(session, redis).upload_to_problem(
        problem_id, file.filename or "file", file.content_type, content, actor_id=user.id
    )
    return AttachmentRead.model_validate(attachment)


@router.get(
    "/problems/{problem_id}/attachments",
    response_model=list[AttachmentRead],
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_DOWNLOAD))],
)
async def list_problem_attachments(
    problem_id: uuid.UUID, session: DbSession
) -> list[AttachmentRead]:
    items = await AttachmentService(session).list_for_problem(problem_id)
    return [AttachmentRead.model_validate(a) for a in items]


@router.post(
    "/devices/{device_id}/attachments",
    response_model=AttachmentRead,
    status_code=201,
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_UPLOAD))],
)
async def upload_device_attachment(
    device_id: uuid.UUID,
    session: DbSession,
    redis: RedisClient,
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
) -> AttachmentRead:
    content = await file.read()
    attachment = await AttachmentService(session, redis).upload_to_device(
        device_id, file.filename or "file", file.content_type, content, actor_id=user.id
    )
    return AttachmentRead.model_validate(attachment)


@router.get(
    "/devices/{device_id}/attachments",
    response_model=list[AttachmentRead],
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_DOWNLOAD))],
)
async def list_device_attachments(
    device_id: uuid.UUID, session: DbSession
) -> list[AttachmentRead]:
    items = await AttachmentService(session).list_for_device(device_id)
    return [AttachmentRead.model_validate(a) for a in items]


@router.get(
    "/attachments/{attachment_id}",
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_DOWNLOAD))],
)
async def download_attachment(
    attachment_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> StreamingResponse:
    attachment = await AttachmentService(session).prepare_download(
        attachment_id, actor_id=user.id
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{attachment.filename}"',
        "X-Content-Type-Options": "nosniff",
    }
    return StreamingResponse(
        storage.open_stream(attachment.storage_key),
        media_type=attachment.mime_type,
        headers=headers,
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=204,
    dependencies=[Depends(require_permission(perms.ATTACHMENTS_UPLOAD))],
)
async def delete_attachment(
    attachment_id: uuid.UUID, session: DbSession, user: CurrentUser
) -> None:
    await AttachmentService(session).delete(attachment_id, actor_id=user.id)
