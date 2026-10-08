"""
ClaimGraph AI — Common schemas used across modules.

Provides standardized response wrappers, pagination, and base schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with strict configuration for all API models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response wrapper."""

    success: bool = True
    data: T
    message: str = "OK"


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    success: bool = True
    data: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorDetail(BaseModel):
    """Error detail block inside error responses."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standardized error response wrapper."""

    success: bool = False
    error: ErrorDetail


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class TimestampSchema(BaseSchema):
    """Schema mixin for created_at / updated_at."""

    created_at: datetime
    updated_at: datetime
