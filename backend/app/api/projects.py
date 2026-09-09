"""
LEGACYX — Projects API Router (Phase 2).

Endpoints:
  POST /api/v1/projects                            — Create project
  GET  /api/v1/projects                            — List projects
  GET  /api/v1/projects/{project_id}               — Get project details
  POST /api/v1/projects/{project_id}/repositories  — Upload repository ZIP
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.db.base import get_async_session
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.repository import (
    IngestionRunResponse,
    ProjectCreate,
    ProjectResponse,
    RepositoryResponse,
)
from app.services.ingestion.extractor import IngestionSecurityException
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/projects", tags=["projects"])
settings = get_settings()


async def get_or_create_default_user(session: AsyncSession) -> User:
    """Helper to retrieve or create default dev user in Phase 2."""
    stmt = select(User).where(User.email == "dev@legacyx.internal")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id="usr-dev-default-001",
            email="dev@legacyx.internal",
            display_name="Dev Engineer",
            hashed_password="dev",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    payload: ProjectCreate,
    session: AsyncSession = Depends(get_async_session),
) -> ProjectResponse:
    """Create a new legacy project under analysis."""
    dev_user = await get_or_create_default_user(session)

    project = Project(
        owner_id=dev_user.id,
        name=payload.name,
        description=payload.description,
        status=ProjectStatus.CREATED,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List all projects",
)
async def list_projects(
    session: AsyncSession = Depends(get_async_session),
) -> list[ProjectResponse]:
    """List all legacy projects."""
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await session.execute(stmt)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ProjectResponse:
    """Get project details by ID."""
    stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    return ProjectResponse.model_validate(project)


@router.post(
    "/{project_id}/repositories",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload repository ZIP file and start ingestion",
)
async def upload_repository(
    project_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
) -> RepositoryResponse:
    """Upload repository ZIP artifact, persist immutably, and execute ingestion pipeline."""
    # ── 1. Validate project existence ──────────────────────────────────────────
    stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    # ── 2. Validate filename extension ─────────────────────────────────────────
    filename = file.filename or "repository.zip"
    if not filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_FILE_TYPE: Only ZIP repository archives (.zip) are supported",
        )

    # ── 3. Read uploaded bytes and check size limit ─────────────────────────────
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"FILE_TOO_LARGE: Upload size ({len(content) // (1024*1024)}MB) exceeds limit of {settings.max_upload_size_mb}MB",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_ARCHIVE: Uploaded file is empty",
        )

    # ── 4. Execute Ingestion Pipeline ──────────────────────────────────────────
    ingestion_service = IngestionService()
    try:
        repository, ingestion_run = await ingestion_service.create_repository_record(
            session, project, filename, content
        )

        # Run ingestion synchronously for Phase 2
        repository, manifest = await ingestion_service.run_ingestion_pipeline(
            session, repository.id, ingestion_run.id
        )

        resp = RepositoryResponse.model_validate(repository)
        resp.latest_ingestion_run = IngestionRunResponse.model_validate(ingestion_run)
        return resp

    except IngestionSecurityException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exc.code}: {exc.message}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"EXTRACTION_FAILED: {str(exc)}",
        )
