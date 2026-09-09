"""
LEGACYX — Common Response Schemas.

Shared Pydantic models used across multiple API endpoints.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """Generic envelope for successful API responses.

    Usage:
        return ApiResponse(data=my_result)
    """
    success: bool = True
    data: DataT


class ErrorDetail(BaseModel):
    """Single field-level validation error."""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response body.

    Internal stack traces are never included (AGENTS.md §9).
    """
    success: bool = False
    error: str
    details: list[ErrorDetail] | None = None


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""
    total: int
    page: int
    page_size: int
    total_pages: int
