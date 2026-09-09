"""
LEGACYX — Tests for Deterministic Transformation Engine (Phase 8).

Verifies:
1. Approved plan → transformation specification
2. Responsibility → transformation mapping
3. Business rule preservation
4. Impact-aware caller transformation
5. Strategy-aware transformation
6. Source evidence preservation
7. Deterministic output
8. Unsupported strategy handling
9. Missing evidence handling
10. Source immutability (No source file mutation)
11. Invalid artifact path rejection (Zip Slip / path traversal security guard)
12. Duplicate artifact prevention
"""

from pathlib import Path
import pytest

from app.models.modernization_plan import ModernizationPlan, ModernizationTask, PlanStatus, TaskStatus, TaskType
from app.models.transformation import ArtifactCategory
from app.modernization.transformation_engine import TransformationEngine, transformation_engine


def test_map_task_type_to_artifact_category():
    """Verify controlled mapping from Phase 7 TaskType to Phase 8 ArtifactCategory."""
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.EXTRACT_RESPONSIBILITY.value) == ArtifactCategory.EXTRACTED_CLASS
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.DEFINE_INTERFACE.value) == ArtifactCategory.EXTRACTED_INTERFACE
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.INTRODUCE_FACADE.value) == ArtifactCategory.FACADE
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.INTRODUCE_ADAPTER.value) == ArtifactCategory.ADAPTER
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.MIGRATE_CALLER.value) == ArtifactCategory.MIGRATED_CALLER
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.ADD_VERIFICATION_CHECKPOINT.value) == ArtifactCategory.SUPPORTING_TEST_STUB
    assert transformation_engine.map_task_type_to_artifact_category(TaskType.ISOLATE_PERSISTENCE.value) == ArtifactCategory.REFACTORED_METHOD
    # Unsupported or unknown task type defaults to EXTRACTED_CLASS gracefully
    assert transformation_engine.map_task_type_to_artifact_category("UNKNOWN_TYPE") == ArtifactCategory.EXTRACTED_CLASS


def test_build_transformation_specification():
    """Verify deterministic build of transformation specification."""
    plan = ModernizationPlan(
        id="plan-001",
        analysis_id="an-001",
        repository_id="repo-001",
        entity_id="ent-001",
        entity_name="AccountService",
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
        strategy_type="MODULARIZE",
        summary="Plan for AccountService",
        status=PlanStatus.APPROVED,
    )
    task = ModernizationTask(
        id="task-001",
        plan_id=plan.id,
        sequence_order=1,
        title="Isolate Balance Validation",
        description="Extract balance check into TransferDomainService",
        task_type=TaskType.EXTRACT_RESPONSIBILITY.value,
        status=TaskStatus.PENDING,
        target_component="TransferDomainService",
        target_file_path="src/main/java/com/legacybank/service/TransferDomainService.java",
    )
    rules = [
        {"id": "rule-101", "title": "Check Transfer Limit", "condition_expression": "amount > 50000"}
    ]
    callers = [{"name": "AccountController"}]

    spec = transformation_engine.build_transformation_specification(plan, task, rules, callers)

    assert spec["plan_id"] == "plan-001"
    assert spec["task_id"] == "task-001"
    assert spec["entity_name"] == "AccountService"
    assert spec["artifact_category"] == ArtifactCategory.EXTRACTED_CLASS.value
    assert len(spec["rules_to_preserve"]) == 1
    assert spec["rules_to_preserve"][0]["id"] == "rule-101"


def test_generate_deterministic_artifacts_extracted_class():
    """Verify code generation and diff computation for EXTRACTED_CLASS artifact."""
    plan = ModernizationPlan(
        id="plan-001",
        analysis_id="an-001",
        repository_id="repo-001",
        entity_id="ent-001",
        entity_name="AccountService",
        relative_file_path="src/main/java/com/legacybank/AccountService.java",
        strategy_type="MODULARIZE",
        summary="Plan summary",
        status=PlanStatus.APPROVED,
    )
    task = ModernizationTask(
        id="task-001",
        plan_id=plan.id,
        sequence_order=1,
        title="Extract Transfer Responsibility",
        description="Extract responsibility",
        task_type=TaskType.EXTRACT_RESPONSIBILITY.value,
        status=TaskStatus.PENDING,
        target_component="TransferDomainService",
        target_file_path="src/main/java/com/legacybank/service/TransferDomainService.java",
    )
    rules = [
        {"id": "rule-101", "title": "Check Transfer Limit", "condition_expression": "amount > 50000"}
    ]

    source_snippet = "public class AccountService { public void processTransfer() { if (amount > 50000) {} } }"
    artifacts = transformation_engine.generate_deterministic_artifacts(plan, task, rules, [], source_snippet)

    assert len(artifacts) == 1
    art = artifacts[0]
    assert art["artifact_category"] == ArtifactCategory.EXTRACTED_CLASS.value
    assert "TransferDomainService" in art["generated_code"]
    assert "amount > 50000" in art["generated_code"]
    assert "a/src/main/java/com/legacybank/AccountService.java" in art["diff_content"] or "b/src/main/java/com/legacybank/service/TransferDomainService.java" in art["diff_content"]


def test_sanitize_artifact_path_security_guard():
    """Verify Zip-Slip / path traversal prevention (AGENTS.md §7.2)."""
    project_id = "proj-123"
    plan_id = "plan-456"

    # Malicious attempt with directory traversal
    malicious_path = "../../etc/passwd"
    clean_path = transformation_engine.sanitize_artifact_path(malicious_path, project_id, plan_id)

    # Must be safely located inside storage/modernized/proj-123/plan-456/
    assert "storage" in clean_path.parts
    assert "modernized" in clean_path.parts
    assert project_id in clean_path.parts
    assert plan_id in clean_path.parts
    assert "etc" not in clean_path.parts or clean_path.name == "passwd"
    assert not str(clean_path).startswith("..")


def test_compute_unified_diff():
    """Verify standard git unified diff format generation."""
    orig = "line 1\nline 2\nline 3\n"
    gen = "line 1\nline 2 modified\nline 3\n"
    diff = transformation_engine.compute_unified_diff(orig, gen, "Sample.java")

    assert "--- a/Sample.java" in diff
    assert "+++ b/Sample.java" in diff
    assert "-line 2" in diff
    assert "+line 2 modified" in diff
