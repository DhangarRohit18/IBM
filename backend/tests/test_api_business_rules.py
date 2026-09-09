"""
API endpoint tests for Phase 4 Business Logic Recovery routes.
"""

from pathlib import Path
import pytest
from app.models.business_rule import BusinessRule, RuleStatus, RuleType

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_api_business_rules_lifecycle(async_client, async_session, sample_project, sample_repository):
    # Set extracted_path on repository for testing
    sample_repository.extracted_path = str(FIXTURES_DIR)
    async_session.add(sample_repository)
    await async_session.commit()

    # 1. Trigger System X-Ray Analysis (which automatically runs BusinessRuleExtractor)
    res_analysis = await async_client.post(f"/api/v1/repositories/{sample_repository.id}/analysis")
    assert res_analysis.status_code == 201
    run_data = res_analysis.json()
    analysis_id = run_data["id"]

    # 2. List Business Rules
    res_rules = await async_client.get(f"/api/v1/analysis/{analysis_id}/business-rules")
    assert res_rules.status_code == 200
    rules = res_rules.json()
    assert len(rules) >= 4

    first_rule = rules[0]
    rule_id = first_rule["id"]

    # 3. Get Rule Detail View
    res_detail = await async_client.get(f"/api/v1/business-rules/{rule_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == rule_id
    assert "source_construct" in detail
    assert "rule_trace" in detail

    # 4. Request AI Explanation
    res_explain = await async_client.post(f"/api/v1/business-rules/{rule_id}/explain")
    assert res_explain.status_code == 200
    explain_data = res_explain.json()
    assert explain_data["status"] == "COMPLETED"
    assert explain_data["explanation"] is not None

    # 5. Review Rule
    res_review = await async_client.post(
        f"/api/v1/business-rules/{rule_id}/review",
        json={"status": "REVIEWED", "reviewed_by": "lead_engineer", "review_notes": "Verified against specs"}
    )
    assert res_review.status_code == 200
    reviewed_rule = res_review.json()
    assert reviewed_rule["status"] == "REVIEWED"
    assert reviewed_rule["reviewed_by"] == "lead_engineer"
