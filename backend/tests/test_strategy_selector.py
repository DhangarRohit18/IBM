"""
Unit tests for Phase 6 StrategySelector engine.
"""

import pytest
from app.analysis_engine.strategy_selector import ModernizationStrategyType, strategy_selector


def test_strategy_selector_modularize():
    resps = [
        {"category": "INPUT_VALIDATION"},
        {"category": "BUSINESS_RULE_ENFORCEMENT"},
        {"category": "CALCULATION_DERIVATION"},
        {"category": "PERSISTENCE_MUTATION"},
    ]
    rules = [{"id": "r1", "title": "Rule 1", "rule_type": "VALIDATION"}]
    direct_deps = [{"name": "TransferController"}]
    trans_deps = [{"name": "NotificationService"}]

    res = strategy_selector.select_strategy(
        entity_name="TransferService",
        entity_type="CLASS",
        component_type="SERVICE",
        relative_file_path="src/main/java/com/legacybank/service/TransferService.java",
        responsibilities=resps,
        business_rules=rules,
        impact_summary={},
        direct_dependents=direct_deps,
        transitive_dependents=trans_deps,
    )

    assert res["recommended_strategy"] == ModernizationStrategyType.MODULARIZE.value
    assert res["alternative_strategy"] == ModernizationStrategyType.STRANGLER.value
    assert len(res["decision_trace"]) == 4
    assert len(res["rules_to_preserve"]) == 1


def test_strategy_selector_no_modernization_needed_negative_test():
    # Model entity with 0 rules and 0 responsibilities
    resps = []
    rules = []
    direct_deps = []
    trans_deps = []

    res = strategy_selector.select_strategy(
        entity_name="AccountDTO",
        entity_type="CLASS",
        component_type="MODEL",
        relative_file_path="src/main/java/com/legacybank/model/AccountDTO.java",
        responsibilities=resps,
        business_rules=rules,
        impact_summary={},
        direct_dependents=direct_deps,
        transitive_dependents=trans_deps,
    )

    # Must conclude NO_MODERNIZATION_NEEDED without AI fabrication
    assert res["recommended_strategy"] == ModernizationStrategyType.NO_MODERNIZATION_NEEDED.value
    assert res["alternative_strategy"] is None
    assert "single responsibility" in res["why_recommended"]
