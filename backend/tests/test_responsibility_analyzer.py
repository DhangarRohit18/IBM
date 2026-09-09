"""
Unit tests for Phase 6 ResponsibilityAnalyzer engine.
"""

from pathlib import Path
import pytest
from app.analysis_engine.responsibility_analyzer import ResponsibilityCategory, responsibility_analyzer

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


def test_analyze_responsibilities_from_account_service():
    account_service_path = FIXTURES_DIR / "src" / "main" / "java" / "com" / "legacybank" / "service" / "AccountService.java"
    lines = account_service_path.read_text(encoding="utf-8").splitlines()

    resps = responsibility_analyzer.analyze_responsibilities(
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        file_lines=lines,
    )

    assert len(resps) >= 3

    categories = {r["category"] for r in resps}
    assert ResponsibilityCategory.INPUT_VALIDATION in categories or ResponsibilityCategory.BUSINESS_RULE_ENFORCEMENT in categories
    assert ResponsibilityCategory.PERSISTENCE_MUTATION in categories or ResponsibilityCategory.SERVICE_COORDINATION in categories

    for r in resps:
        assert "title" in r
        assert "line_number" in r
        assert "evidence_reason" in r
        assert "source_snippet" in r
