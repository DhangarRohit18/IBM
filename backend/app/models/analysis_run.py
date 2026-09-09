"""
LEGACYX — AnalysisRun ORM Model (Phase 3).

Records execution metrics and audit outcomes of System X-Ray static analysis runs.
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class AnalysisRunStatus(str, enum.Enum):
    """Lifecycle state of an analysis run."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisRun(Base):
    """Audit and tracking record for a System X-Ray analysis execution."""

    __tablename__ = "analysis_runs"

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
    status: Mapped[AnalysisRunStatus] = mapped_column(
        Enum(AnalysisRunStatus, name="analysis_run_status"),
        nullable=False,
        default=AnalysisRunStatus.PENDING,
        index=True,
    )

    # ── Parser Version Info ───────────────────────────────────────────────────
    parser_name: Mapped[str] = mapped_column(String(64), nullable=False, default="javalang")
    parser_version: Mapped[str] = mapped_column(String(32), nullable=False, default="0.13.0")

    # ── Metrics ────────────────────────────────────────────────────────────────
    files_analyzed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    packages_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    classes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    interfaces_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enums_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    methods_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fields_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    relationships_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Error Info ─────────────────────────────────────────────────────────────
    error_code: Mapped[str] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

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

    # ── Relationships ──────────────────────────────────────────────────────────
    packages: Mapped[list["CodePackage"]] = relationship(  # noqa: F821
        "CodePackage", back_populates="analysis_run", cascade="all, delete-orphan"
    )
    entities: Mapped[list["CodeEntity"]] = relationship(  # noqa: F821
        "CodeEntity", back_populates="analysis_run", cascade="all, delete-orphan"
    )
    relationships: Mapped[list["CodeRelationship"]] = relationship(  # noqa: F821
        "CodeRelationship", back_populates="analysis_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AnalysisRun id={self.id!r} repo={self.repository_id!r} status={self.status}>"
