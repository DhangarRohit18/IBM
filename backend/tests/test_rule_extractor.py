"""
Unit tests for Phase 4 Deterministic Business Rule Extractor.
"""

from pathlib import Path
import javalang
import pytest

from app.analysis_engine.rule_extractor import BusinessRuleExtractor
from app.models.business_rule import RuleType, RuleStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


def test_extract_rules_from_legacy_bank_account_service():
    account_service_path = FIXTURES_DIR / "src" / "main" / "java" / "com" / "legacybank" / "service" / "AccountService.java"
    content = account_service_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    ast_tree = javalang.parse.parse(content)
    extractor = BusinessRuleExtractor()

    rules = extractor.extract_rules_from_ast(
        analysis_id="test_analysis_1",
        repository_id="test_repo_1",
        entity_id="test_entity_1",
        method_id=None,
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        ast_tree=ast_tree,
        file_lines=lines,
    )

    assert len(rules) >= 4

    rule_types = {r["rule_type"] for r in rules}
    assert RuleType.VALIDATION in rule_types
    assert RuleType.THRESHOLD in rule_types
    assert RuleType.CALCULATION in rule_types
    assert RuleType.STATE_TRANSITION in rule_types or RuleType.ACTION in rule_types

    # Test Threshold Rule specifics (amount > 50000)
    threshold_rule = next(r for r in rules if r["threshold_value"] == "50000")
    assert threshold_rule["threshold_operator"] == ">"
    assert threshold_rule["rule_type"] == RuleType.THRESHOLD
    assert "amount > 50000" in threshold_rule["condition_expression"]
    assert threshold_rule["action_expression"] == "requireManagerApproval()"

    # Test Validation Rule specifics
    val_rule = next(r for r in rules if r["rule_type"] == RuleType.VALIDATION)
    cond_expr = val_rule["condition_expression"].lower()
    assert any(k in cond_expr for k in ["balance", "blocked", "fraud", "amount", "valid"])
    assert val_rule["status"] == RuleStatus.EXTRACTED


    # Test Rule Trace Structure
    assert len(threshold_rule["rule_trace"]) >= 2
    step_types = [s["step_type"] for s in threshold_rule["rule_trace"]]
    assert "CONDITION" in step_types
    assert "DECISION_CONTEXT" in step_types


def test_rule_extractor_deduplication():
    extractor = BusinessRuleExtractor()
    raw = [
        {
            "relative_file_path": "Test.java",
            "line_start": 10,
            "rule_type": RuleType.THRESHOLD,
            "condition_expression": "x > 100",
            "title": "Dup 1",
        },
        {
            "relative_file_path": "Test.java",
            "line_start": 10,
            "rule_type": RuleType.THRESHOLD,
            "condition_expression": "x > 100",
            "title": "Dup 2",
        },
        {
            "relative_file_path": "Test.java",
            "line_start": 20,
            "rule_type": RuleType.CALCULATION,
            "calculation_formula": "y = x * 2",
            "title": "Unique",
        },
    ]

    deduped = extractor._deduplicate_candidates(raw)
    assert len(deduped) == 2
    assert deduped[0]["title"] == "Dup 1"
    assert deduped[1]["title"] == "Unique"
