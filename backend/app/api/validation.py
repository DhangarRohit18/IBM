"""
LEGACYX — Phase 9 Validation & Behavioral Equivalence Router (AGENTS.md §5, ADR-013).

Provides API endpoints for running isolated build, test, and behavioral equivalence checks,
inspecting execution evidence, reviewing scenario comparisons, and human-in-the-loop review.
"""

from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.ai.gateway import ai_gateway
from app.core.logging import get_logger
from app.db.base import get_async_session
from app.models.transformation import TransformationProposal

from app.models.validation import (
    BehavioralScenario,
    ValidationEvidence,
    ValidationRun,
)
from app.schemas.modernization import (
    BehavioralScenarioResponse,
    ValidationEvidenceResponse,
    ValidationExplainResponse,
    ValidationReviewRequest,
    ValidationRunResponse,
)
from app.validation.validation_engine import run_validation_pipeline

logger = get_logger(__name__)

router = APIRouter(tags=["Validation & Equivalence"])


@router.post(
    "/transformations/{proposal_id}/validation/run",
    response_model=ValidationRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Build, Test & Behavioral Validation Run",
)
async def create_validation_run(
    proposal_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> ValidationRunResponse:
    """
    Executes an empirical validation pipeline for an approved Transformation Proposal (Phase 9).
    Never modifies original legacy source in storage/extracted/ or original Phase 8 artifacts.
    Executes within an isolated validation workspace.
    """
    # Fetch transformation proposal
    prop_stmt = select(TransformationProposal).where(TransformationProposal.id == proposal_id)
    prop_res = await db.execute(prop_stmt)
    proposal = prop_res.scalar_one_or_none()

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transformation proposal '{proposal_id}' not found.",
        )

    # Execute isolated validation pipeline
    validation_run = await run_validation_pipeline(proposal.id, db)

    # Fetch loaded run with relations
    run_stmt = (
        select(ValidationRun)
        .options(
            selectinload(ValidationRun.evidences),
            selectinload(ValidationRun.scenarios),
        )
        .where(ValidationRun.id == validation_run.id)
    )
    run_res = await db.execute(run_stmt)
    run_obj = run_res.scalar_one()

    return ValidationRunResponse.model_validate(run_obj)


