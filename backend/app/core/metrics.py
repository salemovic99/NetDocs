"""Prometheus metrics (PRD §13): request rate/latency/errors + middleware."""

from collections.abc import Awaitable, Callable

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUESTS = Counter(
    "netdocs_http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)
LATENCY = Histogram(
    "netdocs_http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "route"],
)


def _route_template(request: Request) -> str:
    """Use the matched route path template to keep label cardinality bounded."""
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        with LATENCY.labels(request.method, _route_template(request)).time():
            response = await call_next(request)
        REQUESTS.labels(
            request.method, _route_template(request), str(response.status_code)
        ).inc()
        return response


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
