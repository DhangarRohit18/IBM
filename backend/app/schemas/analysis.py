"""
LEGACYX — System X-Ray Analysis Schemas (Phase 3).

Defines Pydantic response models for System X-Ray endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.analysis_run import AnalysisRunStatus
from app.models.code_entity import ComponentType, EntityType
from app.models.code_relationship import RelationshipType


class AnalysisRunResponse(BaseModel):
    """Response model for an analysis run status and metrics."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    status: AnalysisRunStatus
    parser_name: str
    parser_version: str
    files_analyzed: int
    packages_count: int
    classes_count: int
    interfaces_count: int
    enums_count: int
    methods_count: int
    fields_count: int
    relationships_count: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime


class AnalysisSummaryResponse(BaseModel):
    """High-level summary of structural entities and classification breakdown."""
    analysis_id: str
    repository_id: str
    total_files: int
    total_packages: int
    total_entities: int
    classes_count: int
    interfaces_count: int
    enums_count: int
    methods_count: int
    fields_count: int
    relationships_count: int
    component_breakdown: dict[str, int]


class CodePackageResponse(BaseModel):
    """Response model for a discovered Java package."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    name: str
    created_at: datetime


class CodeMethodResponse(BaseModel):
    """Response model for a Java method or constructor."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_id: str
    name: str
    return_type: str
    parameters: list[dict[str, Any]]
    modifiers: list[str]
    annotations: list[dict[str, Any]]
    is_constructor: bool
    line_start: int
    line_end: int


class CodeFieldResponse(BaseModel):
    """Response model for a Java field."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_id: str
    name: str
    field_type: str
    modifiers: list[str]
    annotations: list[dict[str, Any]]
    line_start: int
    line_end: int


class CodeRelationshipResponse(BaseModel):
    """Response model for a structural relationship with line & construct evidence."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    source_entity_id: str
    source_method_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    target_entity_name: str
    relationship_type: RelationshipType
    relative_file_path: str
    line_number: int
    source_construct: str
    evidence_reason: str
    is_resolved: bool


class CodeEntityResponse(BaseModel):
    """Response model for a Java class/interface/enum entity."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    repository_id: str
    package_id: Optional[str] = None
    entity_type: EntityType
    name: str
    fully_qualified_name: str
    relative_file_path: str
    line_start: int
    line_end: int
    extends_name: Optional[str] = None
    implements_names: list[str]
    annotations: list[dict[str, Any]]
    modifiers: list[str]
    component_type: ComponentType
    classification_evidence: list[str]
    created_at: datetime


class CodeEntityDetailResponse(CodeEntityResponse):
    """Detailed response for a single entity including methods, fields, and relationships."""
    methods: list[CodeMethodResponse] = []
    fields: list[CodeFieldResponse] = []
    outgoing_relationships: list[CodeRelationshipResponse] = []
    incoming_relationships: list[CodeRelationshipResponse] = []


class GraphNode(BaseModel):
    id: str
    name: str
    fully_qualified_name: str
    entity_type: str
    component_type: str
    relative_file_path: str
    line_start: int
    line_end: int
    classification_evidence: list[str]


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    target_name: str
    type: str
    line_number: int
    source_construct: str
    evidence_reason: str
    is_resolved: bool


class GraphResponse(BaseModel):
    """Response model for the architecture dependency graph."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class SearchResultResponse(BaseModel):
    """Response model for structural entity search results."""
    id: str
    type: str  # CLASS, METHOD, FIELD, PACKAGE
    name: str
    fully_qualified_name: str
    relative_file_path: str
    line_start: int
    line_end: int
    component_type: Optional[str] = None
    evidence_snippet: str
