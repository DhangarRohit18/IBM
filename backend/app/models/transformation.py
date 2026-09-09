"""
LEGACYX — TransformationProposal & TransformationArtifact ORM Models (Phase 8).

Stores evidence-grounded code transformation proposals, artifact specifications,
git-style unified diffs, preserved business rule mappings, human review workflows,
and isolated storage file references.
"""

from datetime import datetime, timezone
import enum
from typing import Any
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TransformationStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"


class ArtifactCategory(str, enum.Enum):
    EXTRACTED_CLASS = "EXTRACTED_CLASS"
    EXTRACTED_INTERFACE = "EXTRACTED_INTERFACE"
    FACADE = "FACADE"
    ADAPTER = "ADAPTER"
    REFACTORED_METHOD = "REFACTORED_METHOD"
    MIGRATED_CALLER = "MIGRATED_CALLER"
    SUPPORTING_TEST_STUB = "SUPPORTING_TEST_STUB"


class TransformationProposal(Base):
    """
    TransformationProposal ORM Model.
    Represents an evidence-backed candidate code transformation for an approved Phase 7 plan task.
    """
    __tablename__ = "transformation_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modernization_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modernization_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[TransformationStatus] = mapped_column(
        String(32), default=TransformationStatus.PROPOSED, nullable=False, index=True
    )
    transformation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Deterministic Specification & Evidence
    specification: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rule_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    impacted_entity_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Auditable Human Review Workflow
    reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Isolated Storage Application Info
    applied_by: Mapped[str] = mapped_column(String(128), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    storage_workspace_path: Mapped[str] = mapped_column(String(512), nullable=True)

    # AI Code Proposal Context
    ai_proposal_status: Mapped[str] = mapped_column(String(32), default="NOT_REQUESTED", nullable=False)
    ai_proposal_summary: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    artifacts = relationship(
        "TransformationArtifact",
        backref="proposal",
        cascade="all, delete-orphan",
        order_by="TransformationArtifact.created_at",
    )

    def __repr__(self) -> str:
        return f"<TransformationProposal id='{self.id}' task_id='{self.task_id}' type='{self.transformation_type}' status='{self.status}'>"


class TransformationArtifact(Base):
    """
    TransformationArtifact ORM Model.
    Represents an individual generated target code file (class, interface, facade, caller update, or test stub).
    """
    __tablename__ = "transformation_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transformation_proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )

    artifact_category: Mapped[ArtifactCategory] = mapped_column(String(64), nullable=False, index=True)
    target_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    source_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    source_line_start: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_line_end: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    generated_code: Mapped[str] = mapped_column(Text, nullable=False)
    diff_content: Mapped[str] = mapped_column(Text, nullable=False)

    rules_preserved: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    evidence_references: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    storage_relative_path: Mapped[str] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<TransformationArtifact id='{self.id}' category='{self.artifact_category}' file='{self.target_file_path}'>"
