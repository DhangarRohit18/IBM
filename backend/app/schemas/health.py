"""
LEGACYX — Health Check Schema.

All API responses use Pydantic schemas (AGENTS.md §9).
Raw ORM objects are never returned from routes.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of an individual infrastructure service."""
    name: str
    status: Literal["ok", "degraded", "unavailable"]
    message: str | None = None


class HealthResponse(BaseModel):
    """Response body for GET /api/v1/health."""
    status: Literal["ok", "degraded", "unavailable"]
    app_name: str
    app_version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    services: list[ServiceStatus] = Field(default_factory=list)
