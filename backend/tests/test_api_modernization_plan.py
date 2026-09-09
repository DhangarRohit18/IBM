"""
LEGACYX — Tests for Modernization Execution Plan API Endpoints (Phase 7).

Verifies:
1. POST /api/v1/analysis/{analysis_id}/modernization/plans/generate
2. GET  /api/v1/analysis/{analysis_id}/modernization/plans
3. GET  /api/v1/modernization/plans/{id}
4. GET  /api/v1/modernization/plans/{id}/tasks
5. POST /api/v1/modernization/plans/{id}/review
6. POST /api/v1/modernization/tasks/{id}/status
7. POST /api/v1/modernization/tasks/{id}/reorder
8. POST /api/v1/modernization/plans/{id}/explain
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_run import AnalysisRun, AnalysisRunStatus
from app.models.business_rule import BusinessRule, RuleStatus, RuleType
from app.models.code_entity import CodeEntity, ComponentType, EntityType
from app.models.modernization_plan import ModernizationPlan, ModernizationTask, PlanStatus, TaskStatus
from app.models.project import Project
from app.models.repository import Repository, RepositoryStatus


@pytest.mark.asyncio
async def test_modernization_plan_api_e2e_flow(async_client: AsyncClient, async_session: AsyncSession):
    """Full API integration test for Phase 7 Modernization Plan endpoints."""
    # 1. Setup Database Fixtures
    project = Project(name="Plan Test Project", description="Test Project", owner_id="user-123")
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

    analysis = AnalysisRun(
        repository_id=repo.id,
        status=AnalysisRunStatus.COMPLETED,
    )
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
        title="Transfer Limit Check",
        condition_expression="amount > 50000",
        threshold_value="50000",
        threshold_operator=">",
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
        line_start=35,
        line_end=40,
        source_construct="if (amount > 50000)",
        extraction_reason="Observed threshold check",
        status=RuleStatus.EXTRACTED,
    )
    async_session.add(rule)
    await async_session.commit()

    # 2. Trigger Plan Generation
    res_gen = await async_client.post(f"/api/v1/analysis/{analysis.id}/modernization/plans/generate")
    assert res_gen.status_code == 201
    plans_data = res_gen.json()
    assert len(plans_data) == 1
    plan_id = plans_data[0]["id"]
    assert plans_data[0]["entity_name"] == "AccountService"
    assert len(plans_data[0]["tasks"]) > 0

    # 3. List Plans
    res_list = await async_client.get(f"/api/v1/analysis/{analysis.id}/modernization/plans")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 4. Get Plan Detail
    res_detail = await async_client.get(f"/api/v1/modernization/plans/{plan_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["id"] == plan_id
    assert len(detail_data["rules_to_preserve"]) == 1

    # 5. Get Plan Tasks
    res_tasks = await async_client.get(f"/api/v1/modernization/plans/{plan_id}/tasks")
    assert res_tasks.status_code == 200
    tasks_list = res_tasks.json()
    assert len(tasks_list) > 0
    first_task_id = tasks_list[0]["id"]

    # 6. Update Task Status
    res_task_stat = await async_client.post(
        f"/api/v1/modernization/tasks/{first_task_id}/status",
        json={"status": "COMPLETED"},
    )
    assert res_task_stat.status_code == 200
    assert res_task_stat.json()["status"] == "COMPLETED"

    # 7. Reorder Task
    res_reorder = await async_client.post(
        f"/api/v1/modernization/tasks/{first_task_id}/reorder",
        json={"new_sequence_order": 2},
    )
    assert res_reorder.status_code == 200
    reordered_list = res_reorder.json()
    assert reordered_list[1]["id"] == first_task_id

    # 8. Human Review Plan
    res_review = await async_client.post(
        f"/api/v1/modernization/plans/{plan_id}/review",
        json={"status": "APPROVED", "user_name": "lead_architect", "notes": "Plan approved for execution"},
    )
    assert res_review.status_code == 200
    assert res_review.json()["status"] == "APPROVED"
    assert res_review.json()["reviewed_by"] == "lead_architect"

    # 9. Request AI Explanation
    res_explain = await async_client.post(f"/api/v1/modernization/plans/{plan_id}/explain")
    assert res_explain.status_code == 200
    assert res_explain.json()["status"] == "COMPLETED"
    assert "Narrative" in res_explain.json()["explanation"] or "watsonx" in res_explain.json()["explanation"]
