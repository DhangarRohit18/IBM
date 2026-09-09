"""
LEGACYX — Health Check Router.

Endpoint: GET /api/v1/health

Returns the status of the application and its infrastructure dependencies
(PostgreSQL, Redis). This is the only implemented endpoint in Phase 1.

Layer: API / Orchestration (AGENTS.md §1.3)
  - Input validation: none required (GET, no params)
  - Calls: db layer, redis client
  - Response: HealthResponse schema only — no raw objects
"""

from datetime import datetime, timezone

import redis.asyncio as aioredis
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.base import async_engine
from app.schemas.health import HealthResponse, ServiceStatus

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the operational status of the LEGACYX backend and its "
        "infrastructure dependencies (PostgreSQL, Redis)."
    ),
    tags=["health"],
)
async def health_check() -> HealthResponse:
    """Check application health and connectivity to all dependencies."""
    services: list[ServiceStatus] = []
    overall_ok = True

    # ── PostgreSQL ─────────────────────────────────────────────────────────────
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        services.append(ServiceStatus(name="postgresql", status="ok"))
    except Exception as exc:
        logger.error("health_check_postgres_failed", error=str(exc))
        services.append(
            ServiceStatus(name="postgresql", status="unavailable", message=str(exc))
        )
        overall_ok = False

    # ── Redis ──────────────────────────────────────────────────────────────────
    try:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        await redis_client.aclose()
        services.append(ServiceStatus(name="redis", status="ok"))
    except Exception as exc:
        logger.error("health_check_redis_failed", error=str(exc))
        services.append(
            ServiceStatus(name="redis", status="unavailable", message=str(exc))
        )
        overall_ok = False

    status = "ok" if overall_ok else "degraded"

    logger.info("health_check_complete", status=status)

    return HealthResponse(
        status=status,
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(tz=timezone.utc),
        services=services,
    )
