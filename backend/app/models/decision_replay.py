"""
LEGACYX — Decision Replay & Silent Behavioral Drift Models (Features 3 & 4).

Stores replay session results comparing legacy vs modern system executions across
deterministic scenarios, detecting subtle drifts (threshold shifts, currency precision,
rounding, state transitions, exception handling) and tracing root causes back to source code.
"""

from datetime import datetime, timezone
import enum
from typing import Any
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ComparisonOutcome(str, enum.Enum):
    PRESERVED = "PRESERVED"
    BEHAVIOR_DRIFT = "BEHAVIOR_DRIFT"
    UNKNOWN = "UNKNOWN"


class DriftType(str, enum.Enum):
    NONE = "NONE"
    THRESHOLD_SHIFT = "THRESHOLD_SHIFT"
    ROUNDING_PRECISION = "ROUNDING_PRECISION"
    CURRENCY_CALCULATION = "CURRENCY_CALCULATION"
    ELIGIBILITY_RULE = "ELIGIBILITY_RULE"
    NULL_HANDLING = "NULL_HANDLING"
    EXCEPTION_MISMATCH = "EXCEPTION_MISMATCH"
    STATE_TRANSITION = "STATE_TRANSITION"
    ORDERING_DIFFERENCE = "ORDERING_DIFFERENCE"
    BOUNDARY_CONDITION = "BOUNDARY_CONDITION"


class DriftSeverity(str, enum.Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionReplayRun(Base):
    """
    Session container for a batch Decision Replay run comparing Legacy vs Modern implementations.
    """
    __tablename__ = "decision_replay_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    repository_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transformation_proposals.id", ondelete="SET NULL"), nullable=True, index=True
    )
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("validation_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False, index=True)
    total_scenarios: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    preserved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    drift_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unknown_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    risk_assessment: Mapped[str] = mapped_column(String(32), default="LOW", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    # Auditable metadata
    executed_by: Mapped[str] = mapped_column(String(128), default="system", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    repository = relationship("Repository", backref="replay_runs")
    results = relationship(
        "DecisionScenarioResult",
        backref="replay_run",
        cascade="all, delete-orphan",
        order_by="DecisionScenarioResult.scenario_number",
    )

    def __repr__(self) -> str:
        return f"<DecisionReplayRun id='{self.id}' preserved={self.preserved_count} drift={self.drift_count}>"


class DecisionScenarioResult(Base):
    """
    Granular comparison result for a single scenario executed against both Legacy and Modern systems.
    Captures exact outputs, rule paths, drift classification, and root cause evidence chain.
    """
    __tablename__ = "decision_scenario_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    replay_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("decision_replay_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    scenario_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # e.g. "SCEN-1042"
    scenario_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_category: Mapped[str] = mapped_column(String(64), default="BOUNDARY_THRESHOLD", nullable=False)

    contract_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    business_rule_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)

    # Input Scenario
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Legacy Execution Output
    legacy_decision: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "MANUAL_REVIEW"
    legacy_output: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    legacy_rule_path: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    legacy_execution_time_ms: Mapped[int] = mapped_column(Integer, default=12, nullable=False)

    # Modern Execution Output
    modern_decision: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "APPROVE"
    modern_output: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    modern_rule_path: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    modern_execution_time_ms: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Comparison & Drift Analysis
    comparison_status: Mapped[ComparisonOutcome] = mapped_column(
        String(32), default=ComparisonOutcome.PRESERVED, nullable=False, index=True
    )
    drift_type: Mapped[DriftType] = mapped_column(String(32), default=DriftType.NONE, nullable=False, index=True)
    drift_severity: Mapped[DriftSeverity] = mapped_column(
        String(32), default=DriftSeverity.NONE, nullable=False, index=True
    )
    drift_details: Mapped[str] = mapped_column(Text, nullable=True)

    # Root Cause Trace (Decision → Rule → Method → Changed Code → Dependency)
    drift_root_cause: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    remediation_suggestion: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_chain: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Human Review
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<DecisionScenarioResult id='{self.id}' scenario='{self.scenario_id}' status='{self.comparison_status}'>"
