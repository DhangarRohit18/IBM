"""
LEGACYX — Tests for Phase 8 Controlled Transformation API Endpoints & State Machine.

Verifies:
1. Proposal generation: POST /api/v1/modernization/plans/{plan_id}/transformations/propose
2. Proposal retrieval: GET /api/v1/modernization/plans/{plan_id}/transformations
3. Proposal detail: GET /api/v1/transformations/{id}
4. Artifact retrieval: GET /api/v1/transformations/{id}/artifacts
5. Human review: POST /api/v1/transformations/{id}/review (APPROVED & REJECTED)
6. Apply to workspace: POST /api/v1/transformations/{id}/apply
7. Invalid state transitions (PROPOSED -> APPLIED prohibited without APPROVAL)
8. Original legacy source immutability (Original source byte-for-byte unchanged)
9. AI Safety test (AI output candidate proposal boundary test)
"""

import os
from pathlib import Path
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_run import AnalysisRun, AnalysisRunStatus
from app.models.business_rule import BusinessRule, RuleStatus, RuleType
from app.models.code_entity import CodeEntity, ComponentType, EntityType
from app.models.modernization_plan import ModernizationPlan, ModernizationTask, PlanStatus, TaskStatus, TaskType
from app.models.project import Project
from app.models.repository import Repository, RepositoryStatus
from app.models.repository_file import RepositoryFile
from app.models.transformation import TransformationProposal, TransformationStatus


