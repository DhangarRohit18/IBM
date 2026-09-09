"""API endpoint tests for Phase 3 System X-Ray routes."""

from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_api_analysis_lifecycle(async_client, async_session, sample_project, sample_repository):
    # Set extracted_path on repository for testing
    sample_repository.extracted_path = str(FIXTURES_DIR)
    async_session.add(sample_repository)
    await async_session.commit()

    # 1. Trigger Analysis (returns 201 Created)
    res = await async_client.post(f"/api/v1/repositories/{sample_repository.id}/analysis")
    assert res.status_code == 201
    run_data = res.json()
    assert run_data["status"] == "COMPLETED"
    analysis_id = run_data["id"]

    # 2. Get Analysis Run
    res_get = await async_client.get(f"/api/v1/analysis/{analysis_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == analysis_id

    # 3. Get Summary
    res_sum = await async_client.get(f"/api/v1/analysis/{analysis_id}/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["total_entities"] >= 8

    # 4. Get Packages
    res_pkg = await async_client.get(f"/api/v1/analysis/{analysis_id}/packages")
    assert res_pkg.status_code == 200
    assert len(res_pkg.json()) > 0

    # 5. Get Classes
    res_cls = await async_client.get(f"/api/v1/analysis/{analysis_id}/classes")
    assert res_cls.status_code == 200
    classes = res_cls.json()
    assert len(classes) >= 8

    # 6. Get Class Detail
    first_class_id = classes[0]["id"]
    res_detail = await async_client.get(f"/api/v1/analysis/{analysis_id}/classes/{first_class_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert "name" in detail
    assert "methods" in detail

    # 7. Get Graph
    res_graph = await async_client.get(f"/api/v1/analysis/{analysis_id}/graph")
    assert res_graph.status_code == 200
    graph = res_graph.json()
    assert len(graph["nodes"]) >= 8

    # 8. Search
    res_search = await async_client.get(f"/api/v1/analysis/{analysis_id}/search?q=Account")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert len(search_data) > 0
