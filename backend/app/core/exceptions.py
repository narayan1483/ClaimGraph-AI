"""
ClaimGraph AI — Global Exception Handling.

Provides a unified error response format and FastAPI exception handlers.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Domain Exception Hierarchy ───────────────────────────────────────

class ClaimGraphError(Exception):
    """Base exception for all ClaimGraph business errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ClaimGraphError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = "") -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class ConflictError(ClaimGraphError):
    """Resource already exists or state conflict."""

    def __init__(self, message: str = "Resource conflict.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
        )


class ForbiddenError(ClaimGraphError):
    """Insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class UnauthorizedError(ClaimGraphError):
    """Authentication required or invalid credentials."""

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ValidationError(ClaimGraphError):
    """Business-level validation error."""

    def __init__(self, message: str = "Validation error.", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ServiceUnavailableError(ClaimGraphError):
    """External service is down or unreachable."""

    def __init__(self, service: str = "External service") -> None:
        super().__init__(
            message=f"{service} is currently unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
        )


# ── Error Response Builder ──────────────────────────────────────────

def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


# ── Register Handlers ───────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(ClaimGraphError)
    async def claimgraph_error_handler(_req: Request, exc: ClaimGraphError) -> JSONResponse:
        logger.warning(
            "domain_error",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return _error_response(exc.status_code, exc.error_code, exc.message, exc.details)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_req: Request, exc: HTTPException) -> JSONResponse:
        return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_req: Request, exc: RequestValidationError) -> JSONResponse:
        details = {"errors": exc.errors()}
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Request validation failed.",
            details,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_req: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected internal error occurred.",
        )
