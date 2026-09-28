"""
LEGACYX — Modernization Assurance & Decision Replay Schemas.

Pydantic schemas for Decision Contracts, Decision Replay Lab, Silent Drift Detection,
Three-Layer Impact Analysis, What-If Simulation, and Modernization Risk Scoring.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Decision Contracts ──────────────────────────────────────────────────────────

class DecisionContractCreateRequest(BaseModel):
    contract_id: str
    name: str
    business_domain: str = "FINANCIAL_SERVICES"
    business_rule_id: Optional[str] = None
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    expected_decision: str
    expected_outputs: dict[str, Any] = Field(default_factory=dict)
    is_critical: bool = False
    notes: Optional[str] = None


class DecisionContractUpdateRequest(BaseModel):
    name: Optional[str] = None
    inputs: Optional[list[dict[str, Any]]] = None
    conditions: Optional[list[str]] = None
    expected_decision: Optional[str] = None
    expected_outputs: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    is_critical: Optional[bool] = None
    notes: Optional[str] = None


class DecisionContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_id: str
    name: str
    business_domain: str
    repository_id: str
    analysis_id: str
    business_rule_id: Optional[str] = None
    inputs: list[dict[str, Any]] = []
    conditions: list[str] = []
    expected_decision: str
    expected_outputs: dict[str, Any] = {}
    version: int = 1
    status: str
    is_critical: bool = False
    evidence: dict[str, Any] = {}
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ── Decision Replay & Silent Drift Detection ──────────────────────────────────

class DecisionScenarioResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    replay_run_id: str
    scenario_number: int
    scenario_id: str
    scenario_name: str
    scenario_category: str
    contract_id: Optional[str] = None
    business_rule_id: Optional[str] = None

    input_payload: dict[str, Any]
    legacy_decision: str
    legacy_output: dict[str, Any]
    legacy_rule_path: list[str] = []
    legacy_execution_time_ms: int

    modern_decision: str
    modern_output: dict[str, Any]
    modern_rule_path: list[str] = []
    modern_execution_time_ms: int

    comparison_status: str  # PRESERVED, BEHAVIOR_DRIFT, UNKNOWN
    drift_type: str        # NONE, THRESHOLD_SHIFT, ROUNDING_PRECISION, etc.
    drift_severity: str    # NONE, LOW, MEDIUM, HIGH, CRITICAL
    drift_details: Optional[str] = None
    drift_root_cause: dict[str, Any] = {}
    remediation_suggestion: Optional[str] = None
    evidence_chain: dict[str, Any] = {}

    reviewed: bool = False
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime


class DecisionReplayRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    proposal_id: Optional[str] = None
    validation_run_id: Optional[str] = None
    status: str
    total_scenarios: int
    preserved_count: int
    drift_count: int
    unknown_count: int
    risk_assessment: str
    summary: Optional[str] = None
    executed_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: list[DecisionScenarioResultResponse] = []


class DecisionReplayExecuteRequest(BaseModel):
    proposal_id: Optional[str] = None
    scenario_categories: list[str] = Field(
        default_factory=lambda: [
            "BOUNDARY_THRESHOLD",
            "CURRENCY_PRECISION",
            "FRAUD_EVALUATION",
            "ELIGIBILITY_CHECK",
            "NULL_HANDLING",
            "STATE_TRANSITION",
        ]
    )
    include_deliberate_drift: bool = True  # Used to showcase empirical drift detection


# ── Three-Layer Impact Analysis ───────────────────────────────────────────────

class ImpactLayerNode(BaseModel):
    id: str
    label: str
    type: str  # CLASS, METHOD, RULE, SERVICE, API, PROCESS, THRESHOLD
    layer: str # CODE, BUSINESS, BEHAVIORAL
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    details: dict[str, Any] = Field(default_factory=dict)


class ImpactLayerEdge(BaseModel):
    source: str
    target: str
    relationship: str # CALLS, IMPLEMENTS, ENFORCES, TRIGGERS, IMPACTS
    confidence: float = 1.0


class ThreeLayerImpactResponse(BaseModel):
    target_entity: str
    target_name: str
    code_impact: dict[str, Any]       # Classes, Methods, Dependencies
    business_impact: dict[str, Any]   # Business Rules, Domain Services, APIs, Workflows
    behavioral_impact: dict[str, Any] # Thresholds, Decisions, State transitions
    nodes: list[ImpactLayerNode] = []
    edges: list[ImpactLayerEdge] = []
    summary_narrative: str
    risk_level: str


# ── What-If Business Rule Simulator ───────────────────────────────────────────

class WhatIfSimulationRequest(BaseModel):
    business_rule_id: str
    modified_parameter: str          # e.g. "threshold_value", "threshold_operator", "condition_expression"
    original_value: str              # e.g. "50000" or "0.80"
    simulated_value: str             # e.g. "45000" or "0.75"
    simulated_operator: Optional[str] = None # e.g. ">=" instead of ">"


class WhatIfSimulationResponse(BaseModel):
    simulation_id: str
    rule_id: str
    rule_title: str
    parameter_changed: str
    original_value: str
    simulated_value: str

    # Projected Blast Radius
    affected_rules: list[dict[str, Any]] = []
    affected_methods: list[str] = []
    affected_services: list[str] = []
    affected_apis: list[str] = []
    affected_tests: list[str] = []
    affected_workflows: list[str] = []
    affected_contracts: list[str] = []

    # Projected Decision Drift
    projected_drift_scenarios: int
    projected_drift_rate_pct: float
    projected_risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    analysis_narrative: str
    evidence_trail: list[str] = []


# ── Modernization Risk Scorecard ──────────────────────────────────────────────

class RiskDimension(BaseModel):
    dimension: str     # Architecture, Business Rules, Dependencies, Behavioral Drift, Validation, Data
    score: float       # 0.0 to 100.0
    level: str         # LOW, MEDIUM, HIGH, CRITICAL
    weight: float
    evidence_points: list[str] = []
    key_findings: list[str] = []


class ModernizationRiskScoreResponse(BaseModel):
    repository_id: str
    overall_risk_score: float
    overall_status: str       # LOW_RISK, ACCEPTABLE, REVIEW_REQUIRED, BLOCKED
    dimensions: list[RiskDimension] = []
    summary: str
    recommended_actions: list[str] = []
    evaluated_at: datetime


# ── Modernization Assurance Report ────────────────────────────────────────────

class ModernizationAssuranceReportResponse(BaseModel):
    report_id: str
    repository_id: str
    repository_name: str
    timestamp: datetime
    product_version: str = "LEGACYX 2.0"
    motto: str = "Modernize the Code. Preserve the Decision. Prove the Difference."

    executive_summary: str
    architecture_status: dict[str, Any]
    business_rules_discovered: int
    contracts_enforced: int
    replay_results: dict[str, Any]
    drift_detection_summary: dict[str, Any]
    three_layer_impact_summary: dict[str, Any]
    risk_scorecard: ModernizationRiskScoreResponse
    watsonx_narrative: str
    evidence_hash_tree: list[dict[str, str]]
    signoff_status: str       # PENDING_AUDIT, APPROVED, CONDITIONALLY_APPROVED, REJECTED
    signoff_authority: Optional[str] = None
