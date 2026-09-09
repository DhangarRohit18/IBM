"""
LEGACYX — CodePackage ORM Model (Phase 3).

Represents a Java package (e.g. com.legacybank.service) discovered in an analysis run.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class CodePackage(Base):
    """A Java package discovered during static analysis."""

    __tablename__ = "code_packages"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Foreign Keys ───────────────────────────────────────────────────────────
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    repository_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Attributes ─────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── Timestamp ──────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    analysis_run: Mapped["AnalysisRun"] = relationship(  # noqa: F821
        "AnalysisRun", back_populates="packages"
    )
    entities: Mapped[list["CodeEntity"]] = relationship(  # noqa: F821
        "CodeEntity", back_populates="package", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_code_pkg_analysis_name", "analysis_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<CodePackage name={self.name!r}>"
