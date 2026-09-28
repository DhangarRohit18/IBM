"""
LEGACYX — Business Rule ORM Model (Phase 4).

Represents a deterministically extracted business rule candidate with line evidence,
deterministic rule trace, review status, and optional AI explanation.
"""

from datetime import datetime, timezone
import enum
from typing import Any
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RuleType(str, enum.Enum):
    VALIDATION = "VALIDATION"
    CONDITIONAL = "CONDITIONAL"
    THRESHOLD = "THRESHOLD"
    CALCULATION = "CALCULATION"
    ACTION = "ACTION"
    STATE_TRANSITION = "STATE_TRANSITION"


class RuleStatus(str, enum.Enum):
    EXTRACTED = "EXTRACTED"
    EXPLAINED = "EXPLAINED"
    REVIEWED = "REVIEWED"
    REJECTED = "REJECTED"


class AIExplanationStatus(str, enum.Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def generate_uuid() -> str:
    return str(uuid.uuid4())


class BusinessRule(Base):
    """
    BusinessRule ORM model.
    Stores authoritative deterministic facts, source evidence, and optional AI explanation.
    """
    __tablename__ = "business_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("code_entities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    method_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("code_methods.id", ondelete="SET NULL"), nullable=True, index=True
    )

    rule_type: Mapped[RuleType] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[RuleStatus] = mapped_column(String(32), default=RuleStatus.EXTRACTED, nullable=False, index=True)

    # Deterministic Facts
    condition_expression: Mapped[str] = mapped_column(Text, nullable=True)
    action_expression: Mapped[str] = mapped_column(Text, nullable=True)
    outcome_expression: Mapped[str] = mapped_column(Text, nullable=True)
    threshold_value: Mapped[str] = mapped_column(String(128), nullable=True)
    threshold_operator: Mapped[str] = mapped_column(String(16), nullable=True)
    calculation_formula: Mapped[str] = mapped_column(Text, nullable=True)
    previous_state: Mapped[str] = mapped_column(String(128), nullable=True)  # UNKNOWN/None unless proven
    new_state: Mapped[str] = mapped_column(String(128), nullable=True)

    # Deterministic Rule Trace (Condition -> Decision/Context -> Action -> State Change)
    rule_trace: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    # Source Evidence
    relative_file_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    line_start: Mapped[int] = mapped_column(Integer, nullable=False)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False)
    source_construct: Mapped[str] = mapped_column(String(128), nullable=False)
    extraction_reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Business Rule DNA (Feature 1)
    business_meaning: Mapped[str] = mapped_column(Text, nullable=True)
    inputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    outputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_apis: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_db_fields: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_business_processes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_tests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_snippet: Mapped[str] = mapped_column(Text, nullable=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Optional AI Explanation (Stored separately from facts)
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    ai_explanation_status: Mapped[AIExplanationStatus] = mapped_column(
        String(32), default=AIExplanationStatus.NOT_REQUESTED, nullable=False
    )

    # Review Audit Trail
    reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run = relationship("AnalysisRun", backref="business_rules")
    repository = relationship("Repository", backref="business_rules")
    entity = relationship("CodeEntity", backref="business_rules")
    method = relationship("CodeMethod", backref="business_rules")

    def __repr__(self) -> str:
        return f"<BusinessRule id='{self.id}' type='{self.rule_type}' title='{self.title}' status='{self.status}'>"
