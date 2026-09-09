"""
LEGACYX — IngestionRun ORM Model (Phase 2).
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class IngestionStatus(str, enum.Enum):
    """Execution status of an ingestion run."""
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IngestionRun(Base):
    """Audit record for a repository ingestion execution."""

    __tablename__ = "ingestion_runs"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Foreign Key ────────────────────────────────────────────────────────────
    repository_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Status ─────────────────────────────────────────────────────────────────
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, name="ingestion_status"),
        nullable=False,
        default=IngestionStatus.STARTED,
        index=True,
    )

    # ── Timestamps ─────────────────────────────────────────────────────────────
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Metrics ────────────────────────────────────────────────────────────────
    files_discovered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    directories_discovered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bytes_extracted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Error Details ──────────────────────────────────────────────────────────
    error_code: Mapped[str] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────────
    repository: Mapped["Repository"] = relationship(  # noqa: F821
        "Repository", back_populates="ingestion_runs"
    )

    def __repr__(self) -> str:
        return f"<IngestionRun id={self.id!r} repo={self.repository_id!r} status={self.status}>"
