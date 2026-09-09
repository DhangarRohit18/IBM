"""
LEGACYX — Business Rules Response & Request Schemas (Phase 4).

Pydantic schemas for Phase 4 Business Logic Recovery endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.business_rule import AIExplanationStatus, RuleStatus, RuleType


class RuleTraceStep(BaseModel):
    step_type: str  # CONDITION, DECISION_CONTEXT, ACTION, STATE_CHANGE
    label: str
    details: Optional[str] = None
    line_number: Optional[int] = None


class BusinessRuleResponse(BaseModel):
    """Response model for a business rule candidate."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    repository_id: str
    entity_id: Optional[str] = None
    method_id: Optional[str] = None
    rule_type: RuleType
    title: str
    status: RuleStatus

    # Deterministic Facts
    condition_expression: Optional[str] = None
    action_expression: Optional[str] = None
    outcome_expression: Optional[str] = None
    threshold_value: Optional[str] = None
    threshold_operator: Optional[str] = None
    calculation_formula: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None

    # Deterministic Trace
    rule_trace: list[RuleTraceStep] = []

    # Evidence
    relative_file_path: str
    line_start: int
    line_end: int
    source_construct: str
    extraction_reason: str

    # AI Explanation
    ai_explanation: Optional[str] = None
    ai_explanation_status: AIExplanationStatus

    # Audit Trail
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RuleReviewRequest(BaseModel):
    """Request model for reviewing/rejecting a business rule candidate."""
    status: RuleStatus  # REVIEWED or REJECTED
    reviewed_by: Optional[str] = "engineer"
    review_notes: Optional[str] = None


class AIExplanationResponse(BaseModel):
    """Response model for an AI explanation request."""
    rule_id: str
    status: AIExplanationStatus
    explanation: Optional[str] = None
    error_message: Optional[str] = None
