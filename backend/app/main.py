"""FastAPI application factory and entrypoint (PRD §8)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import RequestContextMiddleware, configure_logging
from app.core.metrics import MetricsMiddleware
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.core.redis import close_redis
from app.db.seed import bootstrap_admin

logger = __import__("logging").getLogger("netdocs.startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    try:
        await bootstrap_admin()
    except Exception:  # pragma: no cover - never block startup on bootstrap
        logger.warning("bootstrap admin step failed", exc_info=True)
    yield
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="NetDocs API",
        version="0.2.0",
        description="Network & IT Problems Documentation Platform — backend API.",
        lifespan=lifespan,
    )

    # Middleware: the LAST added runs OUTERMOST. We want request_id assigned first,
    # then security headers, then rate limiting, then CORS, then the app.
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["ETag", "X-Request-ID"],
        )
    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)
    if settings.security_headers_enabled:
        app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router)  # /healthz, /readyz, /metrics (unversioned)
    app.include_router(api_router)
    return app


app = create_app()
