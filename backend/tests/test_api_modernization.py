"""
API endpoint tests for Phase 6 Modernization Strategy routes.
"""

from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_api_modernization_lifecycle(async_client, async_session, sample_project, sample_repository):
    # Set extracted_path on repository for testing
    sample_repository.extracted_path = str(FIXTURES_DIR)
    async_session.add(sample_repository)
    await async_session.commit()

    # 1. Trigger System X-Ray Analysis
    res_analysis = await async_client.post(f"/api/v1/repositories/{sample_repository.id}/analysis")
    assert res_analysis.status_code == 201
    run_data = res_analysis.json()
    analysis_id = run_data["id"]

    # 2. Trigger Strategy Evaluation
    res_eval = await async_client.post(f"/api/v1/analysis/{analysis_id}/modernization/evaluate")
    assert res_eval.status_code == 201
    strategies = res_eval.json()
    assert len(strategies) > 0

    first_strat = strategies[0]
    strat_id = first_strat["id"]
    assert "recommended_strategy" in first_strat
    assert "decision_trace" in first_strat
    assert "observed_responsibilities" in first_strat

    # 3. List Strategies with Filter
    res_list = await async_client.get(f"/api/v1/analysis/{analysis_id}/modernization/strategies")
    assert res_list.status_code == 200
    assert len(res_list.json()) == len(strategies)

    # 4. Get Strategy Detail View
    res_detail = await async_client.get(f"/api/v1/modernization/strategies/{strat_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == strat_id

    # 5. Request AI Explanation (Strict AI Boundary)
    res_explain = await async_client.post(f"/api/v1/modernization/strategies/{strat_id}/explain")
    assert res_explain.status_code == 200
    explain_data = res_explain.json()
    assert explain_data["status"] == "COMPLETED"
    assert explain_data["explanation"] is not None

    # 6. Record Audited Human Override
    res_override = await async_client.post(
        f"/api/v1/modernization/strategies/{strat_id}/override",
        json={
            "status": "OVERRIDDEN",
            "user_override_strategy": "STRANGLER",
            "user_name": "lead_architect",
            "notes": "Overriding to Strangler pattern due to legacy system coexistence requirements",
        },
    )
    assert res_override.status_code == 200
    overridden = res_override.json()
    assert overridden["status"] == "OVERRIDDEN"
    assert overridden["user_override_strategy"] == "STRANGLER"
    assert overridden["user_override_by"] == "lead_architect"
    assert "coexistence" in overridden["user_override_notes"]
