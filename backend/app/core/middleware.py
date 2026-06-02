"""HTTP middleware: security headers + rate limiting (PRD §7, §12)."""

import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core import ratelimit, security
from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger("netdocs.middleware")

_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
_LOGIN_PATH = "/api/v1/auth/login"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Defense-in-depth headers (primary set is at the reverse proxy, §12)."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if settings.environment == "prod":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Login limited per IP; other mutating /api/v1 calls limited per user."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path
        window = settings.rate_limit_window_seconds
        redis = get_redis()
        key: str | None = None
        limit = 0

        if path == _LOGIN_PATH and request.method == "POST":
            ip = request.client.host if request.client else "unknown"
            key, limit = f"login:ip:{ip}", settings.rate_limit_login_ip
        elif request.method in _MUTATING and path.startswith("/api/v1"):
            subject = self._subject_from_bearer(request)
            if subject:
                key, limit = f"write:user:{subject}", settings.rate_limit_write_user

        if key:
            allowed, retry_after = await ratelimit.hit(redis, key, limit, window)
            if not allowed:
                request_id = getattr(request.state, "request_id", "-")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded",
                        "code": "rate_limited",
                        "request_id": request_id,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
        return await call_next(request)

    @staticmethod
    def _subject_from_bearer(request: Request) -> str | None:
        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            return None
        try:
            claims = security.decode_token(auth.split(" ", 1)[1])
            return claims.get("sub")
        except security.JWTError:
            return None
