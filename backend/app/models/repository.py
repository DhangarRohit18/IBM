"""
LEGACYX — Repository ORM Model (Phase 2).
"""

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class RepositoryStatus(str, enum.Enum):
    """Lifecycle state of repository ingestion."""
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    EXTRACTING = "EXTRACTING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Repository(Base, TimestampMixin):
    """A legacy application source code repository artifact."""

    __tablename__ = "repositories"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Foreign Key ────────────────────────────────────────────────────────────
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Metadata ───────────────────────────────────────────────────────────────
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    extracted_path: Mapped[str] = mapped_column(String(512), nullable=True)

    # ── Status ─────────────────────────────────────────────────────────────────
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(RepositoryStatus, name="repository_status"),
        nullable=False,
        default=RepositoryStatus.UPLOADED,
        index=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project", back_populates="repository"
    )
    files: Mapped[list["RepositoryFile"]] = relationship(  # noqa: F821
        "RepositoryFile", back_populates="repository", cascade="all, delete-orphan"
    )
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(  # noqa: F821
        "IngestionRun", back_populates="repository", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Repository id={self.id!r} project_id={self.project_id!r} status={self.status}>"
