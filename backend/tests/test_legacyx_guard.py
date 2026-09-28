"""
LEGACYX — Tests for LegacyX Guard IDE Extension API.

Tests the 4 capabilities + Mutation Challenge + Ask AI:
- 01 Understand: Business decision discovery & method risk analysis
- 02 Capture: Behavioral baseline freezing
- 03 Change: Blast radius evaluation
- 04 Prove: Dual-harness replay & drift detection
- Mutation Challenge: Controlled drift injection
- Ask LegacyX: Grounded AI reasoning
"""

import pytest


@pytest.mark.asyncio
async def test_guard_analyze_method(async_client):
    """01 Understand: Returns business decisions and risk metadata for method."""
    res = await async_client.post(
        "/api/v1/guard/analyze-method",
        json={"file_path": "FeeCalculation.java", "method_name": "calculateTransferFee"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["business_decisions_found"] == 3
    assert len(data["business_decisions"]) == 3
    decisions = [d["title"] for d in data["business_decisions"]]
    assert "Transfer Fee Calculation" in decisions
    assert "High-Risk Compliance Boundary" in decisions
    assert len(data["dependencies"]) > 0
    assert len(data["affected_apis"]) > 0
    assert data["risk_level"] == "HIGH"


@pytest.mark.asyncio
async def test_guard_create_baseline(async_client):
    """02 Capture: Freezes canonical execution paths into immutable baseline."""
    res = await async_client.post(
        "/api/v1/guard/create-baseline",
        json={"file_path": "FeeCalculation.java", "method_name": "calculateTransferFee"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BASE_FROZEN"
    assert data["scenarios_captured"] == 7
    assert "4f9a0c2188b1ec45d3e098a12903fe45b8" in data["fingerprint"]
    assert len(data["scenarios"]) == 7


@pytest.mark.asyncio
async def test_guard_change_impact(async_client):
    """03 Change: Blast radius evaluation across decisions, scenarios, services, and APIs."""
    res = await async_client.post(
        "/api/v1/guard/change-impact",
        json={"file_path": "FeeCalculation.java", "method_name": "calculateTransferFee"},
    )
    assert res.status_code == 200
    data = res.json()
    blast = data["blast_radius"]
    assert blast["business_decisions_affected"] == 3
    assert blast["behavioral_scenarios_affected"] == 7
    assert "TransferService" in blast["downstream_services_affected"]
    assert len(blast["public_apis_affected"]) == 2


@pytest.mark.asyncio
async def test_guard_verify_change_preservation(async_client):
    """04 Prove: When unmutated, returns 100% equivalence across 7 scenarios."""
    res = await async_client.post(
        "/api/v1/guard/verify-change",
        json={"file_path": "FeeCalculation.java", "method_name": "calculateTransferFee", "override_mutation": False},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BEHAVIORALLY_EQUIVALENT"
    assert data["overall_equivalence"] is True
    assert data["equivalent_count"] == 7
    assert data["drift_count"] == 0
    assert data["hero_drift"] is None


@pytest.mark.asyncio
async def test_guard_verify_change_drift_detected(async_client):
    """04 Prove: When mutated, catches Scenario #04 drift and outputs exact source diff."""
    res = await async_client.post(
        "/api/v1/guard/verify-change",
        json={"file_path": "FeeCalculation.java", "method_name": "calculateTransferFee", "override_mutation": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BEHAVIORAL_DRIFT_DETECTED"
    assert data["overall_equivalence"] is False
    assert data["drift_count"] == 1
    assert data["equivalent_count"] == 6

    hero = data["hero_drift"]
    assert hero["scenario_id"] == "SCEN-04"
    assert hero["transfer_amount"] == "₹50,000"
    assert hero["legacy_runtime"] == "₹250.00"
    assert hero["current_runtime"] == "₹249.99"
    assert hero["difference"] == "₹0.01"
    assert hero["root_cause"]["source_file"] == "FeeCalculation.java"
    assert hero["root_cause"]["line"] == 45
    assert "- BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_UP);" in hero["root_cause"]["diff"]
    assert "+ BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_DOWN);" in hero["root_cause"]["diff"]
    assert "The compiler said this change was valid" in data["wow_quote"]


@pytest.mark.asyncio
async def test_guard_mutation_challenge_toggle(async_client):
    """Mutation Challenge: Toggling controlled drift updates mutation state."""
    # Inject mutation
    res = await async_client.post("/api/v1/guard/inject-drift", json={"enabled": True})
    assert res.status_code == 200
    assert res.json()["is_mutated"] is True
    assert res.json()["active_rounding"] == "HALF_DOWN"

    # Reset mutation
    res2 = await async_client.post("/api/v1/guard/inject-drift", json={"enabled": False})
    assert res2.status_code == 200
    assert res2.json()["is_mutated"] is False
    assert res2.json()["active_rounding"] == "HALF_UP"


@pytest.mark.asyncio
async def test_guard_ask_legacyx(async_client):
    """Ask LegacyX: Responds with grounded evidence on risk questions."""
    res = await async_client.post(
        "/api/v1/guard/ask",
        json={"question": "Why is this method high risk?", "method_name": "calculateTransferFee", "file_path": "FeeCalculation.java"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "HIGH RISK" in data["explanation"]
    assert "AccountService" in data["explanation"]
    assert "evidence_used" in data
