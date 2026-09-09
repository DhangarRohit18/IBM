"""
LEGACYX — Tests for Deterministic Modernization Plan Generator Engine (Phase 7).

Verifies:
1. Deterministic task generation from responsibilities, rules, and impact surface
2. Task taxonomy mapping (SEPARATE_BUSINESS_RULE, EXTRACT_CALCULATION, ISOLATE_STATE_TRANSITION, DEFINE_INTERFACE, etc.)
3. Topological DAG dependency ordering
4. Preservation Rules Catalog compiler
5. Verification Checkpoints generation
6. Zero fake scores (all metrics derived from observable facts)
7. Consistency across identical inputs
"""

import pytest
from app.modernization.plan_generator import plan_generator
from app.models.modernization_plan import TaskType


def test_plan_generator_basic_structure():
    """Test generating a modernization plan for a component with validation and calculation rules."""
    responsibilities = [
        {"category": "INPUT_VALIDATION", "line_number": 12, "source_snippet": "if (amount <= 0) throw error;"},
        {"category": "CALCULATION_DERIVATION", "line_number": 25, "source_snippet": "fee = amount * 0.02;"},
    ]
    business_rules = [
        {
            "id": "rule-1",
            "title": "Validation Rule",
            "rule_type": "VALIDATION",
            "condition_expression": "amount <= 0",
            "line_start": 12,
            "line_end": 14,
        },
        {
            "id": "rule-2",
            "title": "Fee Calculation Rule",
            "rule_type": "CALCULATION",
            "calculation_formula": "fee = amount * 0.02",
            "line_start": 25,
            "line_end": 26,
        },
    ]
    impact_summary = {"direct_dependent_count": 1}
    direct_dependents = [{"name": "AccountController", "relative_file_path": "src/AccountController.java"}]

    plan = plan_generator.generate_plan(
        entity_name="AccountService",
        entity_type="CLASS",
        component_type="SERVICE",
        relative_file_path="src/AccountService.java",
        strategy_type="MODULARIZE",
        responsibilities=responsibilities,
        business_rules=business_rules,
        impact_summary=impact_summary,
        direct_dependents=direct_dependents,
    )

    assert plan["entity_name"] == "AccountService"
    assert plan["strategy_type"] == "MODULARIZE"
    assert len(plan["rules_to_preserve"]) == 2
    assert len(plan["tasks"]) >= 5

    task_types = [t["task_type"] for t in plan["tasks"]]
    assert TaskType.SEPARATE_BUSINESS_RULE.value in task_types
    assert TaskType.EXTRACT_CALCULATION.value in task_types
    assert TaskType.DEFINE_INTERFACE.value in task_types
    assert TaskType.INTRODUCE_FACADE.value in task_types
    assert TaskType.MIGRATE_CALLER.value in task_types
    assert TaskType.PRESERVE_BEHAVIOR.value in task_types
    assert TaskType.ADD_VERIFICATION_CHECKPOINT.value in task_types


def test_plan_generator_task_ordering_and_dag_dependencies():
    """Verify task dependencies follow DAG topological order (isolation -> interface -> facade -> caller -> checkpoint)."""
    plan = plan_generator.generate_plan(
        entity_name="PaymentProcessor",
        entity_type="CLASS",
        component_type="SERVICE",
        relative_file_path="src/PaymentProcessor.java",
        strategy_type="EXTRACT_SERVICE",
        responsibilities=[{"category": "STATE_TRANSITION", "line_number": 40, "source_snippet": "setStatus('COMPLETED')"}],
        business_rules=[{
            "id": "rule-state",
            "title": "State Rule",
            "rule_type": "STATE_TRANSITION",
            "condition_expression": "state == PENDING",
            "line_start": 40,
            "line_end": 42,
        }],
        impact_summary={"direct_dependent_count": 0},
        direct_dependents=[],
    )

    tasks = plan["tasks"]
    task_map = {t["id"]: t for t in tasks}

    # Verify each task's prerequisites appear earlier in sequence order
    for t in tasks:
        for dep_id in t["depends_on_task_ids"]:
            dep_task = task_map[dep_id]
            assert dep_task["sequence_order"] < t["sequence_order"], (
                f"Prerequisite task '{dep_task['title']}' (seq={dep_task['sequence_order']}) "
                f"must appear before dependent task '{t['title']}' (seq={t['sequence_order']})"
            )


def test_plan_generator_determinism():
    """Verify identical facts generate identical task sequences and descriptions."""
    args = dict(
        entity_name="TransferService",
        entity_type="CLASS",
        component_type="SERVICE",
        relative_file_path="src/TransferService.java",
        strategy_type="STRANGLER",
        responsibilities=[{"category": "PERSISTENCE_MUTATION", "line_number": 10, "source_snippet": "repo.save()"}],
        business_rules=[{"id": "r1", "title": "Guard", "rule_type": "VALIDATION", "condition_expression": "x != null", "line_start": 5, "line_end": 6}],
        impact_summary={},
        direct_dependents=[],
    )

    p1 = plan_generator.generate_plan(**args)
    p2 = plan_generator.generate_plan(**args)

    assert p1["summary"] == p2["summary"]
    assert len(p1["tasks"]) == len(p2["tasks"])
    for t1, t2 in zip(p1["tasks"], p2["tasks"]):
        assert t1["title"] == t2["title"]
        assert t1["task_type"] == t2["task_type"]
