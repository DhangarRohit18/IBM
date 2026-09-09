"""
LEGACYX — Impact Analysis Schemas (Phase 5).

Pydantic schemas for Phase 5 Impact Analysis endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ImpactTargetInfo(BaseModel):
    id: str
    type: str  # class, method, field, package, business_rule
    name: str
    fully_qualified_name: str
    file_path: str = ""
    description: str = ""


class AffectedComponentResponse(BaseModel):
    id: str
    name: str
    fully_qualified_name: str
    entity_type: str
    component_type: str
    relative_file_path: str
    line_start: int
    line_end: int
    depth: int
    is_direct: bool
    is_target: bool = False


class AffectedRuleResponse(BaseModel):
    id: str
    title: str
    rule_type: str
    status: str
    relative_file_path: str
    line_start: int
    line_end: int
    entity_id: Optional[str] = None
    method_id: Optional[str] = None
    condition_expression: Optional[str] = None
    action_expression: Optional[str] = None
    extraction_reason: str
    depth: Optional[int] = None
    is_target: bool = False


class ImpactPathStep(BaseModel):
    from_component: str
    from_id: str
    to_component: str
    to_id: str
    relationship_type: str
    depth: int
    file_path: str
    line_number: int
    evidence_reason: str


class ImpactSummary(BaseModel):
    direct_component_count: int
    transitive_component_count: int
    direct_rule_count: int
    transitive_rule_count: int
    total_impacted_nodes: int


class ImpactGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    target_name: str
    type: str
    line_number: int
    relative_file_path: str
    source_construct: str
    evidence_reason: str
    is_resolved: bool


class ImpactGraph(BaseModel):
    nodes: list[AffectedComponentResponse]
    edges: list[ImpactGraphEdge]


class ImpactAnalysisResponse(BaseModel):
    analysis_id: str
    target: ImpactTargetInfo
    direction: str  # forward or reverse
    max_depth: int
    has_evidenced_impact: bool
    status: str  # EVIDENCED_IMPACT_FOUND or NO_EVIDENCED_IMPACT
    summary: ImpactSummary
    direct_affected_components: list[AffectedComponentResponse]
    transitive_affected_components: list[AffectedComponentResponse]
    direct_affected_rules: list[AffectedRuleResponse]
    transitive_affected_rules: list[AffectedRuleResponse]
    impact_paths: list[ImpactPathStep]
    graph: ImpactGraph


class ImpactExplainRequest(BaseModel):
    analysis_id: str
    target_type: str
    target_id: str
    direction: str = "forward"
    max_depth: int = 3


class ImpactExplainResponse(BaseModel):
    explanation: str
    status: str
