"""
LEGACYX — Project ORM Model.
"""

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class ProjectStatus(str, enum.Enum):
    """Lifecycle state of a project."""
    CREATED = "CREATED"
    INGESTING = "INGESTING"
    READY = "READY"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"


class Project(Base, TimestampMixin):
    """A legacy application project under analysis."""

    __tablename__ = "projects"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )

    # ── Ownership ──────────────────────────────────────────────────────────────
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Identity ───────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    # ── Status ─────────────────────────────────────────────────────────────────
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.CREATED,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="projects", lazy="noload"
    )
    repository: Mapped["Repository"] = relationship(  # noqa: F821
        "Repository", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id!r} name={self.name!r} status={self.status}>"
