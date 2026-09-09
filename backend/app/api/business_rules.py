"""
LEGACYX — Business Logic Recovery API Router (Phase 4).

Endpoints:
  POST /api/v1/analysis/{analysis_id}/business-rules/extract — Trigger rule extraction
  GET  /api/v1/analysis/{analysis_id}/business-rules         — List extracted rules with filters
  GET  /api/v1/analysis/{analysis_id}/business-rules/{id}     — Get detailed rule inspection
  POST /api/v1/business-rules/{id}/explain                    — Request AI Gateway explanation
  POST /api/v1/business-rules/{id}/review                     — Review or reject rule candidate
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.ai.gateway import ai_gateway
from app.db.base import get_async_session
from app.models.analysis_run import AnalysisRun
from app.models.business_rule import AIExplanationStatus, BusinessRule, RuleStatus, RuleType
from app.schemas.business_rules import (
    AIExplanationResponse,
    BusinessRuleResponse,
    RuleReviewRequest,
)

router = APIRouter(prefix="", tags=["business-rules"])


@router.get(
    "/analysis/{analysis_id}/business-rules",
    response_model=list[BusinessRuleResponse],
    summary="List extracted business rules",
)
async def list_business_rules(
    analysis_id: str,
    rule_type: Optional[str] = Query(None, description="Filter by rule type (VALIDATION, THRESHOLD, etc.)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (EXTRACTED, EXPLAINED, REVIEWED, REJECTED)"),
    q: Optional[str] = Query(None, description="Search query"),
    session: AsyncSession = Depends(get_async_session),
) -> list[BusinessRuleResponse]:
    """List business rule candidates for an analysis run with optional filtering."""
    stmt = select(BusinessRule).where(BusinessRule.analysis_id == analysis_id)

    if rule_type:
        try:
            rt_enum = RuleType(rule_type.upper())
            stmt = stmt.where(BusinessRule.rule_type == rt_enum)
        except ValueError:
            pass

    if status_filter:
        try:
            st_enum = RuleStatus(status_filter.upper())
            stmt = stmt.where(BusinessRule.status == st_enum)
        except ValueError:
            pass

    if q:
        query_str = f"%{q}%"
        stmt = stmt.where(
            BusinessRule.title.ilike(query_str)
            | BusinessRule.condition_expression.ilike(query_str)
            | BusinessRule.relative_file_path.ilike(query_str)
        )

    stmt = stmt.order_by(BusinessRule.line_start.asc())
    res = await session.execute(stmt)
    rules = res.scalars().all()
    return [BusinessRuleResponse.model_validate(r) for r in rules]


@router.get(
    "/analysis/{analysis_id}/business-rules/{rule_id}",
    response_model=BusinessRuleResponse,
    summary="Get rule details",
)
@router.get(
    "/business-rules/{rule_id}",
    response_model=BusinessRuleResponse,
    summary="Get rule details alias",
)
async def get_business_rule(
    rule_id: str,
    analysis_id: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
) -> BusinessRuleResponse:
    """Get full details, facts, source evidence, and AI explanation for a single rule."""
    stmt = select(BusinessRule).where(BusinessRule.id == rule_id)
    if analysis_id:
        stmt = stmt.where(BusinessRule.analysis_id == analysis_id)

    res = await session.execute(stmt)
    rule = res.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business rule '{rule_id}' not found",
        )

    return BusinessRuleResponse.model_validate(rule)


@router.post(
    "/business-rules/{rule_id}/explain",
    response_model=AIExplanationResponse,
    summary="Request AI explanation for rule",
)
async def explain_business_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> AIExplanationResponse:
    """Requests an AI explanation via the central AI Gateway for deterministic rule context."""
    stmt = select(BusinessRule).where(BusinessRule.id == rule_id)
    res = await session.execute(stmt)
    rule = res.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business rule '{rule_id}' not found",
        )

    rule.ai_explanation_status = AIExplanationStatus.PENDING
    await session.commit()

    rule_context = {
        "rule_type": rule.rule_type if isinstance(rule.rule_type, str) else rule.rule_type.value,
        "title": rule.title,
        "condition_expression": rule.condition_expression,
        "action_expression": rule.action_expression,
        "outcome_expression": rule.outcome_expression,
        "threshold_value": rule.threshold_value,
        "threshold_operator": rule.threshold_operator,
        "calculation_formula": rule.calculation_formula,
        "previous_state": rule.previous_state,
        "new_state": rule.new_state,
        "file": rule.relative_file_path,
        "lines": f"{rule.line_start}-{rule.line_end}",
    }

    success, explanation_str = await ai_gateway.generate_rule_explanation(rule_context)

    if success:
        rule.ai_explanation = explanation_str
        rule.ai_explanation_status = AIExplanationStatus.COMPLETED
        if rule.status == RuleStatus.EXTRACTED:
            rule.status = RuleStatus.EXPLAINED
    else:
        rule.ai_explanation = None
        rule.ai_explanation_status = AIExplanationStatus.FAILED

    await session.commit()
    await session.refresh(rule)

    return AIExplanationResponse(
        rule_id=rule.id,
        status=rule.ai_explanation_status,
        explanation=rule.ai_explanation,
        error_message=explanation_str if not success else None,
    )


@router.post(
    "/business-rules/{rule_id}/review",
    response_model=BusinessRuleResponse,
    summary="Review or reject rule candidate",
)
async def review_business_rule(
    rule_id: str,
    body: RuleReviewRequest,
    session: AsyncSession = Depends(get_async_session),
) -> BusinessRuleResponse:
    """Updates status to REVIEWED or REJECTED with audit notes."""
    if body.status not in (RuleStatus.REVIEWED, RuleStatus.REJECTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'REVIEWED' or 'REJECTED'",
        )

    stmt = select(BusinessRule).where(BusinessRule.id == rule_id)
    res = await session.execute(stmt)
    rule = res.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business rule '{rule_id}' not found",
        )

    rule.status = body.status
    rule.reviewed_by = body.reviewed_by or "engineer"
    rule.review_notes = body.review_notes
    rule.reviewed_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(rule)

    return BusinessRuleResponse.model_validate(rule)
