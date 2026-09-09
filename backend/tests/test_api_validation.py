"""
LEGACYX — Validation API Integration Tests (Phase 9).

Tests all REST endpoints in app/api/validation.py.
"""

import pytest
from httpx import AsyncClient

from app.models.transformation import TransformationProposal


@pytest.mark.asyncio
async def test_validation_api_endpoints(async_client: AsyncClient, async_session, sample_repository):
    """Tests running, retrieving, listing, reviewing, and explaining validation runs via API."""
    # 1. Create approved proposal
    proposal = TransformationProposal(
        plan_id="plan_api_val_1",
        task_id="task_api_val_1",
        analysis_id="analysis_val_1",
        repository_id=sample_repository.id,
        status="APPROVED",
        transformation_type="FACADE_EXTRACTION",
        target_entity="AccountServiceFacade",
        summary="Test facade proposal for API tests",
        rule_ids=["BR-001", "BR-002"],
        ai_proposal_status="COMPLETED",
    )
    async_session.add(proposal)
    await async_session.commit()


    # 2. Trigger validation run
    resp = await async_client.post(f"/api/v1/transformations/{proposal.id}/validation/run")
    assert resp.status_code == 201
    run_data = resp.json()
    run_id = run_data["id"]
    assert run_data["transformation_proposal_id"] == proposal.id
    assert "build_status" in run_data
    assert "test_status" in run_data
    assert "behavioral_status" in run_data

    # 3. List validation runs for proposal
    resp_list = await async_client.get(f"/api/v1/transformations/{proposal.id}/validation")
    assert resp_list.status_code == 200
    runs_list = resp_list.json()
    assert len(runs_list) >= 1

    # 4. Get run details by ID
    resp_detail = await async_client.get(f"/api/v1/validation/{run_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == run_id

    # 5. Get validation evidence logs
    resp_ev = await async_client.get(f"/api/v1/validation/{run_id}/evidence")
    assert resp_ev.status_code == 200
    ev_list = resp_ev.json()
    assert isinstance(ev_list, list)

    # 6. Get behavioral scenarios
    resp_sc = await async_client.get(f"/api/v1/validation/{run_id}/scenarios")
    assert resp_sc.status_code == 200
    sc_list = resp_sc.json()
    assert isinstance(sc_list, list)

    # 7. Record human review
    review_payload = {
        "status": "VALIDATED",
        "user_name": "lead_qa",
        "notes": "Verified empirical outputs match Phase 4 rules cleanly.",
    }
    resp_rev = await async_client.post(f"/api/v1/validation/{run_id}/review", json=review_payload)
    assert resp_rev.status_code == 200
    updated_run = resp_rev.json()
    assert updated_run["status"] == "VALIDATED"
    assert updated_run["reviewed_by"] == "lead_qa"


    # 8. Request AI evidence explanation
    resp_exp = await async_client.post(f"/api/v1/validation/{run_id}/explain")
    assert resp_exp.status_code == 200
    exp_data = resp_exp.json()
    assert "explanation" in exp_data
    assert exp_data["status"] == "COMPLETED"
