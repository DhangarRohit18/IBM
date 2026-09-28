"""
LEGACYX — Modernization Assurance API Router.

Exposes REST endpoints for:
- Decision Contracts (Feature 2)
- Decision Replay Lab (Feature 3)
- Silent Drift Detection (Feature 4)
- Three-Layer Impact Analysis (Feature 6)
- What-If Simulator (Feature 7)
- Modernization Risk Scorecard (Feature 10)
- Modernization Assurance Report
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.assurance.assurance_report import assurance_report_generator
from app.assurance.contract_engine import contract_engine
from app.assurance.impact_service import three_layer_impact_service
from app.assurance.replay_engine import decision_replay_engine
from app.assurance.risk_scorer import risk_scorer
from app.assurance.what_if_simulator import what_if_simulator
from app.db.base import get_async_session
from app.models.business_rule import BusinessRule
from app.models.decision_replay import DecisionReplayRun, DecisionScenarioResult
from app.schemas.business_rules import BusinessRuleResponse
from app.schemas.decision_assurance import (
    DecisionContractResponse,
    DecisionReplayExecuteRequest,
    DecisionReplayRunResponse,
    DecisionScenarioResultResponse,
    ModernizationAssuranceReportResponse,
    ModernizationRiskScoreResponse,
    ThreeLayerImpactResponse,
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
)

router = APIRouter(prefix="", tags=["Modernization Assurance"])


# ── Decision Contracts ─────────────────────────────────────────────────────────

@router.post(
    "/analysis/{analysis_id}/contracts/generate",
    response_model=list[DecisionContractResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Decision Contracts from Discovered Business Rule DNA",
)
async def generate_contracts(
    analysis_id: str,
    repository_id: str = Query(..., description="Repository ID"),
    db: AsyncSession = Depends(get_async_session),
) -> list[DecisionContractResponse]:
    """Generates implementation-agnostic Decision Contracts from Business Rule DNA."""
    contracts = await contract_engine.generate_contracts_from_rules(
        analysis_id=analysis_id,
        repository_id=repository_id,
        db=db,
    )
    return [DecisionContractResponse.model_validate(c) for c in contracts]


@router.get(
    "/repositories/{repository_id}/contracts",
    response_model=list[DecisionContractResponse],
    summary="List Decision Contracts for Repository",
)
async def list_contracts(
    repository_id: str,
    domain: Optional[str] = Query(None, description="Filter by business domain"),
    db: AsyncSession = Depends(get_async_session),
) -> list[DecisionContractResponse]:
    contracts = await contract_engine.list_contracts(repository_id, domain, db)
    return [DecisionContractResponse.model_validate(c) for c in contracts]


@router.get(
    "/contracts/{contract_id}",
    response_model=DecisionContractResponse,
    summary="Get Decision Contract Details",
)
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> DecisionContractResponse:
    contract = await contract_engine.get_contract(contract_id, db)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract '{contract_id}' not found")
    return DecisionContractResponse.model_validate(contract)


# ── Decision Replay Lab & Silent Drift Detection ───────────────────────────────

@router.post(
    "/repositories/{repository_id}/decision-replay",
    response_model=DecisionReplayRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Decision Replay Session (Legacy vs Modern)",
)
async def execute_decision_replay(
    repository_id: str,
    payload: Optional[DecisionReplayExecuteRequest] = None,
    db: AsyncSession = Depends(get_async_session),
) -> DecisionReplayRunResponse:
    """
    Executes scenarios through legacy and modern execution harnesses.
    Compares decisions, calculations, exceptions, and state transitions to detect silent drift.
    """
    include_drift = payload.include_deliberate_drift if payload else True
    proposal_id = payload.proposal_id if payload else None

    replay_run = await decision_replay_engine.execute_replay_session(
        repository_id=repository_id,
        proposal_id=proposal_id,
        include_deliberate_drift=include_drift,
        db=db,
    )

    # Fetch with loaded scenario results
    stmt = (
        select(DecisionReplayRun)
        .options(selectinload(DecisionReplayRun.results))
        .where(DecisionReplayRun.id == replay_run.id)
    )
    res = await db.execute(stmt)
    full_run = res.scalar_one()
    return DecisionReplayRunResponse.model_validate(full_run)


@router.get(
    "/repositories/{repository_id}/decision-replay",
    response_model=list[DecisionReplayRunResponse],
    summary="List Decision Replay Runs for Repository",
)
async def list_decision_replays(
    repository_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> list[DecisionReplayRunResponse]:
    stmt = (
        select(DecisionReplayRun)
        .options(selectinload(DecisionReplayRun.results))
        .where(DecisionReplayRun.repository_id == repository_id)
        .order_by(DecisionReplayRun.created_at.desc())
    )
    res = await db.execute(stmt)
    runs = res.scalars().all()
    return [DecisionReplayRunResponse.model_validate(r) for r in runs]


@router.get(
    "/decision-replay/{replay_id}",
    response_model=DecisionReplayRunResponse,
    summary="Get Decision Replay Details",
)
async def get_decision_replay(
    replay_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> DecisionReplayRunResponse:
    stmt = (
        select(DecisionReplayRun)
        .options(selectinload(DecisionReplayRun.results))
        .where(DecisionReplayRun.id == replay_id)
    )
    res = await db.execute(stmt)
    replay = res.scalar_one_or_none()
    if not replay:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Replay run '{replay_id}' not found")
    return DecisionReplayRunResponse.model_validate(replay)


@router.get(
    "/decision-scenarios/{scenario_id}",
    response_model=DecisionScenarioResultResponse,
    summary="Get Granular Decision Scenario Details & Drift Root Cause",
)
async def get_decision_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> DecisionScenarioResultResponse:
    stmt = select(DecisionScenarioResult).where(
        (DecisionScenarioResult.id == scenario_id) | (DecisionScenarioResult.scenario_id == scenario_id)
    )
    res = await db.execute(stmt)
    sc = res.scalar_one_or_none()
    if not sc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{scenario_id}' not found")
    return DecisionScenarioResultResponse.model_validate(sc)


@router.post(
    "/decision-scenarios/{scenario_id}/review",
    response_model=DecisionScenarioResultResponse,
    summary="Submit Human Review on Drift Scenario",
)
async def review_drift_scenario(
    scenario_id: str,
    reviewed_by: str = Query("auditor", description="Reviewer identifier"),
    notes: str = Query("", description="Review notes"),
    db: AsyncSession = Depends(get_async_session),
) -> DecisionScenarioResultResponse:
    stmt = select(DecisionScenarioResult).where(
        (DecisionScenarioResult.id == scenario_id) | (DecisionScenarioResult.scenario_id == scenario_id)
    )
    res = await db.execute(stmt)
    sc = res.scalar_one_or_none()
    if not sc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{scenario_id}' not found")

    sc.reviewed = True
    sc.reviewed_by = reviewed_by
    sc.review_notes = notes
    await db.commit()
    await db.refresh(sc)
    return DecisionScenarioResultResponse.model_validate(sc)


# ── Three-Layer Impact Analysis ───────────────────────────────────────────────

@router.get(
    "/analysis/{analysis_id}/impact/three-layer",
    response_model=ThreeLayerImpactResponse,
    summary="Compute Three-Layer Impact Analysis (Code + Business + Behavioral)",
)
async def get_three_layer_impact(
    analysis_id: str,
    target_id: Optional[str] = Query(None, description="Entity or Class ID"),
    db: AsyncSession = Depends(get_async_session),
) -> ThreeLayerImpactResponse:
    impact_data = await three_layer_impact_service.calculate_three_layer_impact(
        analysis_id=analysis_id,
        target_entity_id=target_id,
        db=db,
    )
    return ThreeLayerImpactResponse(**impact_data)


# ── What-If Business Rule Simulator ───────────────────────────────────────────

@router.post(
    "/rules/{rule_id}/what-if",
    response_model=WhatIfSimulationResponse,
    summary="Simulate Business Rule Parameter Change & Projected Blast Radius",
)
async def simulate_rule_what_if(
    rule_id: str,
    payload: WhatIfSimulationRequest,
    db: AsyncSession = Depends(get_async_session),
) -> WhatIfSimulationResponse:
    sim_data = await what_if_simulator.simulate_rule_modification(
        business_rule_id=rule_id,
        modified_parameter=payload.modified_parameter,
        original_value=payload.original_value,
        simulated_value=payload.simulated_value,
        simulated_operator=payload.simulated_operator,
        db=db,
    )
    return WhatIfSimulationResponse(**sim_data)


# ── Modernization Risk Scorecard ──────────────────────────────────────────────

@router.get(
    "/repositories/{repository_id}/risk-score",
    response_model=ModernizationRiskScoreResponse,
    summary="Compute Explainable Modernization Risk Scorecard",
)
async def get_modernization_risk_score(
    repository_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> ModernizationRiskScoreResponse:
    risk_data = await risk_scorer.compute_risk_scorecard(repository_id, db)
    return ModernizationRiskScoreResponse(**risk_data)


# ── Modernization Assurance Report ────────────────────────────────────────────

@router.get(
    "/repositories/{repository_id}/assurance-report",
    response_model=ModernizationAssuranceReportResponse,
    summary="Generate Comprehensive Modernization Assurance Report",
)
async def get_assurance_report(
    repository_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> ModernizationAssuranceReportResponse:
    report_data = await assurance_report_generator.generate_report(repository_id, db)
    return ModernizationAssuranceReportResponse(**report_data)


# ── Business Rule Governance (Lock & Critical Flags) ─────────────────────────

@router.post(
    "/business-rules/{rule_id}/lock",
    response_model=BusinessRuleResponse,
    summary="Lock or Unlock Business Rule",
)
async def toggle_rule_lock(
    rule_id: str,
    locked: bool = Query(True, description="Lock status"),
    db: AsyncSession = Depends(get_async_session),
) -> BusinessRuleResponse:
    stmt = select(BusinessRule).where(BusinessRule.id == rule_id)
    res = await db.execute(stmt)
    rule = res.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule '{rule_id}' not found")
    rule.is_locked = locked
    await db.commit()
    await db.refresh(rule)
    return BusinessRuleResponse.model_validate(rule)


@router.post(
    "/business-rules/{rule_id}/critical",
    response_model=BusinessRuleResponse,
    summary="Mark Business Rule as Mission Critical",
)
async def toggle_rule_critical(
    rule_id: str,
    critical: bool = Query(True, description="Critical status"),
    db: AsyncSession = Depends(get_async_session),
) -> BusinessRuleResponse:
    stmt = select(BusinessRule).where(BusinessRule.id == rule_id)
    res = await db.execute(stmt)
    rule = res.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule '{rule_id}' not found")
    rule.is_critical = critical
    await db.commit()
    await db.refresh(rule)
    return BusinessRuleResponse.model_validate(rule)
