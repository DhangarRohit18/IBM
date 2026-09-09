"""
LEGACYX — ModernizationPlan & ModernizationTask ORM Models (Phase 7).

Stores evidence-backed modernization execution plans, topologically ordered tasks,
prerequisite dependencies, evidence references, rules-to-preserve mappings,
impact surfaces, verification checkpoints, and auditable human review history.
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


class PlanStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"
    SKIPPED = "SKIPPED"


class TaskType(str, enum.Enum):
    EXTRACT_RESPONSIBILITY = "EXTRACT_RESPONSIBILITY"
    SEPARATE_BUSINESS_RULE = "SEPARATE_BUSINESS_RULE"
    EXTRACT_CALCULATION = "EXTRACT_CALCULATION"
    ISOLATE_PERSISTENCE = "ISOLATE_PERSISTENCE"
    ISOLATE_STATE_TRANSITION = "ISOLATE_STATE_TRANSITION"
    ISOLATE_EXTERNAL_NOTIFICATION = "ISOLATE_EXTERNAL_NOTIFICATION"
    DEFINE_INTERFACE = "DEFINE_INTERFACE"
    INTRODUCE_ADAPTER = "INTRODUCE_ADAPTER"
    INTRODUCE_FACADE = "INTRODUCE_FACADE"
    REDUCE_DEPENDENCY = "REDUCE_DEPENDENCY"
    SPLIT_COMPONENT = "SPLIT_COMPONENT"
    MIGRATE_CALLER = "MIGRATE_CALLER"
    PRESERVE_BEHAVIOR = "PRESERVE_BEHAVIOR"
    ADD_VERIFICATION_CHECKPOINT = "ADD_VERIFICATION_CHECKPOINT"


class ModernizationPlan(Base):
    """
    ModernizationPlan ORM Model.
    Represents an evidence-backed execution plan for modernizing a legacy component.
    """
    __tablename__ = "modernization_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("code_entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    strategy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modernization_strategies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relative_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    strategy_type: Mapped[str] = mapped_column(String(64), nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        String(32), default=PlanStatus.PROPOSED, nullable=False, index=True
    )

    # Deterministic Maps & Catalogs
    rules_to_preserve: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    impact_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_checkpoints: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    # Auditable Human Review Workflow
    reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # AI Gateway Explanation
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    ai_explanation_status: Mapped[str] = mapped_column(String(32), default="NOT_REQUESTED", nullable=False)

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
    tasks = relationship("ModernizationTask", backref="plan", cascade="all, delete-orphan", order_by="ModernizationTask.sequence_order")

    def __repr__(self) -> str:
        return f"<ModernizationPlan id='{self.id}' entity='{self.entity_name}' strategy='{self.strategy_type}' status='{self.status}'>"


class ModernizationTask(Base):
    """
    ModernizationTask ORM Model.
    Represents an individual step in an execution plan with full evidence traceability.
    """
    __tablename__ = "modernization_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modernization_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[TaskType] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(
        String(32), default=TaskStatus.PENDING, nullable=False, index=True
    )

    target_component: Mapped[str] = mapped_column(String(255), nullable=False)
    target_file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # Traceability & Graph References
    depends_on_task_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    rule_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    evidence_references: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    verification_checkpoint: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

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
        return f"<ModernizationTask id='{self.id}' seq={self.sequence_order} type='{self.task_type}' status='{self.status}'>"
