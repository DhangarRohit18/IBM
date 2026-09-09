"""
LEGACYX — Structured Logging.

Uses structlog for machine-parseable JSON log output (AGENTS.md §9).
All log records are emitted as JSON in production.
Development mode emits coloured human-readable output.
"""

import logging
import sys
from typing import Any

import structlog

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure structlog and stdlib logging for the application.

    Must be called once at application startup (inside the lifespan hook).
    """
    settings = get_settings()
    is_dev = settings.is_development

    # ── structlog processors ───────────────────────────────────────────────────
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_dev:
        # Human-readable output in development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON output in staging/production
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ── stdlib logging integration ─────────────────────────────────────────────
    # Route stdlib log records (from uvicorn, sqlalchemy, etc.) through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Silence noisy loggers in development
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.is_development else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a named structlog logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("event_name", key="value")
    """
    return structlog.get_logger(name)
