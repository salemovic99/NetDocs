"""Structured JSON logging + request-id correlation middleware (PRD §13)."""

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "level": record.levelname,
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "actor_id", "route", "latency_ms", "status_code"):
            if (value := getattr(record, key, None)) is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


access_logger = logging.getLogger("netdocs.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign a request_id, time the request, and emit a structured access log."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        access_logger.info(
            "request",
            extra={
                "request_id": request_id,
                "route": f"{request.method} {request.url.path}",
                "latency_ms": latency_ms,
                "status_code": response.status_code,
            },
        )
        return response
