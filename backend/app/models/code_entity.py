"""
LEGACYX — CodeEntity ORM Model (Phase 3).

Represents a Java top-level type construct (Class, Interface, Enum) discovered during static analysis.
All classifications store evidence string arrays (no confidence scores or percentages).
All entities retain exact file and line range evidence.
"""

import enum
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class EntityType(str, enum.Enum):
    """Type of Java type declaration."""
    CLASS = "CLASS"
    INTERFACE = "INTERFACE"
    ENUM = "ENUM"


class ComponentType(str, enum.Enum):
    """Evidence-backed classification of component role."""
    CONTROLLER = "CONTROLLER"
    SERVICE = "SERVICE"
    REPOSITORY = "REPOSITORY"
    MODEL = "MODEL"
    CONFIG = "CONFIG"
    UTILITY = "UTILITY"
    OTHER = "OTHER"


class CodeEntity(Base):
    """A Java class, interface, or enum entity."""

    __tablename__ = "code_entities"

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
    package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("code_packages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Identity & Classification ──────────────────────────────────────────────
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type"),
        nullable=False,
        default=EntityType.CLASS,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fully_qualified_name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # ── Source Evidence ────────────────────────────────────────────────────────
    relative_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_start: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # ── Type Hierarchy & Modifiers ─────────────────────────────────────────────
    extends_name: Mapped[str] = mapped_column(String(512), nullable=True)
    implements_names: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    annotations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    modifiers: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # ── Evidence-Backed Component Role ─────────────────────────────────────────
    component_type: Mapped[ComponentType] = mapped_column(
        Enum(ComponentType, name="component_type"),
        nullable=False,
        default=ComponentType.OTHER,
        index=True,
    )
    classification_evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # ── Timestamp ──────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    analysis_run: Mapped["AnalysisRun"] = relationship(  # noqa: F821
        "AnalysisRun", back_populates="entities"
    )
    package: Mapped["CodePackage"] = relationship(  # noqa: F821
        "CodePackage", back_populates="entities"
    )
    methods: Mapped[list["CodeMethod"]] = relationship(  # noqa: F821
        "CodeMethod", back_populates="entity", cascade="all, delete-orphan"
    )
    fields: Mapped[list["CodeField"]] = relationship(  # noqa: F821
        "CodeField", back_populates="entity", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_code_entity_fqn", "analysis_id", "fully_qualified_name"),
        Index("idx_code_entity_component", "analysis_id", "component_type"),
    )

    def __repr__(self) -> str:
        return f"<CodeEntity fqn={self.fully_qualified_name!r} type={self.component_type}>"
