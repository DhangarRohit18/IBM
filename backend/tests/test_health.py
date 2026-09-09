"""
LEGACYX — Health Endpoint Tests.

Phase 1 acceptance criteria (IMPLEMENTATION_PLAN.md):
  - Backend: health endpoint returns 200
  - Backend: response includes service status
  - Backend: response schema matches HealthResponse

Note: These tests run against the actual database and Redis when run inside
Docker Compose (docker compose exec backend pytest). When run locally without
the full stack, the health status for postgres/redis will be 'unavailable'
but the endpoint itself must still return 200 with a valid HealthResponse.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(async_client: AsyncClient) -> None:
    """Health endpoint must return HTTP 200 regardless of dependency status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_has_required_fields(async_client: AsyncClient) -> None:
    """Health response body must contain all required fields."""
    response = await async_client.get("/api/v1/health")
    body = response.json()

    assert "status" in body
    assert "app_name" in body
    assert "app_version" in body
    assert "environment" in body
    assert "timestamp" in body
    assert "services" in body
    assert isinstance(body["services"], list)


@pytest.mark.asyncio
async def test_health_status_is_valid(async_client: AsyncClient) -> None:
    """Health status must be one of the defined values."""
    response = await async_client.get("/api/v1/health")
    body = response.json()

    assert body["status"] in ("ok", "degraded", "unavailable")


@pytest.mark.asyncio
async def test_health_app_name(async_client: AsyncClient) -> None:
    """Health response must identify LEGACYX as the app name."""
    response = await async_client.get("/api/v1/health")
    body = response.json()

    assert body["app_name"] == "LEGACYX"


@pytest.mark.asyncio
async def test_health_services_have_required_fields(async_client: AsyncClient) -> None:
    """Each service status in the health response must have name and status."""
    response = await async_client.get("/api/v1/health")
    body = response.json()

    for service in body["services"]:
        assert "name" in service
        assert "status" in service
        assert service["status"] in ("ok", "degraded", "unavailable")
