"""
LEGACYX — RepositoryFile ORM Model (Phase 2).
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class RepositoryFile(Base):
    """An individual file or folder inside an ingested repository."""

    __tablename__ = "repository_files"

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

    # ── File Attributes ────────────────────────────────────────────────────────
    relative_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_directory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)

    # ── Timestamp ──────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    repository: Mapped["Repository"] = relationship(  # noqa: F821
        "Repository", back_populates="files"
    )

    __table_args__ = (
        Index("idx_repo_file_repo_relpath", "repository_id", "relative_path"),
        Index("idx_repo_file_extension", "extension"),
    )

    def __repr__(self) -> str:
        return f"<RepositoryFile path={self.relative_path!r} size={self.size_bytes}>"
