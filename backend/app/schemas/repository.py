"""
LEGACYX — Repository & Project Schemas (Phase 2).

Defines Pydantic response and request models for API validation and response shaping.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.ingestion_run import IngestionStatus
from app.models.project import ProjectStatus
from app.models.repository import RepositoryStatus


# ── Project Schemas ────────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    """Payload for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(default=None, description="Optional description")


class ProjectResponse(BaseModel):
    """Response model for a project."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


# ── Repository File Schema ─────────────────────────────────────────────────────
class RepositoryFileResponse(BaseModel):
    """Response model for a single file in a repository."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    relative_path: str
    filename: str
    extension: str
    size_bytes: int
    is_directory: bool
    checksum: str | None


# ── Ingestion Run Schema ───────────────────────────────────────────────────────
class IngestionRunResponse(BaseModel):
    """Response model for an ingestion run audit record."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    repository_id: str
    status: IngestionStatus
    started_at: datetime
    completed_at: datetime | None
    files_discovered: int
    directories_discovered: int
    bytes_extracted: int
    error_code: str | None
    error_message: str | None


# ── Repository Overview Schema ─────────────────────────────────────────────────
class RepositoryResponse(BaseModel):
    """Response model for repository metadata and operational status."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    original_filename: str
    artifact_size: int
    sha256: str
    status: RepositoryStatus
    created_at: datetime
    updated_at: datetime
    latest_ingestion_run: IngestionRunResponse | None = None


# ── Repository Manifest Schema ─────────────────────────────────────────────────
class TechnologyEvidenceResponse(BaseModel):
    name: str
    evidence: list[str]


class RepositoryManifestResponse(BaseModel):
    """Response model for repository manifest."""
    repository: dict[str, Any]
    summary: dict[str, Any]
    extension_breakdown: dict[str, int]
    technologies: list[TechnologyEvidenceResponse]
    key_files: list[str]


# ── File Content View Schema ───────────────────────────────────────────────────
class FileContentResponse(BaseModel):
    """Response model for safely reading source file text content."""
    relative_path: str
    filename: str
    extension: str
    size_bytes: int
    content: str
    is_truncated: bool = False
