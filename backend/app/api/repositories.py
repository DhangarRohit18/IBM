"""
LEGACYX — Repositories API Router (Phase 2).

Endpoints:
  POST /api/v1/repositories/{repository_id}/ingest        — Trigger ingestion
  GET  /api/v1/repositories/{repository_id}               — Get repository overview
  GET  /api/v1/repositories/{repository_id}/files         — List repository files / tree
  GET  /api/v1/repositories/{repository_id}/manifest      — Get repository manifest
  GET  /api/v1/repositories/{repository_id}/ingestion     — Get ingestion run status
  GET  /api/v1/repositories/{repository_id}/files/content — View safe source file text
"""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.storage import LocalStorageProvider
from app.db.base import get_async_session
from app.models.ingestion_run import IngestionRun, IngestionStatus
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.schemas.repository import (
    FileContentResponse,
    IngestionRunResponse,
    RepositoryFileResponse,
    RepositoryManifestResponse,
    RepositoryResponse,
)
from app.services.ingestion.detector import TechnologyDetector
from app.services.ingestion.indexer import FileIndexer, IndexedFileItem
from app.services.ingestion.manifest import ManifestGenerator
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/repositories", tags=["repositories"])
storage_provider = LocalStorageProvider()


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    summary="Get repository overview",
)
async def get_repository(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> RepositoryResponse:
    """Get metadata, sha256 checksum, and status of a repository."""
    stmt = select(Repository).where(
        (Repository.id == repository_id) | (Repository.project_id == repository_id)
    )
    result = await session.execute(stmt)
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    # Fetch latest ingestion run
    stmt_run = (
        select(IngestionRun)
        .where(IngestionRun.repository_id == repository_id)
        .order_by(IngestionRun.created_at.desc())
    )
    res_run = await session.execute(stmt_run)
    latest_run = res_run.scalars().first()

    resp = RepositoryResponse.model_validate(repository)
    if latest_run:
        resp.latest_ingestion_run = IngestionRunResponse.model_validate(latest_run)
    return resp


@router.post(
    "/{repository_id}/ingest",
    response_model=RepositoryResponse,
    summary="Trigger ingestion run for repository",
)
async def trigger_ingestion(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> RepositoryResponse:
    """Re-trigger or execute ingestion run for an uploaded repository."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await session.execute(stmt)
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    ingestion_service = IngestionService(storage_provider)

    ingestion_run = IngestionRun(
        repository_id=repository.id,
        status=IngestionStatus.STARTED,
    )
    session.add(ingestion_run)
    await session.commit()
    await session.refresh(ingestion_run)

    repository, _ = await ingestion_service.run_ingestion_pipeline(
        session, repository.id, ingestion_run.id
    )

    resp = RepositoryResponse.model_validate(repository)
    resp.latest_ingestion_run = IngestionRunResponse.model_validate(ingestion_run)
    return resp


@router.get(
    "/{repository_id}/files",
    response_model=list[RepositoryFileResponse],
    summary="List files in repository",
)
async def list_repository_files(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[RepositoryFileResponse]:
    """List all indexed files for a repository."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    stmt_files = (
        select(RepositoryFile)
        .where(RepositoryFile.repository_id == repository_id)
        .order_by(RepositoryFile.relative_path.asc())
    )
    res_files = await session.execute(stmt_files)
    files = res_files.scalars().all()
    return [RepositoryFileResponse.model_validate(f) for f in files]


@router.get(
    "/{repository_id}/manifest",
    response_model=RepositoryManifestResponse,
    summary="Get repository manifest",
)
async def get_repository_manifest(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> RepositoryManifestResponse:
    """Generate and return repository manifest with technology evidence and file breakdowns."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await session.execute(stmt)
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    stmt_files = select(RepositoryFile).where(RepositoryFile.repository_id == repository_id)
    res_files = await session.execute(stmt_files)
    db_files = res_files.scalars().all()

    indexed_items = [
        IndexedFileItem(
            relative_path=f.relative_path,
            filename=f.filename,
            extension=f.extension,
            size_bytes=f.size_bytes,
            is_directory=f.is_directory,
            checksum=f.checksum,
        )
        for f in db_files
    ]

    extracted_dir = (
        storage_provider.get_extracted_path(repository.id)
        if repository.extracted_path
        else Path("./storage/extracted") / repository.id
    )

    detector = TechnologyDetector()
    technologies = detector.detect_technologies(extracted_dir, indexed_items)

    manifest_gen = ManifestGenerator()
    manifest_dict = manifest_gen.generate_manifest(
        repository_id=repository.id,
        original_filename=repository.original_filename,
        artifact_size=repository.artifact_size,
        sha256=repository.sha256,
        indexed_items=indexed_items,
        technologies=technologies,
    )

    return RepositoryManifestResponse(**manifest_dict)


@router.get(
    "/{repository_id}/ingestion",
    response_model=list[IngestionRunResponse],
    summary="Get ingestion runs history",
)
async def get_ingestion_runs(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[IngestionRunResponse]:
    """List all ingestion runs for a repository."""
    stmt = (
        select(IngestionRun)
        .where(IngestionRun.repository_id == repository_id)
        .order_by(IngestionRun.started_at.desc())
    )
    result = await session.execute(stmt)
    runs = result.scalars().all()
    return [IngestionRunResponse.model_validate(r) for r in runs]


@router.get(
    "/{repository_id}/files/content",
    response_model=FileContentResponse,
    summary="Get source file text content",
)
async def get_file_content(
    repository_id: str,
    path: str = Query(..., description="Relative file path"),
    session: AsyncSession = Depends(get_async_session),
) -> FileContentResponse:
    """Read text content of a specific file safely for viewing in the UI file explorer."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await session.execute(stmt)
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    # Sanitize path traversal in query parameter
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PATH_TRAVERSAL_DETECTED: Invalid relative path",
        )

    extracted_dir = storage_provider.get_extracted_path(repository_id)
    target_file = (extracted_dir / path).resolve()

    if not str(target_file).startswith(str(extracted_dir.resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PATH_TRAVERSAL_DETECTED: Requested file is outside repository boundary",
        )

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{path}' not found",
        )

    size_bytes = target_file.stat().st_size

    # Limit max preview size to 1MB to prevent memory exhaustion
    max_preview_bytes = 1024 * 1024
    is_truncated = size_bytes > max_preview_bytes

    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_preview_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to read file content: {str(exc)}",
        )

    return FileContentResponse(
        relative_path=path,
        filename=target_file.name,
        extension=target_file.suffix.lstrip(".").lower(),
        size_bytes=size_bytes,
        content=content,
        is_truncated=is_truncated,
    )
