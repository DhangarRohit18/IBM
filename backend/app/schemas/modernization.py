"""
LEGACYX — Modernization Strategy Schemas (Phase 6).

Pydantic models for Phase 6 Modernization Strategy endpoints.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResponsibilityItemResponse(BaseModel):
    category: str
    title: str
    description: str
    relative_file_path: str
    line_number: int
    evidence_reason: str
    source_snippet: str


class RulePreservationItemResponse(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    rule_type: Optional[str] = None
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    condition: Optional[str] = None


class DecisionTraceStepResponse(BaseModel):
    step: int
    label: str
    detail: str


class QualitativeComparisonItemResponse(BaseModel):
    dimension: str
    recommended_value: str
    alternative_value: str


class StrategyImpactSummaryResponse(BaseModel):
    direct_dependent_count: int
    transitive_dependent_count: int
    direct_dependents: list[str] = []
    transitive_dependents: list[str] = []


class ModernizationStrategyResponse(BaseModel):
    """Response model for a component modernization strategy."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    repository_id: str
    entity_id: str
    entity_name: str
    relative_file_path: str

    recommended_strategy: str
    alternative_strategy: Optional[str] = None

    why_recommended: str
    why_alternative: Optional[str] = None
    what_not_to_change: Optional[str] = None

    decision_trace: list[DecisionTraceStepResponse] = []
    observed_responsibilities: list[ResponsibilityItemResponse] = []
    rules_to_preserve: list[RulePreservationItemResponse] = []
    impact_summary: StrategyImpactSummaryResponse
    qualitative_comparison: list[QualitativeComparisonItemResponse] = []

    status: str
    user_override_strategy: Optional[str] = None
    user_override_by: Optional[str] = None
    user_override_at: Optional[datetime] = None
    user_override_notes: Optional[str] = None

    ai_explanation: Optional[str] = None
    ai_explanation_status: str

    created_at: datetime
    updated_at: datetime


class StrategyOverrideRequest(BaseModel):
    status: str = Field(..., description="Target status: REVIEWED or OVERRIDDEN")
    user_override_strategy: Optional[str] = Field(None, description="New strategy if status is OVERRIDDEN")
    user_name: str = Field("engineer", description="Name/ID of user making override")
    notes: Optional[str] = Field(None, description="Auditable rationale for override")


class StrategyExplainResponse(BaseModel):
    explanation: str
    status: str


# ==========================================
# Phase 7 — Execution Plan Schemas
# ==========================================

class ModernizationTaskResponse(BaseModel):
    """Response model for an individual modernization execution task."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    sequence_order: int
    title: str
    description: str
    task_type: str
    status: str
    target_component: str
    target_file_path: str

    depends_on_task_ids: list[str] = []
    rule_ids: list[str] = []
    evidence_references: list[dict[str, Any]] = []
    verification_checkpoint: dict[str, Any] = {}

    created_at: datetime
    updated_at: datetime


class ModernizationPlanResponse(BaseModel):
    """Response model for a modernization execution plan."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    repository_id: str
    entity_id: str
    strategy_id: Optional[str] = None
    entity_name: str
    relative_file_path: str
    strategy_type: str
    summary: str
    status: str

    rules_to_preserve: list[dict[str, Any]] = []
    impact_summary: dict[str, Any] = {}
    verification_checkpoints: list[dict[str, Any]] = []

    tasks: list[ModernizationTaskResponse] = []

    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    ai_explanation: Optional[str] = None
    ai_explanation_status: str

    created_at: datetime
    updated_at: datetime


class PlanReviewRequest(BaseModel):
    status: str = Field(..., description="Target status: REVIEWED, APPROVED, or REJECTED")
    user_name: str = Field("architect", description="Name/ID of reviewing architect")
    notes: Optional[str] = Field(None, description="Review feedback notes")


class TaskStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Task status: PENDING, IN_PROGRESS, COMPLETED, DEFERRED, SKIPPED")


class TaskReorderRequest(BaseModel):
    new_sequence_order: int = Field(..., ge=1, description="New 1-based sequence order")


class PlanExplainResponse(BaseModel):
    explanation: str
    status: str


# ==========================================
# Phase 8 — Code Transformation Schemas
# ==========================================

class TransformationArtifactResponse(BaseModel):
    """Response model for a generated target code artifact."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    artifact_category: str
    target_file_path: str
    source_file_path: str
    source_line_start: int
    source_line_end: int
    generated_code: str
    diff_content: str
    rules_preserved: list[dict[str, Any]] = []
    evidence_references: list[dict[str, Any]] = []
    storage_relative_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TransformationProposalResponse(BaseModel):
    """Response model for a transformation proposal."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    task_id: str
    analysis_id: str
    repository_id: str
    status: str
    transformation_type: str
    target_entity: str
    summary: str
    specification: dict[str, Any] = {}
    rule_ids: list[str] = []
    impacted_entity_ids: list[str] = []

    artifacts: list[TransformationArtifactResponse] = []

    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    applied_by: Optional[str] = None
    applied_at: Optional[datetime] = None
    storage_workspace_path: Optional[str] = None

    ai_proposal_status: str
    ai_proposal_summary: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class TransformationReviewRequest(BaseModel):
    status: str = Field(..., description="Review outcome status: REVIEWED, APPROVED, or REJECTED")
    user_name: str = Field("architect", description="Name/ID of reviewing architect")
    notes: Optional[str] = Field(None, description="Auditable review notes")


class TransformationApplyRequest(BaseModel):
    user_name: str = Field("architect", description="Name/ID of user applying artifact to isolated workspace")


# ==========================================
# Phase 9 — Validation & Equivalence Schemas
# ==========================================

class ValidationEvidenceResponse(BaseModel):
    """Response model for validation evidence item."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    validation_run_id: str
    stage: str
    command: str = ""
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    status: str
    evidence_json: dict[str, Any] = {}
    created_at: datetime


class BehavioralScenarioResponse(BaseModel):
    """Response model for a behavioral test scenario."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    validation_run_id: str
    business_rule_id: str
    scenario_name: str
    input_json: dict[str, Any] = {}
    legacy_output_json: dict[str, Any] = {}
    modernized_output_json: dict[str, Any] = {}
    comparison_result: str
    evidence_json: dict[str, Any] = {}
    created_at: datetime


class ValidationRunResponse(BaseModel):
    """Response model for a validation run."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    transformation_proposal_id: str
    plan_id: str
    repository_id: str

    status: str
    build_status: str
    test_status: str
    behavioral_status: str
    overall_status: str

    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    ai_explanation: Optional[str] = None
    ai_explanation_status: str = "NOT_REQUESTED"

    evidences: list[ValidationEvidenceResponse] = []
    scenarios: list[BehavioralScenarioResponse] = []

    created_at: datetime
    updated_at: datetime



class ValidationReviewRequest(BaseModel):
    status: str = Field(..., description="Validation review status: REVIEWED or VALIDATED")
    user_name: str = Field("qa_lead", description="Name/ID of reviewer")
    notes: Optional[str] = Field(None, description="Auditable verification notes")


class ValidationExplainResponse(BaseModel):
    explanation: str
    status: str



