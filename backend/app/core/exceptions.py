"""Domain exception hierarchy and FastAPI handlers.

All errors are serialised to a consistent shape (PRD §10):
    { "detail": "...", "code": "...", "request_id": "..." }
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base class for expected, mappable application errors."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "bad_request"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.code
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthenticated"


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"


class PasswordChangeRequiredError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "password_change_required"


class RateLimitedError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"

    def __init__(self, detail: str | None = None, retry_after: int | None = None):
        super().__init__(detail)
        self.retry_after = retry_after


class NotImplementedYetError(AppError):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    code = "not_implemented"


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def _body(detail: str, code: str, request: Request) -> dict[str, str]:
    return {"detail": detail, "code": code, "request_id": _request_id(request)}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        headers = None
        retry_after = getattr(exc, "retry_after", None)
        if retry_after is not None:
            headers = {"Retry-After": str(retry_after)}
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.detail, exc.code, request),
            headers=headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(str(exc.detail), f"http_{exc.status_code}", request),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                **_body("Request validation failed", "validation_error", request),
                "errors": _jsonable_errors(exc.errors()),
            },
        )


def _jsonable_errors(errors: list) -> list:
    """Strip non-serialisable context (e.g. ValueError instances) from error detail."""
    cleaned = []
    for err in errors:
        err = dict(err)
        err.pop("ctx", None)
        cleaned.append(err)
    return cleaned
