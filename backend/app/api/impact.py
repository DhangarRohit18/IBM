"""
LEGACYX — Impact Analysis API Router (Phase 5).

Endpoints:
  GET  /api/v1/analysis/{analysis_id}/impact — Perform deterministic impact analysis
  POST /api/v1/impact/explain                — Request AI explanation of established impact paths
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import ai_gateway
from app.analysis_engine.impact_analyzer import ImpactDirection, ImpactTargetType, impact_analyzer
from app.db.base import get_async_session
from app.schemas.impact import (
    ImpactAnalysisResponse,
    ImpactExplainRequest,
    ImpactExplainResponse,
)

router = APIRouter(prefix="", tags=["impact-analysis"])


@router.get(
    "/analysis/{analysis_id}/impact",
    response_model=ImpactAnalysisResponse,
    summary="Perform deterministic impact analysis",
)
async def analyze_impact(
    analysis_id: str,
    target_type: str = Query(..., description="Target type (class, method, field, package, business_rule)"),
    target_id: str = Query(..., description="Target UUID or identifier"),
    direction: str = Query("forward", description="Traversal direction: forward (dependencies) or reverse (dependents)"),
    max_depth: int = Query(3, ge=1, le=10, description="Maximum traversal depth (1..10)"),
    session: AsyncSession = Depends(get_async_session),
) -> ImpactAnalysisResponse:
    """
    Computes deterministic forward or reverse impact analysis for a specified code construct or business rule.
    Returns direct vs transitive affected components, affected business rules, impact paths, and visual graph elements.
    """
    try:
        tt = ImpactTargetType(target_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target_type '{target_type}'. Allowed: class, method, field, package, business_rule",
        )

    try:
        dir_enum = ImpactDirection(direction.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid direction '{direction}'. Allowed: forward, reverse",
        )

    result = await impact_analyzer.analyze(
        session=session,
        analysis_id=analysis_id,
        target_type=tt,
        target_id=target_id,
        direction=dir_enum,
        max_depth=max_depth,
    )

    return ImpactAnalysisResponse(**result)


@router.post(
    "/impact/explain",
    response_model=ImpactExplainResponse,
    summary="Request AI explanation of established impact paths",
)
async def explain_impact(
    body: ImpactExplainRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ImpactExplainResponse:
    """
    Requests AI Gateway narrative explanation for established impact facts.
    Strict AI Boundary: Traversal logic establishes all facts first; AI only translates facts into explanation.
    """
    try:
        tt = ImpactTargetType(body.target_type.lower())
        dir_enum = ImpactDirection(body.direction.lower())
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    # Fetch deterministic analysis facts first
    impact_data = await impact_analyzer.analyze(
        session=session,
        analysis_id=body.analysis_id,
        target_type=tt,
        target_id=body.target_id,
        direction=dir_enum,
        max_depth=body.max_depth,
    )

    context = {
        "target_name": impact_data["target"]["name"],
        "target_type": impact_data["target"]["type"],
        "direction": impact_data["direction"],
        "max_depth": impact_data["max_depth"],
        "status": impact_data["status"],
        "direct_components": impact_data["direct_affected_components"],
        "transitive_components": impact_data["transitive_affected_components"],
        "direct_rules": impact_data["direct_affected_rules"],
        "impact_paths": impact_data["impact_paths"],
    }

    success, explanation = await ai_gateway.generate_impact_explanation(context)

    return ImpactExplainResponse(
        explanation=explanation,
        status="COMPLETED" if success else "FAILED",
    )
