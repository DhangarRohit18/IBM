"""
LEGACYX — Modernization Strategy API Router (Phase 6).

Endpoints:
  POST /api/v1/analysis/{analysis_id}/modernization/evaluate   — Trigger deterministic strategy evaluation
  GET  /api/v1/analysis/{analysis_id}/modernization/strategies  — List evaluated strategies
  GET  /api/v1/modernization/strategies/{id}                    — Inspect detailed strategy & trace
  POST /api/v1/modernization/strategies/{id}/explain             — Request AI Gateway explanation
  POST /api/v1/modernization/strategies/{id}/override            — Record audited human review / override
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.ai.gateway import ai_gateway
from app.analysis_engine.impact_analyzer import ImpactDirection, ImpactTargetType, impact_analyzer
from app.analysis_engine.responsibility_analyzer import responsibility_analyzer
from app.analysis_engine.strategy_selector import strategy_selector
from app.core.storage import LocalStorageProvider
from app.db.base import get_async_session
from app.models.analysis_run import AnalysisRun
from app.models.business_rule import BusinessRule
from app.models.code_entity import CodeEntity
from app.models.modernization_plan import ModernizationPlan, ModernizationTask, PlanStatus, TaskStatus
from app.models.modernization_strategy import ModernizationStrategy, StrategyStatus
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.transformation import (
    ArtifactCategory,
    TransformationArtifact,
    TransformationProposal,
    TransformationStatus,
)
from app.modernization.plan_generator import plan_generator
from app.modernization.transformation_engine import transformation_engine
from app.schemas.modernization import (
    ModernizationPlanResponse,
    ModernizationStrategyResponse,
    ModernizationTaskResponse,
    PlanExplainResponse,
    PlanReviewRequest,
    StrategyExplainResponse,
    StrategyOverrideRequest,
    TaskReorderRequest,
    TaskStatusUpdateRequest,
    TransformationApplyRequest,
    TransformationArtifactResponse,
    TransformationProposalResponse,
    TransformationReviewRequest,
)

router = APIRouter(prefix="", tags=["modernization-strategy"])


@router.post(
    "/analysis/{analysis_id}/modernization/evaluate",
    response_model=list[ModernizationStrategyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Trigger deterministic modernization strategy evaluation",
)
async def evaluate_modernization_strategies(
    analysis_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationStrategyResponse]:
    """
    Evaluates modernization strategies for all discovered entities in an analysis run.
    Consumes System X-Ray entities, AST responsibilities, Phase 4 business rules, and Phase 5 impact surface.
    """
    res_run = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    run = res_run.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis run '{analysis_id}' not found")

    res_repo = await session.execute(select(Repository).where(Repository.id == run.repository_id))
    repo = res_repo.scalar_one_or_none()
    extracted_dir = Path(repo.extracted_path) if repo and repo.extracted_path else None

    res_entities = await session.execute(select(CodeEntity).where(CodeEntity.analysis_id == analysis_id))
    entities = list(res_entities.scalars().all())

    res_rules = await session.execute(select(BusinessRule).where(BusinessRule.analysis_id == analysis_id))
    all_rules = list(res_rules.scalars().all())

    created_strategies: list[ModernizationStrategy] = []

    for entity in entities:
        # 1. Extract AST Responsibilities
        file_lines: list[str] = []
        if extracted_dir and entity.relative_file_path:
            file_path = extracted_dir / entity.relative_file_path
            if file_path.exists():
                file_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()

        responsibilities = responsibility_analyzer.analyze_responsibilities(
            relative_file_path=entity.relative_file_path,
            file_lines=file_lines,
        )

        # 2. Get Phase 4 Business Rules for entity
        entity_rules = [
            {
                "id": r.id,
                "title": r.title,
                "rule_type": r.rule_type if isinstance(r.rule_type, str) else r.rule_type.value,
                "relative_file_path": r.relative_file_path,
                "line_start": r.line_start,
                "condition_expression": r.condition_expression,
            }
            for r in all_rules
            if r.entity_id == entity.id
        ]

        # 3. Get Phase 5 Impact Analysis (Reverse - who depends on this component?)
        impact_data = await impact_analyzer.analyze(
            session=session,
            analysis_id=analysis_id,
            target_type=ImpactTargetType.CLASS,
            target_id=entity.id,
            direction=ImpactDirection.REVERSE,
            max_depth=3,
        )

        direct_dependents = impact_data.get("direct_affected_components", [])
        transitive_dependents = impact_data.get("transitive_affected_components", [])

        # 4. Evaluate Strategy Selector Engine
        strategy_eval = strategy_selector.select_strategy(
            entity_name=entity.name,
            entity_type=entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
            component_type=entity.component_type.value if hasattr(entity.component_type, 'value') else str(entity.component_type),
            relative_file_path=entity.relative_file_path,
            responsibilities=responsibilities,
            business_rules=entity_rules,
            impact_summary=impact_data.get("summary", {}),
            direct_dependents=direct_dependents,
            transitive_dependents=transitive_dependents,
        )

        # 5. Save/Update ModernizationStrategy record
        res_existing = await session.execute(
            select(ModernizationStrategy).where(
                ModernizationStrategy.analysis_id == analysis_id,
                ModernizationStrategy.entity_id == entity.id,
            )
        )
        existing = res_existing.scalar_one_or_none()

        if existing:
            strat_obj = existing
            strat_obj.recommended_strategy = strategy_eval["recommended_strategy"]
            strat_obj.alternative_strategy = strategy_eval["alternative_strategy"]
            strat_obj.why_recommended = strategy_eval["why_recommended"]
            strat_obj.why_alternative = strategy_eval["why_alternative"]
            strat_obj.what_not_to_change = strategy_eval["what_not_to_change"]
            strat_obj.decision_trace = strategy_eval["decision_trace"]
            strat_obj.observed_responsibilities = strategy_eval["observed_responsibilities"]
            strat_obj.rules_to_preserve = strategy_eval["rules_to_preserve"]
            strat_obj.impact_summary = strategy_eval["impact_summary"]
            strat_obj.qualitative_comparison = strategy_eval["qualitative_comparison"]
        else:
            strat_obj = ModernizationStrategy(
                analysis_id=analysis_id,
                repository_id=run.repository_id,
                entity_id=entity.id,
                entity_name=entity.name,
                relative_file_path=entity.relative_file_path,
                recommended_strategy=strategy_eval["recommended_strategy"],
                alternative_strategy=strategy_eval["alternative_strategy"],
                why_recommended=strategy_eval["why_recommended"],
                why_alternative=strategy_eval["why_alternative"],
                what_not_to_change=strategy_eval["what_not_to_change"],
                decision_trace=strategy_eval["decision_trace"],
                observed_responsibilities=strategy_eval["observed_responsibilities"],
                rules_to_preserve=strategy_eval["rules_to_preserve"],
                impact_summary=strategy_eval["impact_summary"],
                qualitative_comparison=strategy_eval["qualitative_comparison"],
                status=StrategyStatus.PROPOSED,
            )
            session.add(strat_obj)

        created_strategies.append(strat_obj)

    await session.commit()
    return [ModernizationStrategyResponse.model_validate(s) for s in created_strategies]


@router.get(
    "/analysis/{analysis_id}/modernization/strategies",
    response_model=list[ModernizationStrategyResponse],
    summary="List evaluated component modernization strategies",
)
async def list_modernization_strategies(
    analysis_id: str,
    strategy_type: Optional[str] = Query(None, description="Filter by strategy (MODULARIZE, EXTRACT_SERVICE, etc.)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PROPOSED, REVIEWED, OVERRIDDEN)"),
    q: Optional[str] = Query(None, description="Search query for component name"),
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationStrategyResponse]:
    """List evaluated component modernization strategies with filtering."""
    stmt = select(ModernizationStrategy).where(ModernizationStrategy.analysis_id == analysis_id)

    if strategy_type:
        stmt = stmt.where(ModernizationStrategy.recommended_strategy == strategy_type.upper())

    if status_filter:
        stmt = stmt.where(ModernizationStrategy.status == status_filter.upper())

    if q:
        stmt = stmt.where(ModernizationStrategy.entity_name.ilike(f"%{q}%"))

    res = await session.execute(stmt)
    strategies = list(res.scalars().all())
    return [ModernizationStrategyResponse.model_validate(s) for s in strategies]


@router.get(
    "/modernization/strategies/{id}",
    response_model=ModernizationStrategyResponse,
    summary="Get detailed modernization strategy and decision trace",
)
async def get_modernization_strategy_detail(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ModernizationStrategyResponse:
    """Inspect detailed modernization strategy, decision trace, and preservation boundaries."""
    res = await session.execute(select(ModernizationStrategy).where(ModernizationStrategy.id == id))
    strat = res.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization strategy '{id}' not found")
    return ModernizationStrategyResponse.model_validate(strat)


@router.post(
    "/modernization/strategies/{id}/explain",
    response_model=StrategyExplainResponse,
    summary="Request AI Gateway explanation for strategy decision trace",
)
async def explain_modernization_strategy(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> StrategyExplainResponse:
    """Requests AI Gateway explanation for established strategy decision trace facts."""
    res = await session.execute(select(ModernizationStrategy).where(ModernizationStrategy.id == id))
    strat = res.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization strategy '{id}' not found")

    context = {
        "target_name": strat.entity_name,
        "recommended_strategy": strat.recommended_strategy,
        "alternative_strategy": strat.alternative_strategy,
        "why_recommended": strat.why_recommended,
        "decision_trace": strat.decision_trace,
        "observed_responsibilities": strat.observed_responsibilities,
        "rules_to_preserve": strat.rules_to_preserve,
    }

    success, explanation = await ai_gateway.generate_strategy_explanation(context)

    strat.ai_explanation = explanation
    strat.ai_explanation_status = "COMPLETED" if success else "FAILED"
    await session.commit()

    return StrategyExplainResponse(
        explanation=explanation,
        status=strat.ai_explanation_status,
    )


@router.post(
    "/modernization/strategies/{id}/override",
    response_model=ModernizationStrategyResponse,
    summary="Record audited human review or override",
)
async def override_modernization_strategy(
    id: str,
    body: StrategyOverrideRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ModernizationStrategyResponse:
    """Records an auditable human review or strategy override."""
    res = await session.execute(select(ModernizationStrategy).where(ModernizationStrategy.id == id))
    strat = res.scalar_one_or_none()
    if not strat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization strategy '{id}' not found")

    try:
        st_enum = StrategyStatus(body.status.upper())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{body.status}'. Allowed: REVIEWED, OVERRIDDEN")

    strat.status = st_enum
    if st_enum == StrategyStatus.OVERRIDDEN:
        if not body.user_override_strategy:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_override_strategy is required when status is OVERRIDDEN")
        strat.user_override_strategy = body.user_override_strategy.upper()

    strat.user_override_by = body.user_name
    strat.user_override_at = datetime.now(timezone.utc)
    strat.user_override_notes = body.notes

    await session.commit()
    return ModernizationStrategyResponse.model_validate(strat)


# ===================================================================
# PHASE 7 — MODERNIZATION EXECUTION PLAN ENDPOINTS
# ===================================================================

@router.post(
    "/analysis/{analysis_id}/modernization/plans/generate",
    response_model=list[ModernizationPlanResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Trigger deterministic modernization execution plan generation",
)
async def generate_modernization_plans(
    analysis_id: str,
    target_entity_id: Optional[str] = Query(None, description="Optional target entity ID to generate plan for"),
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationPlanResponse]:
    """
    Generates deterministic execution plans for components in an analysis run.
    Consumes System X-Ray entities, Phase 4 Business Rules, Phase 5 Impact Surface, and Phase 6 Strategy selections.
    """
    res_run = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    run = res_run.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis run '{analysis_id}' not found")

    res_repo = await session.execute(select(Repository).where(Repository.id == run.repository_id))
    repo = res_repo.scalar_one_or_none()
    extracted_dir = Path(repo.extracted_path) if repo and repo.extracted_path else None

    stmt_entities = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
    if target_entity_id:
        stmt_entities = stmt_entities.where(CodeEntity.id == target_entity_id)

    res_entities = await session.execute(stmt_entities)
    entities = list(res_entities.scalars().all())

    res_rules = await session.execute(select(BusinessRule).where(BusinessRule.analysis_id == analysis_id))
    all_rules = list(res_rules.scalars().all())

    res_strategies = await session.execute(select(ModernizationStrategy).where(ModernizationStrategy.analysis_id == analysis_id))
    strategies_by_entity = {s.entity_id: s for s in res_strategies.scalars().all()}

    created_plans: list[ModernizationPlan] = []

    for entity in entities:
        # Check strategy selection (defaulting if not evaluated yet)
        strat = strategies_by_entity.get(entity.id)
        effective_strategy = strat.user_override_strategy if strat and strat.status == StrategyStatus.OVERRIDDEN and strat.user_override_strategy else (strat.recommended_strategy if strat else "MODULARIZE")

        # 1. Extract AST Responsibilities
        file_lines: list[str] = []
        if extracted_dir and entity.relative_file_path:
            file_path = extracted_dir / entity.relative_file_path
            if file_path.exists():
                file_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()

        responsibilities = responsibility_analyzer.analyze_responsibilities(
            relative_file_path=entity.relative_file_path,
            file_lines=file_lines,
        )

        # 2. Extract Phase 4 Business Rules for entity
        entity_rules = [
            {
                "id": r.id,
                "title": r.title,
                "rule_type": r.rule_type if isinstance(r.rule_type, str) else r.rule_type.value,
                "relative_file_path": r.relative_file_path,
                "line_start": r.line_start,
                "line_end": r.line_end,
                "condition_expression": r.condition_expression,
                "calculation_formula": r.calculation_formula,
            }
            for r in all_rules
            if r.entity_id == entity.id
        ]

        # 3. Extract Phase 5 Impact Analysis (Reverse direct dependents)
        impact_data = await impact_analyzer.analyze(
            session=session,
            analysis_id=analysis_id,
            target_type=ImpactTargetType.CLASS,
            target_id=entity.id,
            direction=ImpactDirection.REVERSE,
            max_depth=3,
        )

        direct_dependents = impact_data.get("direct_affected_components", [])

        # 4. Generate Deterministic Execution Plan
        plan_eval = plan_generator.generate_plan(
            entity_name=entity.name,
            entity_type=entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
            component_type=entity.component_type.value if hasattr(entity.component_type, 'value') else str(entity.component_type),
            relative_file_path=entity.relative_file_path,
            strategy_type=effective_strategy,
            responsibilities=responsibilities,
            business_rules=entity_rules,
            impact_summary=impact_data.get("summary", {}),
            direct_dependents=direct_dependents,
        )

        # 5. Delete existing plan for entity if present (to regenerate cleanly)
        res_existing = await session.execute(
            select(ModernizationPlan).where(
                ModernizationPlan.analysis_id == analysis_id,
                ModernizationPlan.entity_id == entity.id,
            )
        )
        existing_plan = res_existing.scalar_one_or_none()
        if existing_plan:
            await session.delete(existing_plan)
            await session.flush()

        # 6. Save ModernizationPlan & ModernizationTasks
        plan_obj = ModernizationPlan(
            analysis_id=analysis_id,
            repository_id=run.repository_id,
            entity_id=entity.id,
            strategy_id=strat.id if strat else None,
            entity_name=entity.name,
            relative_file_path=entity.relative_file_path,
            strategy_type=effective_strategy,
            summary=plan_eval["summary"],
            status=PlanStatus.PROPOSED,
            rules_to_preserve=plan_eval["rules_to_preserve"],
            impact_summary=plan_eval["impact_summary"],
            verification_checkpoints=plan_eval["verification_checkpoints"],
        )
        session.add(plan_obj)
        await session.flush()

        # Add tasks
        for t_data in plan_eval["tasks"]:
            task_obj = ModernizationTask(
                id=t_data["id"],
                plan_id=plan_obj.id,
                sequence_order=t_data["sequence_order"],
                title=t_data["title"],
                description=t_data["description"],
                task_type=t_data["task_type"],
                status=TaskStatus.PENDING,
                target_component=t_data["target_component"],
                target_file_path=t_data["target_file_path"],
                depends_on_task_ids=t_data["depends_on_task_ids"],
                rule_ids=t_data["rule_ids"],
                evidence_references=t_data["evidence_references"],
                verification_checkpoint=t_data["verification_checkpoint"],
            )
            session.add(task_obj)

        created_plans.append(plan_obj)

    await session.commit()

    # Re-query with eager tasks loading
    res_final = await session.execute(
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.analysis_id == analysis_id)
    )
    plans = list(res_final.scalars().all())
    return [ModernizationPlanResponse.model_validate(p) for p in plans]


@router.get(
    "/analysis/{analysis_id}/modernization/plans",
    response_model=list[ModernizationPlanResponse],
    summary="List generated modernization execution plans",
)
async def list_modernization_plans(
    analysis_id: str,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by plan status (PROPOSED, REVIEWED, APPROVED, REJECTED)"),
    q: Optional[str] = Query(None, description="Search query for component name"),
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationPlanResponse]:
    """List modernization execution plans for an analysis run."""
    stmt = (
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.analysis_id == analysis_id)
    )

    if status_filter:
        stmt = stmt.where(ModernizationPlan.status == status_filter.upper())

    if q:
        stmt = stmt.where(ModernizationPlan.entity_name.ilike(f"%{q}%"))

    res = await session.execute(stmt)
    plans = list(res.scalars().all())
    return [ModernizationPlanResponse.model_validate(p) for p in plans]


@router.get(
    "/modernization/plans/{id}",
    response_model=ModernizationPlanResponse,
    summary="Get detailed modernization execution plan with tasks",
)
async def get_modernization_plan_detail(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ModernizationPlanResponse:
    """Inspect detailed modernization execution plan, task DAG, preservation rules, and checkpoints."""
    res = await session.execute(
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.id == id)
    )
    plan = res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization plan '{id}' not found")
    return ModernizationPlanResponse.model_validate(plan)


@router.get(
    "/modernization/plans/{id}/tasks",
    response_model=list[ModernizationTaskResponse],
    summary="Get ordered execution tasks for a modernization plan",
)
async def get_modernization_plan_tasks(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationTaskResponse]:
    """Get topologically ordered execution tasks for a modernization plan."""
    res = await session.execute(
        select(ModernizationTask)
        .where(ModernizationTask.plan_id == id)
        .order_by(ModernizationTask.sequence_order)
    )
    tasks = list(res.scalars().all())
    return [ModernizationTaskResponse.model_validate(t) for t in tasks]


@router.post(
    "/modernization/plans/{id}/review",
    response_model=ModernizationPlanResponse,
    summary="Record audited human architect plan review",
)
async def review_modernization_plan(
    id: str,
    body: PlanReviewRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ModernizationPlanResponse:
    """Records an auditable human review or approval of a modernization plan."""
    res = await session.execute(
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.id == id)
    )
    plan = res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization plan '{id}' not found")

    try:
        st_enum = PlanStatus(body.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{body.status}'. Allowed: REVIEWED, APPROVED, REJECTED",
        )

    plan.status = st_enum
    plan.reviewed_by = body.user_name
    plan.reviewed_at = datetime.now(timezone.utc)
    plan.review_notes = body.notes

    await session.commit()
    return ModernizationPlanResponse.model_validate(plan)


@router.post(
    "/modernization/tasks/{task_id}/status",
    response_model=ModernizationTaskResponse,
    summary="Update individual modernization task status",
)
async def update_task_status(
    task_id: str,
    body: TaskStatusUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
) -> ModernizationTaskResponse:
    """Updates individual task execution status (PENDING, IN_PROGRESS, COMPLETED, DEFERRED)."""
    res = await session.execute(select(ModernizationTask).where(ModernizationTask.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization task '{task_id}' not found")

    try:
        st_enum = TaskStatus(body.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task status '{body.status}'. Allowed: PENDING, IN_PROGRESS, COMPLETED, DEFERRED, SKIPPED",
        )

    task.status = st_enum
    await session.commit()
    return ModernizationTaskResponse.model_validate(task)


@router.post(
    "/modernization/tasks/{task_id}/reorder",
    response_model=list[ModernizationTaskResponse],
    summary="Reorder modernization task execution sequence",
)
async def reorder_task_sequence(
    task_id: str,
    body: TaskReorderRequest,
    session: AsyncSession = Depends(get_async_session),
) -> list[ModernizationTaskResponse]:
    """Reorders task sequence order within its parent modernization plan."""
    res_task = await session.execute(select(ModernizationTask).where(ModernizationTask.id == task_id))
    task = res_task.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization task '{task_id}' not found")

    res_all = await session.execute(
        select(ModernizationTask)
        .where(ModernizationTask.plan_id == task.plan_id)
        .order_by(ModernizationTask.sequence_order)
    )
    all_tasks = list(res_all.scalars().all())

    # Reorder logic
    all_tasks.remove(task)
    target_idx = max(0, min(body.new_sequence_order - 1, len(all_tasks)))
    all_tasks.insert(target_idx, task)

    for idx, t in enumerate(all_tasks, start=1):
        t.sequence_order = idx

    await session.commit()
    return [ModernizationTaskResponse.model_validate(t) for t in all_tasks]


@router.post(
    "/modernization/plans/{id}/explain",
    response_model=PlanExplainResponse,
    summary="Request AI Gateway explanation for modernization plan",
)
async def explain_modernization_plan(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> PlanExplainResponse:
    """Requests AI Gateway narrative explanation for established plan facts."""
    res = await session.execute(
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.id == id)
    )
    plan = res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization plan '{id}' not found")

    context = {
        "entity_name": plan.entity_name,
        "strategy_type": plan.strategy_type,
        "summary": plan.summary,
        "rules_to_preserve": plan.rules_to_preserve,
        "verification_checkpoints": plan.verification_checkpoints,
        "tasks": [
            {
                "sequence_order": t.sequence_order,
                "title": t.title,
                "task_type": t.task_type,
                "target_component": t.target_component,
            }
            for t in plan.tasks
        ],
    }

    success, explanation = await ai_gateway.generate_plan_explanation(context)

    plan.ai_explanation = explanation
    plan.ai_explanation_status = "COMPLETED" if success else "FAILED"
    await session.commit()

    return PlanExplainResponse(
        explanation=explanation,
        status=plan.ai_explanation_status,
    )


# ==========================================
# Phase 8 — Controlled Code Transformation Endpoints
# ==========================================

@router.post(
    "/modernization/plans/{plan_id}/transformations/propose",
    response_model=list[TransformationProposalResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate evidence-backed code transformation proposals",
)
async def propose_transformations(
    plan_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[TransformationProposalResponse]:
    """
    Generates controlled transformation proposals for approved Phase 7 plan tasks.
    Grounds transformation in Phase 3 AST, Phase 4 Business Rules, and Phase 5 Impact analysis.
    """
    res_plan = await session.execute(
        select(ModernizationPlan)
        .options(selectinload(ModernizationPlan.tasks))
        .where(ModernizationPlan.id == plan_id)
    )
    plan = res_plan.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modernization plan '{plan_id}' not found")

    # Fetch business rules for analysis
    res_rules = await session.execute(
        select(BusinessRule).where(BusinessRule.analysis_id == plan.analysis_id)
    )
    rules = list(res_rules.scalars().all())
    rules_dict = [
        {
            "id": r.id,
            "title": r.title,
            "rule_type": r.rule_type.value if hasattr(r.rule_type, "value") else str(r.rule_type),
            "condition_expression": r.condition_expression or "",
            "line_start": r.line_start,
            "line_end": r.line_end,
        }
        for r in rules
    ]

    # Fetch source file text if available
    source_snippet = ""
    try:
        storage_provider = LocalStorageProvider()
        ext_dir = storage_provider.get_extracted_path(plan.repository_id)
        file_path = ext_dir / plan.relative_file_path
        if file_path.exists() and file_path.is_file():
            source_snippet = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        source_snippet = ""

    created_proposals = []

    for task in plan.tasks:
        # Check if proposal already exists for this task
        res_prop = await session.execute(
            select(TransformationProposal)
            .options(selectinload(TransformationProposal.artifacts))
            .where(TransformationProposal.task_id == task.id)
        )
        existing_prop = res_prop.scalar_one_or_none()
        if existing_prop:
            created_proposals.append(existing_prop)
            continue

        # Build specification
        spec = transformation_engine.build_transformation_specification(
            plan=plan,
            task=task,
            rules=rules_dict,
            impacted_callers=plan.impact_summary.get("direct_dependents", []),
        )

        # Generate deterministic artifacts
        artifacts_data = transformation_engine.generate_deterministic_artifacts(
            plan=plan,
            task=task,
            rules=rules_dict,
            impacted_callers=plan.impact_summary.get("direct_dependents", []),
            source_code_snippet=source_snippet,
        )

        cat = transformation_engine.map_task_type_to_artifact_category(task.task_type)

        # AI Gateway Code Proposal Candidate (Optional proposal metadata)
        ai_success, ai_proposal_text = await ai_gateway.generate_code_proposal({
            "entity_name": plan.entity_name,
            "title": task.title,
            "artifact_category": cat.value,
            "rules_to_preserve": rules_dict,
        })

        prop = TransformationProposal(
            plan_id=plan.id,
            task_id=task.id,
            analysis_id=plan.analysis_id,
            repository_id=plan.repository_id,
            status=TransformationStatus.PROPOSED,
            transformation_type=task.task_type,
            target_entity=task.target_component or plan.entity_name,
            summary=f"Transformation proposal for task: {task.title}",
            specification=spec,
            rule_ids=[r["id"] for r in rules_dict],
            impacted_entity_ids=[],
            ai_proposal_status="COMPLETED" if ai_success else "FAILED",
            ai_proposal_summary=ai_proposal_text,
        )
        session.add(prop)
        await session.flush()

        for art_info in artifacts_data:
            art = TransformationArtifact(
                proposal_id=prop.id,
                artifact_category=art_info["artifact_category"],
                target_file_path=art_info["target_file_path"],
                source_file_path=art_info["source_file_path"],
                source_line_start=art_info["source_line_start"],
                source_line_end=art_info["source_line_end"],
                generated_code=art_info["generated_code"],
                diff_content=art_info["diff_content"],
                rules_preserved=art_info["rules_preserved"],
                evidence_references=art_info["evidence_references"],
            )
            session.add(art)

        created_proposals.append(prop)

    await session.commit()

    # Re-query with eager loading
    res_final = await session.execute(
        select(TransformationProposal)
        .options(selectinload(TransformationProposal.artifacts))
        .where(TransformationProposal.plan_id == plan_id)
    )
    props = list(res_final.scalars().all())
    return [TransformationProposalResponse.model_validate(p) for p in props]


@router.get(
    "/modernization/plans/{plan_id}/transformations",
    response_model=list[TransformationProposalResponse],
    summary="List transformation proposals for a plan",
)
async def list_plan_transformations(
    plan_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[TransformationProposalResponse]:
    """Lists generated transformation proposals for a modernization execution plan."""
    res = await session.execute(
        select(TransformationProposal)
        .options(selectinload(TransformationProposal.artifacts))
        .where(TransformationProposal.plan_id == plan_id)
    )
    props = list(res.scalars().all())
    return [TransformationProposalResponse.model_validate(p) for p in props]


@router.get(
    "/transformations/{id}",
    response_model=TransformationProposalResponse,
    summary="Get transformation proposal details",
)
async def get_transformation_detail(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> TransformationProposalResponse:
    """Inspect detailed transformation proposal and associated artifacts."""
    res = await session.execute(
        select(TransformationProposal)
        .options(selectinload(TransformationProposal.artifacts))
        .where(TransformationProposal.id == id)
    )
    prop = res.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transformation proposal '{id}' not found")
    return TransformationProposalResponse.model_validate(prop)


@router.get(
    "/transformations/{id}/artifacts",
    response_model=list[TransformationArtifactResponse],
    summary="Get artifacts for a transformation proposal",
)
async def list_transformation_artifacts(
    id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[TransformationArtifactResponse]:
    """Lists generated target code artifacts and diffs for a transformation proposal."""
    res = await session.execute(
        select(TransformationArtifact).where(TransformationArtifact.proposal_id == id)
    )
    artifacts = list(res.scalars().all())
    return [TransformationArtifactResponse.model_validate(a) for a in artifacts]


@router.post(
    "/transformations/{id}/review",
    response_model=TransformationProposalResponse,
    summary="Record human architect review of transformation proposal",
)
async def review_transformation_proposal(
    id: str,
    body: TransformationReviewRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TransformationProposalResponse:
    """Records audited human review outcome (REVIEWED, APPROVED, REJECTED) for a proposal."""
    res = await session.execute(
        select(TransformationProposal)
        .options(selectinload(TransformationProposal.artifacts))
        .where(TransformationProposal.id == id)
    )
    prop = res.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transformation proposal '{id}' not found")

    try:
        target_status = TransformationStatus(body.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{body.status}'. Allowed: REVIEWED, APPROVED, REJECTED",
        )

    if target_status == TransformationStatus.APPLIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply proposal via review endpoint. Use POST /transformations/{id}/apply",
        )

    prop.status = target_status
    prop.reviewed_by = body.user_name
    prop.reviewed_at = datetime.now(timezone.utc)
    prop.review_notes = body.notes

    await session.commit()
    return TransformationProposalResponse.model_validate(prop)


@router.post(
    "/transformations/{id}/apply",
    response_model=TransformationProposalResponse,
    summary="Apply approved transformation artifacts to isolated storage workspace",
)
async def apply_transformation_proposal(
    id: str,
    body: TransformationApplyRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TransformationProposalResponse:
    """
    Writes approved transformation artifacts into isolated workspace storage (storage/modernized/{project_id}/{plan_id}/).
    Original repository source code is NEVER mutated (AGENTS.md §4.1).
    """
    res = await session.execute(
        select(TransformationProposal)
        .options(selectinload(TransformationProposal.artifacts))
        .where(TransformationProposal.id == id)
    )
    prop = res.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transformation proposal '{id}' not found")

    if prop.status != TransformationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot apply proposal in status '{prop.status}'. Must be APPROVED first.",
        )

    # Fetch project ID via repository
    res_repo = await session.execute(select(Repository).where(Repository.id == prop.repository_id))
    repo = res_repo.scalar_one_or_none()
    project_id = repo.project_id if repo else "default_project"

    workspace_dir = Path("storage") / "modernized" / project_id / prop.plan_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    for art in prop.artifacts:
        sanitized_path = transformation_engine.sanitize_artifact_path(
            art.target_file_path, project_id, prop.plan_id
        )
        sanitized_path.parent.mkdir(parents=True, exist_ok=True)

        with open(sanitized_path, "w", encoding="utf-8") as f:
            f.write(art.generated_code)

        art.storage_relative_path = str(sanitized_path)

    prop.status = TransformationStatus.APPLIED
    prop.applied_by = body.user_name
    prop.applied_at = datetime.now(timezone.utc)
    prop.storage_workspace_path = str(workspace_dir)

    await session.commit()
    return TransformationProposalResponse.model_validate(prop)


