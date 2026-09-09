"""
LEGACYX — System X-Ray Analysis API Router (Phase 3).

Endpoints:
  POST /api/v1/repositories/{repository_id}/analysis   — Start static analysis
  GET  /api/v1/analysis/{analysis_id}                  — Get analysis status & run details
  GET  /api/v1/analysis/{analysis_id}/summary          — Get summary stats & component breakdown
  GET  /api/v1/analysis/{analysis_id}/packages         — List packages
  GET  /api/v1/analysis/{analysis_id}/classes          — List entities (search & component filter)
  GET  /api/v1/analysis/{analysis_id}/classes/{id}     — Detailed class view with line numbers & evidence
  GET  /api/v1/analysis/{analysis_id}/relationships   — List structural relationships with source evidence
  GET  /api/v1/analysis/{analysis_id}/graph           — Get architecture dependency graph
  GET  /api/v1/analysis/{analysis_id}/search          — Structural search across entities, methods, fields
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.analysis_engine.graph_builder import ArchitectureGraphBuilder
from app.analysis_engine.service import AnalysisService
from app.db.base import get_async_session
from app.models.analysis_run import AnalysisRun
from app.models.code_entity import CodeEntity, ComponentType
from app.models.code_field import CodeField
from app.models.code_method import CodeMethod
from app.models.code_package import CodePackage
from app.models.code_relationship import CodeRelationship
from app.models.repository import Repository
from app.schemas.analysis import (
    AnalysisRunResponse,
    AnalysisSummaryResponse,
    CodeEntityDetailResponse,
    CodeEntityResponse,
    CodeFieldResponse,
    CodeMethodResponse,
    CodePackageResponse,
    CodeRelationshipResponse,
    GraphResponse,
    SearchResultResponse,
)

router = APIRouter(prefix="", tags=["analysis"])


@router.post(
    "/repositories/{repository_id}/analysis",
    response_model=AnalysisRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start System X-Ray static analysis",
)
async def start_analysis(
    repository_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> AnalysisRunResponse:
    """Start static analysis pipeline for an ingested repository."""
    stmt = select(Repository).where(Repository.id == repository_id)
    res = await session.execute(stmt)
    repository = res.scalar_one_or_none()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    analysis_service = AnalysisService()
    analysis_run = await analysis_service.create_analysis_run(session, repository)

    # Run analysis pipeline synchronously for Phase 3
    analysis_run, _ = await analysis_service.run_analysis_pipeline(
        session, repository.id, analysis_run.id
    )

    return AnalysisRunResponse.model_validate(analysis_run)


@router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisRunResponse,
    summary="Get analysis run details",
)
async def get_analysis_run(
    analysis_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> AnalysisRunResponse:
    """Get status and metrics of an analysis run."""
    stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
    res = await session.execute(stmt)
    run = res.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRun '{analysis_id}' not found",
        )

    return AnalysisRunResponse.model_validate(run)


@router.get(
    "/analysis/{analysis_id}/summary",
    response_model=AnalysisSummaryResponse,
    summary="Get analysis summary metrics",
)
async def get_analysis_summary(
    analysis_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> AnalysisSummaryResponse:
    """Get high-level summary and component classification breakdown."""
    stmt = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
    res = await session.execute(stmt)
    run = res.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRun '{analysis_id}' not found",
        )

    stmt_entities = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
    res_entities = await session.execute(stmt_entities)
    entities = res_entities.scalars().all()

    breakdown: dict[str, int] = {}
    for e in entities:
        comp_val = e.component_type.value
        breakdown[comp_val] = breakdown.get(comp_val, 0) + 1

    return AnalysisSummaryResponse(
        analysis_id=run.id,
        repository_id=run.repository_id,
        total_files=run.files_analyzed,
        total_packages=run.packages_count,
        total_entities=len(entities),
        classes_count=run.classes_count,
        interfaces_count=run.interfaces_count,
        enums_count=run.enums_count,
        methods_count=run.methods_count,
        fields_count=run.fields_count,
        relationships_count=run.relationships_count,
        component_breakdown=breakdown,
    )


@router.get(
    "/analysis/{analysis_id}/packages",
    response_model=list[CodePackageResponse],
    summary="List packages in analysis",
)
async def list_packages(
    analysis_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[CodePackageResponse]:
    """List all packages discovered in an analysis run."""
    stmt = (
        select(CodePackage)
        .where(CodePackage.analysis_id == analysis_id)
        .order_by(CodePackage.name.asc())
    )
    res = await session.execute(stmt)
    packages = res.scalars().all()
    return [CodePackageResponse.model_validate(p) for p in packages]


@router.get(
    "/analysis/{analysis_id}/classes",
    response_model=list[CodeEntityResponse],
    summary="List classes & entities",
)
async def list_classes(
    analysis_id: str,
    component: Optional[str] = Query(None, description="Filter by component type (CONTROLLER, SERVICE, REPOSITORY, etc.)"),
    q: Optional[str] = Query(None, description="Search query"),
    session: AsyncSession = Depends(get_async_session),
) -> list[CodeEntityResponse]:
    """List structural entities with optional filtering."""
    stmt = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)

    if component:
        try:
            comp_enum = ComponentType(component.upper())
            stmt = stmt.where(CodeEntity.component_type == comp_enum)
        except ValueError:
            pass

    if q:
        stmt = stmt.where(CodeEntity.name.ilike(f"%{q}%") | CodeEntity.fully_qualified_name.ilike(f"%{q}%"))

    stmt = stmt.order_by(CodeEntity.name.asc())
    res = await session.execute(stmt)
    entities = res.scalars().all()
    return [CodeEntityResponse.model_validate(e) for e in entities]


@router.get(
    "/analysis/{analysis_id}/classes/{class_id}",
    response_model=CodeEntityDetailResponse,
    summary="Get detailed class information",
)
@router.get(
    "/analysis/classes/{class_id}",
    response_model=CodeEntityDetailResponse,
    summary="Get detailed class information alias",
)
async def get_class_detail(
    class_id: str,
    analysis_id: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
) -> CodeEntityDetailResponse:
    """Get full entity inspector details including line numbers, methods, fields, annotations, dependencies, and callers."""
    stmt = (
        select(CodeEntity)
        .options(
            selectinload(CodeEntity.methods),
            selectinload(CodeEntity.fields),
        )
        .where(CodeEntity.id == class_id)
    )
    if analysis_id:
        stmt = stmt.where(CodeEntity.analysis_id == analysis_id)

    res = await session.execute(stmt)
    entity = res.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class entity '{class_id}' not found",
        )

    # Outgoing relationships
    stmt_out = select(CodeRelationship).where(CodeRelationship.source_entity_id == class_id)
    res_out = await session.execute(stmt_out)
    outgoing = res_out.scalars().all()

    # Incoming relationships
    stmt_in = select(CodeRelationship).where(CodeRelationship.target_entity_id == class_id)
    res_in = await session.execute(stmt_in)
    incoming = res_in.scalars().all()

    detail = CodeEntityDetailResponse.model_validate(entity)
    detail.methods = [CodeMethodResponse.model_validate(m) for m in entity.methods]
    detail.fields = [CodeFieldResponse.model_validate(f) for f in entity.fields]
    detail.outgoing_relationships = [CodeRelationshipResponse.model_validate(r) for r in outgoing]
    detail.incoming_relationships = [CodeRelationshipResponse.model_validate(r) for r in incoming]

    return detail


@router.get(
    "/analysis/{analysis_id}/relationships",
    response_model=list[CodeRelationshipResponse],
    summary="List relationships with source evidence",
)
async def list_relationships(
    analysis_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[CodeRelationshipResponse]:
    """List structural relationships with line number and source construct evidence."""
    stmt = (
        select(CodeRelationship)
        .where(CodeRelationship.analysis_id == analysis_id)
        .order_by(CodeRelationship.line_number.asc())
    )
    res = await session.execute(stmt)
    rels = res.scalars().all()
    return [CodeRelationshipResponse.model_validate(r) for r in rels]


@router.get(
    "/analysis/{analysis_id}/graph",
    response_model=GraphResponse,
    summary="Get architecture graph",
)
async def get_architecture_graph(
    analysis_id: str,
    package: Optional[str] = Query(None, description="Filter by package prefix"),
    component: Optional[str] = Query(None, description="Filter by component type"),
    session: AsyncSession = Depends(get_async_session),
) -> GraphResponse:
    """Get nodes and edges for the System X-Ray architecture dependency graph."""
    stmt_entities = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
    res_entities = await session.execute(stmt_entities)
    entities = res_entities.scalars().all()

    stmt_rels = select(CodeRelationship).where(CodeRelationship.analysis_id == analysis_id)
    res_rels = await session.execute(stmt_rels)
    relationships = res_rels.scalars().all()

    builder = ArchitectureGraphBuilder()
    graph_dict = builder.build_graph(entities, relationships, package_filter=package, component_filter=component)

    return GraphResponse(**graph_dict)


@router.get(
    "/analysis/{analysis_id}/search",
    response_model=list[SearchResultResponse],
    summary="Structural entity search",
)
async def search_entities(
    analysis_id: str,
    q: str = Query(..., min_length=1, description="Search query"),
    session: AsyncSession = Depends(get_db_session_placeholder := get_async_session),
) -> list[SearchResultResponse]:
    """Perform deterministic search across classes, methods, fields, and packages."""
    results: list[SearchResultResponse] = []
    query_str = f"%{q.lower()}%"

    # Search Entities (Classes/Interfaces/Enums)
    stmt_ent = select(CodeEntity).where(
        CodeEntity.analysis_id == analysis_id,
        (CodeEntity.name.ilike(query_str) | CodeEntity.fully_qualified_name.ilike(query_str)),
    )
    res_ent = await session.execute(stmt_ent)
    for e in res_ent.scalars().all():
        results.append(
            SearchResultResponse(
                id=e.id,
                type=e.entity_type.value,
                name=e.name,
                fully_qualified_name=e.fully_qualified_name,
                relative_file_path=e.relative_file_path,
                line_start=e.line_start,
                line_end=e.line_end,
                component_type=e.component_type.value,
                evidence_snippet=f"{e.entity_type.value.lower()} {e.name} in {e.relative_file_path}:{e.line_start}",
            )
        )

    # Search Methods
    stmt_m = (
        select(CodeMethod, CodeEntity)
        .join(CodeEntity, CodeMethod.entity_id == CodeEntity.id)
        .where(CodeMethod.analysis_id == analysis_id, CodeMethod.name.ilike(query_str))
    )
    res_m = await session.execute(stmt_m)
    for m, e in res_m.all():
        results.append(
            SearchResultResponse(
                id=m.id,
                type="METHOD",
                name=m.name,
                fully_qualified_name=f"{e.fully_qualified_name}.{m.name}()",
                relative_file_path=e.relative_file_path,
                line_start=m.line_start,
                line_end=m.line_end,
                component_type=e.component_type.value,
                evidence_snippet=f"method {m.return_type} {m.name}() in {e.relative_file_path}:{m.line_start}",
            )
        )

    # Search Fields
    stmt_f = (
        select(CodeField, CodeEntity)
        .join(CodeEntity, CodeField.entity_id == CodeEntity.id)
        .where(CodeField.analysis_id == analysis_id, CodeField.name.ilike(query_str))
    )
    res_f = await session.execute(stmt_f)
    for f, e in res_f.all():
        results.append(
            SearchResultResponse(
                id=f.id,
                type="FIELD",
                name=f.name,
                fully_qualified_name=f"{e.fully_qualified_name}.{f.name}",
                relative_file_path=e.relative_file_path,
                line_start=f.line_start,
                line_end=f.line_end,
                component_type=e.component_type.value,
                evidence_snippet=f"field {f.field_type} {f.name} in {e.relative_file_path}:{f.line_start}",
            )
        )

    return results
