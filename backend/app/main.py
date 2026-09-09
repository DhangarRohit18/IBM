"""
LEGACYX — FastAPI Application Factory.

This module creates and configures the FastAPI application.
It is the entry point for the ASGI server (uvicorn).

Responsibilities:
  - Application creation and metadata
  - Lifespan events (startup / shutdown)
  - Middleware configuration (CORS)
  - Router registration
  - Global exception handlers

Layer: API / Orchestration (AGENTS.md §1.3)
  - Does not contain business logic.
  - Does not call AI providers.
  - Does not access the database directly.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.init_db import check_db_connection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    # ── Startup ────────────────────────────────────────────────────────────────
    configure_logging()
    logger = get_logger(__name__)
    logger.info(
        "legacyx_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    # Fail fast if database is unreachable
    await check_db_connection()
    logger.info("legacyx_ready")

    yield  # Application is running

    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("legacyx_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="LEGACYX",
        description=(
            "Legacy Application Modernization & Behavioral Validation Platform. "
            "DISCOVER → UNDERSTAND → DECIDE → CHANGE → VERIFY."
        ),
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Global Exception Handlers ──────────────────────────────────────────────
    # Internal stack traces must never be exposed to the frontend (AGENTS.md §9)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger = get_logger(__name__)
        logger.error(
            "unhandled_exception",
            path=str(request.url),
            method=request.method,
            error=str(exc),
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "An internal error occurred."},
        )

    return app


# ── ASGI application instance ──────────────────────────────────────────────────
app = create_app()