@router.get(
    "/transformations/{proposal_id}/validation",
    response_model=list[ValidationRunResponse],
    summary="List Validation Runs for Transformation Proposal",
)
async def list_validation_runs(
    proposal_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> list[ValidationRunResponse]:
    """Lists all validation runs associated with a transformation proposal."""
    stmt = (
        select(ValidationRun)
        .options(
            selectinload(ValidationRun.evidences),
            selectinload(ValidationRun.scenarios),
        )
        .where(ValidationRun.transformation_proposal_id == proposal_id)
        .order_by(ValidationRun.created_at.desc())
    )
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [ValidationRunResponse.model_validate(r) for r in runs]


@router.get(
    "/validation/{run_id}",
    response_model=ValidationRunResponse,
    summary="Get Validation Run Details",
)
async def get_validation_run(
    run_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> ValidationRunResponse:
    """Retrieves detailed record of a validation run."""
    stmt = (
        select(ValidationRun)
        .options(
            selectinload(ValidationRun.evidences),
            selectinload(ValidationRun.scenarios),
        )
        .where(ValidationRun.id == run_id)
    )
    result = await db.execute(stmt)
    run_obj = result.scalar_one_or_none()

    if not run_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation run '{run_id}' not found.",
        )

    return ValidationRunResponse.model_validate(run_obj)


@router.get(
    "/validation/{run_id}/evidence",
    response_model=list[ValidationEvidenceResponse],
    summary="Get Validation Evidence Log Entries",
)
async def get_validation_evidence(
    run_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> list[ValidationEvidenceResponse]:
    """Retrieves empirical execution evidence records (stdout, stderr, exit codes, commands) for a run."""
    stmt = select(ValidationEvidence).where(ValidationEvidence.validation_run_id == run_id).order_by(ValidationEvidence.created_at.asc())
    result = await db.execute(stmt)
    evidences = result.scalars().all()

    return [ValidationEvidenceResponse.model_validate(ev) for ev in evidences]


@router.get(
    "/validation/{run_id}/scenarios",
    response_model=list[BehavioralScenarioResponse],
    summary="Get Behavioral Equivalence Scenarios",
)
async def get_validation_scenarios(
    run_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> list[BehavioralScenarioResponse]:
    """Retrieves scenario comparison results comparing legacy and modern behavior for authoritative business rules."""
    stmt = select(BehavioralScenario).where(BehavioralScenario.validation_run_id == run_id).order_by(BehavioralScenario.created_at.asc())
    result = await db.execute(stmt)

    scenarios = result.scalars().all()

    return [BehavioralScenarioResponse.model_validate(sc) for sc in scenarios]


@router.post(
    "/validation/{run_id}/review",
    response_model=ValidationRunResponse,
    summary="Record Human Verification / Review Decision",
)
async def review_validation_run(
    run_id: str,
    req: ValidationReviewRequest,
    db: AsyncSession = Depends(get_async_session),
) -> ValidationRunResponse:
    """
    Submits human audit review for a validation run.
    Even if build and tests pass, human review remains the mandatory state gate (AGENTS.md §4.5).
    """
    stmt = (
        select(ValidationRun)
        .options(
            selectinload(ValidationRun.evidences),
            selectinload(ValidationRun.scenarios),
        )
        .where(ValidationRun.id == run_id)
    )
    result = await db.execute(stmt)
    run_obj = result.scalar_one_or_none()

    if not run_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation run '{run_id}' not found.",
        )

    valid_statuses = {"REVIEWED", "VALIDATED"}
    if req.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid review status '{req.status}'. Must be one of {valid_statuses}.",
        )

    run_obj.status = req.status
    run_obj.reviewed_by = req.user_name
    run_obj.reviewed_at = datetime.now(timezone.utc)
    if req.notes:
        run_obj.review_notes = req.notes

    await db.commit()
    await db.refresh(run_obj)

    return ValidationRunResponse.model_validate(run_obj)


@router.post(
    "/validation/{run_id}/explain",
    response_model=ValidationExplainResponse,
    summary="Generate AI Explanation of Empirical Validation Evidence",
)
async def explain_validation_run(
    run_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> ValidationExplainResponse:
    """
    Generates an AI explanation of validation evidence through central AI Gateway.
    Does NOT modify overall status or claim verification without empirical facts.
    """
    stmt = select(ValidationRun).where(ValidationRun.id == run_id)
    result = await db.execute(stmt)
    run_obj = result.scalar_one_or_none()

    if not run_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation run '{run_id}' not found.",
        )

    sc_stmt = select(BehavioralScenario).where(BehavioralScenario.validation_run_id == run_id)
    sc_res = await db.execute(sc_stmt)
    scenarios = sc_res.scalars().all()

    passed = sum(1 for s in scenarios if str(s.comparison_result) == "MATCH")
    failed = sum(1 for s in scenarios if str(s.comparison_result) == "MISMATCH")
    total = len(scenarios)

    context = {
        "run_id": run_obj.id,
        "build_status": run_obj.build_status,
        "test_status": run_obj.test_status,
        "behavioral_status": run_obj.behavioral_status,
        "overall_status": run_obj.overall_status,
        "passed_scenarios": passed,
        "failed_scenarios": failed,
        "total_scenarios": total,
    }

    success, explanation = await ai_gateway.generate_validation_explanation(context)

    if success:
        run_obj.ai_explanation = explanation
        run_obj.ai_explanation_status = "COMPLETED"
        await db.commit()
        return ValidationExplainResponse(explanation=explanation, status="COMPLETED")
    else:
        run_obj.ai_explanation_status = "FAILED"
        await db.commit()
        return ValidationExplainResponse(explanation=explanation, status="FAILED")
