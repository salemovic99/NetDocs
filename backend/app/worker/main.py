"""AV-scan + maintenance worker (PRD §8).

Consumes the `av:scan` Redis queue, runs each attachment through ClamAV, and
updates its `av_status`. Also periodically cleans orphaned files (on disk with no
DB row) and re-enqueues attachments stuck in `pending`.

Run: `python -m app.worker.main`
"""

import asyncio
import io
import logging
import os
import uuid

from redis.asyncio import Redis
from sqlalchemy import select

from app.core import storage
from app.core.config import settings
from app.core.database import SessionFactory
from app.core.logging import configure_logging
from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository
from app.services.attachment_service import AV_SCAN_QUEUE

logger = logging.getLogger("netdocs.worker")

CLEANUP_INTERVAL_SECONDS = 3600


def _scan_bytes(content: bytes) -> str:
    """Return 'clean' or 'infected'. Best-effort: on scanner error, leave pending."""
    try:
        import clamd
    except ImportError:  # pragma: no cover
        logger.warning("clamd not installed; cannot scan")
        return "pending"
    try:
        client = clamd.ClamdNetworkSocket(
            host=settings.clamav_host, port=settings.clamav_port, timeout=30
        )
        result = client.instream(io.BytesIO(content))
        status = result.get("stream", ("ERROR",))[0]
        return "clean" if status == "OK" else "infected"
    except Exception:  # pragma: no cover - scanner unreachable
        logger.warning("ClamAV scan failed; leaving pending", exc_info=True)
        return "pending"


async def _scan_attachment(attachment_id: uuid.UUID) -> None:
    async with SessionFactory() as session:
        attachment = await session.get(Attachment, attachment_id)
        if attachment is None or attachment.av_status != "pending":
            return
        if not storage.exists(attachment.storage_key):
            logger.warning("attachment %s missing on disk", attachment_id)
            return
        content = b"".join(storage.open_stream(attachment.storage_key))
        status = await asyncio.to_thread(_scan_bytes, content)
        if status == "pending":
            return  # scanner unavailable; will be retried by the cleanup sweep
        attachment.av_status = status
        await session.commit()
        logger.info("scanned attachment %s -> %s", attachment_id, status)


async def _cleanup_orphans() -> None:
    """Delete files on disk that have no matching attachment row."""
    async with SessionFactory() as session:
        keys = await AttachmentRepository(session).all_storage_keys()
    root = settings.upload_dir
    if not os.path.isdir(root):
        return
    removed = 0
    for dirpath, _dirs, filenames in os.walk(root):
        for name in filenames:
            if name not in keys:
                try:
                    os.remove(os.path.join(dirpath, name))
                    removed += 1
                except OSError:
                    pass
    if removed:
        logger.info("orphan cleanup removed %d files", removed)


async def _requeue_pending(redis: Redis) -> None:
    """Re-enqueue attachments still pending (e.g. scanner was down)."""
    async with SessionFactory() as session:
        stmt = select(Attachment.id).where(Attachment.av_status == "pending")
        ids = (await session.execute(stmt)).scalars().all()
    for aid in ids:
        await redis.lpush(AV_SCAN_QUEUE, str(aid))
    if ids:
        logger.info("re-enqueued %d pending attachments", len(ids))


async def _periodic_maintenance(redis: Redis) -> None:
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        try:
            await _cleanup_orphans()
            await _requeue_pending(redis)
        except Exception:  # pragma: no cover
            logger.warning("maintenance pass failed", exc_info=True)


async def run() -> None:
    configure_logging()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    logger.info("worker started; consuming %s", AV_SCAN_QUEUE)
    asyncio.create_task(_periodic_maintenance(redis))
    while True:
        try:
            item = await redis.brpop(AV_SCAN_QUEUE, timeout=5)
            if item is None:
                continue
            _, raw_id = item
            await _scan_attachment(uuid.UUID(raw_id))
        except asyncio.CancelledError:  # pragma: no cover
            break
        except Exception:  # pragma: no cover
            logger.warning("scan loop error", exc_info=True)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run())
