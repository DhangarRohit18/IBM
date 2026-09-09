"""
LEGACYX — CodeRelationship ORM Model (Phase 3).

Represents a deterministic structural relationship between code constructs:
IMPORTS, EXTENDS, IMPLEMENTS, DEPENDS_ON, CALLS.

Source evidence is a first-class architectural concept (AGENTS.md & Phase 3 contract):
Every relationship retains relative file path, line number, source construct, evidence reason, and resolution flag.
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class RelationshipType(str, enum.Enum):
    """Type of structural code relationship."""
    IMPORTS = "IMPORTS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    DEPENDS_ON = "DEPENDS_ON"
    CALLS = "CALLS"


class CodeRelationship(Base):
    """A structural relationship between entities or methods."""

    __tablename__ = "code_relationships"

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
    source_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("code_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_method_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("code_methods.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("code_entities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # ── Target Identity & Relationship Type ────────────────────────────────────
    target_entity_name: Mapped[str] = mapped_column(String(512), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType, name="relationship_type"),
        nullable=False,
        index=True,
    )

    # ── First-Class Source Evidence (Mandatory Requirement) ────────────────────
    relative_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_construct: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    evidence_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # ── Resolution Accuracy Flag ───────────────────────────────────────────────
    # Conservative resolution: is_resolved=False when call target is ambiguous.
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Timestamp ──────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    analysis_run: Mapped["AnalysisRun"] = relationship(  # noqa: F821
        "AnalysisRun", back_populates="relationships"
    )

    __table_args__ = (
        Index("idx_code_rel_src_target", "source_entity_id", "target_entity_id"),
        Index("idx_code_rel_type", "analysis_id", "relationship_type"),
    )

    def __repr__(self) -> str:
        return f"<CodeRelationship {self.relationship_type.value} target={self.target_entity_name!r} line={self.line_number}>"