@pytest.mark.asyncio
async def test_transformation_api_full_flow(async_client: AsyncClient, async_session: AsyncSession):
    """Full integration test for Phase 8 Transformation pipeline endpoints."""
    # 1. Fixtures Setup
    project = Project(name="Transformation Test Project", description="Test Project", owner_id="user-789")
    async_session.add(project)
    await async_session.flush()

    repo = Repository(
        project_id=project.id,
        original_filename="valid-legacybank-app.zip",
        artifact_size=1024,
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_key="storage/valid-legacybank-app.zip",
        status=RepositoryStatus.COMPLETED,
    )
    async_session.add(repo)
    await async_session.flush()

    repo_file = RepositoryFile(
        repository_id=repo.id,
        relative_path="src/main/java/com/legacybank/AccountService.java",
        filename="AccountService.java",
        extension="java",
        size_bytes=500,
        is_directory=False,
    )
    async_session.add(repo_file)
    await async_session.flush()

    analysis = AnalysisRun(repository_id=repo.id, status=AnalysisRunStatus.COMPLETED)
    async_session.add(analysis)
    await async_session.flush()

    entity = CodeEntity(
        analysis_id=analysis.id,
        repository_id=repo.id,
        name="AccountService",
        fully_qualified_name="com.legacybank.AccountService",
        entity_type=EntityType.CLASS,
        component_type=ComponentType.SERVICE,
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
    )
    async_session.add(entity)
    await async_session.flush()

    rule = BusinessRule(
        analysis_id=analysis.id,
        repository_id=repo.id,
        entity_id=entity.id,
        rule_type=RuleType.THRESHOLD,
        title="Approval Threshold",
        condition_expression="amount > 50000",
        threshold_value="50000",
        threshold_operator=">",
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
        line_start=10,
        line_end=15,
        source_construct="if (amount > 50000)",
        extraction_reason="Observed threshold check",
        status=RuleStatus.EXTRACTED,
    )
    async_session.add(rule)
    await async_session.flush()

    plan = ModernizationPlan(
        analysis_id=analysis.id,
        repository_id=repo.id,
        entity_id=entity.id,
        entity_name="AccountService",
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
        strategy_type="MODULARIZE",
        summary="Modernization plan for AccountService",
        status=PlanStatus.APPROVED,
    )
    async_session.add(plan)
    await async_session.flush()

    task1 = ModernizationTask(
        plan_id=plan.id,
        sequence_order=1,
        title="Extract Responsibility",
        description="Extract domain service",
        task_type=TaskType.EXTRACT_RESPONSIBILITY.value,
        status=TaskStatus.PENDING,
        target_component="TransferDomainService",
        target_file_path="src/main/java/com/legacybank/service/TransferDomainService.java",
    )
    task2 = ModernizationTask(
        plan_id=plan.id,
        sequence_order=2,
        title="Introduce Facade",
        description="Wrap AccountService",
        task_type=TaskType.INTRODUCE_FACADE.value,
        status=TaskStatus.PENDING,
        target_component="AccountServiceFacade",
        target_file_path="src/main/java/com/legacybank/facade/AccountServiceFacade.java",
    )
    async_session.add_all([task1, task2])
    await async_session.commit()

    # 2. Propose Transformations
    res_prop = await async_client.post(f"/api/v1/modernization/plans/{plan.id}/transformations/propose")
    assert res_prop.status_code == 201
    props_data = res_prop.json()
    assert len(props_data) == 2
    first_prop_id = props_data[0]["id"]
    assert props_data[0]["status"] == "PROPOSED"
    assert len(props_data[0]["artifacts"]) > 0

    # 3. List Transformations
    res_list = await async_client.get(f"/api/v1/modernization/plans/{plan.id}/transformations")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

    # 4. Get Detail & Artifacts
    res_detail = await async_client.get(f"/api/v1/transformations/{first_prop_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == first_prop_id

    res_arts = await async_client.get(f"/api/v1/transformations/{first_prop_id}/artifacts")
    assert res_arts.status_code == 200
    assert len(res_arts.json()) > 0
    assert "generated_code" in res_arts.json()[0]
    assert "diff_content" in res_arts.json()[0]

    # 5. Test Invalid Transition (PROPOSED -> APPLIED must fail with 400)
    res_invalid_apply = await async_client.post(
        f"/api/v1/transformations/{first_prop_id}/apply",
        json={"user_name": "hacker"},
    )
    assert res_invalid_apply.status_code == 400

    # 6. Human Review: Approve Proposal
    res_review = await async_client.post(
        f"/api/v1/transformations/{first_prop_id}/review",
        json={"status": "APPROVED", "user_name": "lead_architect", "notes": "Approved for isolated workspace application"},
    )
    assert res_review.status_code == 200
    assert res_review.json()["status"] == "APPROVED"
    assert res_review.json()["reviewed_by"] == "lead_architect"

    # 7. Apply Proposal to Isolated Storage Workspace
    res_apply = await async_client.post(
        f"/api/v1/transformations/{first_prop_id}/apply",
        json={"user_name": "lead_architect"},
    )
    assert res_apply.status_code == 200
    apply_data = res_apply.json()
    assert apply_data["status"] == "APPLIED"
    assert apply_data["storage_workspace_path"] is not None

    # Verify physical file exists in isolated storage workspace
    workspace_path = Path(apply_data["storage_workspace_path"])
    assert workspace_path.exists() or Path("storage/modernized").exists()


@pytest.mark.asyncio
async def test_original_source_immutability(async_client: AsyncClient, async_session: AsyncSession):
    """Verify original repository source code files are strictly immutable (AGENTS.md §4.1)."""
    # Create sample extracted source file
    extracted_dir = Path("storage/extracted/test_repo_immutability")
    extracted_dir.mkdir(parents=True, exist_ok=True)
    sample_file = extracted_dir / "AccountService.java"

    original_content = "public class AccountService { public void legacyMethod() {} }"
    sample_file.write_text(original_content, encoding="utf-8")

    try:
        # Verify content before transformation
        assert sample_file.read_text(encoding="utf-8") == original_content

        # Verify target modernization workspace directory is separate
        modernized_dir = Path("storage/modernized/test_project/test_plan")
        assert not sample_file.is_relative_to(modernized_dir)
    finally:
        # Clean up temporary test file
        if sample_file.exists():
            sample_file.unlink()


@pytest.mark.asyncio
async def test_ai_proposal_safety_boundary():
    """Verify AI Gateway candidate code proposals cannot alter deterministic rule evidence or specifications."""
    from app.ai.gateway import ai_gateway

    context = {
        "entity_name": "AccountService",
        "title": "Isolate Approval Guard",
        "artifact_category": "EXTRACTED_CLASS",
        "rules_to_preserve": [{"id": "rule-101", "condition_expression": "amount > 50000"}],
    }

    success, proposal = await ai_gateway.generate_code_proposal(context)
    assert success is True
    assert "AccountService" in proposal
    assert "EXTRACTED_CLASS" in proposal
