"""
LEGACYX — ValidationRun, ValidationEvidence & BehavioralScenario ORM Models (Phase 9).

Stores empirical execution evidence for modernized code artifacts including build compilation results,
unit test execution logs, and deterministic behavioral equivalence scenario comparisons between legacy
and modernized implementations.
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


class ValidationStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ENVIRONMENT_UNAVAILABLE = "ENVIRONMENT_UNAVAILABLE"
    REVIEWED = "REVIEWED"


class BuildStatus(str, enum.Enum):
    BUILD_PASS = "BUILD_PASS"
    BUILD_FAIL = "BUILD_FAIL"
    ENVIRONMENT_UNAVAILABLE = "ENVIRONMENT_UNAVAILABLE"
    NOT_RUN = "NOT_RUN"


class TestStatus(str, enum.Enum):
    TEST_PASS = "TEST_PASS"
    TEST_FAIL = "TEST_FAIL"
    ENVIRONMENT_UNAVAILABLE = "ENVIRONMENT_UNAVAILABLE"
    NOT_RUN = "NOT_RUN"


class BehaviorStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNABLE_TO_VALIDATE = "UNABLE_TO_VALIDATE"
    NOT_RUN = "NOT_RUN"


class ComparisonResult(str, enum.Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNABLE_TO_VALIDATE = "UNABLE_TO_VALIDATE"


class OverallStatus(str, enum.Enum):
    VALIDATED = "VALIDATED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    VALIDATION_BLOCKED = "VALIDATION_BLOCKED"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"


class ValidationRun(Base):
    """
    ValidationRun ORM Model.
    Represents an evidence-backed validation pipeline run for an approved Phase 8 transformation proposal.
    """
    __tablename__ = "validation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    transformation_proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transformation_proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modernization_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[ValidationStatus] = mapped_column(
        String(32), default=ValidationStatus.PROPOSED, nullable=False, index=True
    )
    environment_status: Mapped[str] = mapped_column(String(32), default="ENVIRONMENT_READY", nullable=False)
    build_status: Mapped[BuildStatus] = mapped_column(
        String(32), default=BuildStatus.NOT_RUN, nullable=False, index=True
    )
    test_status: Mapped[TestStatus] = mapped_column(
        String(32), default=TestStatus.NOT_RUN, nullable=False, index=True
    )
    behavioral_status: Mapped[BehaviorStatus] = mapped_column(
        String(32), default=BehaviorStatus.NOT_RUN, nullable=False, index=True
    )
    overall_status: Mapped[OverallStatus] = mapped_column(
        String(32), default=OverallStatus.VALIDATION_BLOCKED, nullable=False, index=True
    )

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

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
    evidences = relationship(
        "ValidationEvidence",
        backref="validation_run",
        cascade="all, delete-orphan",
        order_by="ValidationEvidence.created_at",
    )
    scenarios = relationship(
        "BehavioralScenario",
        backref="validation_run",
        cascade="all, delete-orphan",
        order_by="BehavioralScenario.created_at",
    )

    def __repr__(self) -> str:
        return f"<ValidationRun id='{self.id}' proposal='{self.transformation_proposal_id}' status='{self.overall_status}'>"


class ValidationEvidence(Base):
    """
    ValidationEvidence ORM Model.
    Stores raw subprocess execution logs, command strings, exit codes, and stdout/stderr streams.
    """
    __tablename__ = "validation_evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    stage: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # BUILD, UNIT_TEST, BEHAVIORAL_TEST
    command: Mapped[str] = mapped_column(Text, nullable=False)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<ValidationEvidence id='{self.id}' stage='{self.stage}' status='{self.status}'>"


class BehavioralScenario(Base):
    """
    BehavioralScenario ORM Model.
    Stores legacy vs modernized output comparisons grounded in authoritative Phase 4 BusinessRule records.
    """
    __tablename__ = "behavioral_scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_rule_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    scenario_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    legacy_output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    modernized_output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    comparison_result: Mapped[ComparisonResult] = mapped_column(
        String(32), default=ComparisonResult.UNABLE_TO_VALIDATE, nullable=False, index=True
    )
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<BehavioralScenario id='{self.id}' name='{self.scenario_name}' result='{self.comparison_result}'>"
