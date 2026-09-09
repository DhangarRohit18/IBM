"""
LEGACYX — ORM Base Model.

Provides a declarative base and a TimestampMixin used by all models.
All ORM models must inherit from Base and include TimestampMixin.

Design rules (AGENTS.md §1.3):
  - Models contain no business logic.
  - Models are pure schema definitions.
  - All datetime fields are timezone-aware UTC.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all LEGACYX ORM models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at to any model.

    created_at — set once at INSERT, never changes.
    updated_at — set at INSERT and updated at every UPDATE.
    Both are stored as UTC timestamps.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def generate_uuid() -> str:
    """Generate a new UUID4 string. Used as default for PK columns."""
    return str(uuid.uuid4())
