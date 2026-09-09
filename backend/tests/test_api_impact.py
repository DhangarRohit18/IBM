"""
API endpoint tests for Phase 5 Impact Analysis routes.
"""

from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_api_impact_analysis_lifecycle(async_client, async_session, sample_project, sample_repository):
    # Set extracted_path on repository for testing
    sample_repository.extracted_path = str(FIXTURES_DIR)
    async_session.add(sample_repository)
    await async_session.commit()

    # 1. Trigger System X-Ray Analysis
    res_analysis = await async_client.post(f"/api/v1/repositories/{sample_repository.id}/analysis")
    assert res_analysis.status_code == 201
    run_data = res_analysis.json()
    analysis_id = run_data["id"]

    # Fetch entities
    res_entities = await async_client.get(f"/api/v1/analysis/{analysis_id}/classes")
    entities = res_entities.json()
    assert len(entities) > 0
    target_entity = entities[0]


    # 2. Call GET /api/v1/analysis/{analysis_id}/impact (Forward)
    res_impact = await async_client.get(
        f"/api/v1/analysis/{analysis_id}/impact",
        params={
            "target_type": "class",
            "target_id": target_entity["id"],
            "direction": "forward",
            "max_depth": 3,
        },
    )
    assert res_impact.status_code == 200
    impact_data = res_impact.json()
    assert impact_data["analysis_id"] == analysis_id
    assert impact_data["target"]["id"] == target_entity["id"]
    assert impact_data["direction"] == "forward"
    assert "graph" in impact_data
    assert "summary" in impact_data

    # 3. Call GET /api/v1/analysis/{analysis_id}/impact (Reverse)
    res_impact_rev = await async_client.get(
        f"/api/v1/analysis/{analysis_id}/impact",
        params={
            "target_type": "class",
            "target_id": target_entity["id"],
            "direction": "reverse",
            "max_depth": 3,
        },
    )
    assert res_impact_rev.status_code == 200
    assert res_impact_rev.json()["direction"] == "reverse"

    # 4. Call POST /api/v1/impact/explain (AI Gateway)
    res_explain = await async_client.post(
        "/api/v1/impact/explain",
        json={
            "analysis_id": analysis_id,
            "target_type": "class",
            "target_id": target_entity["id"],
            "direction": "forward",
            "max_depth": 3,
        },
    )
    assert res_explain.status_code == 200
    explain_data = res_explain.json()
    assert explain_data["status"] == "COMPLETED"
    assert explain_data["explanation"] is not None
    assert "Impact" in explain_data["explanation"] or "Narrative" in explain_data["explanation"]
