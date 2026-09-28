"""
LEGACYX — Modernization Assurance Test Suite.

Verifies:
- Business Rule DNA enrichment
- Decision Contract generation & validation
- Decision Replay execution (Legacy vs Modern)
- Silent Business Drift detection (Boundary, Currency precision, Fraud threshold)
- Complete root cause trace: Drift -> Decision -> Rule -> Method -> Diff -> Remediation
- Three-Layer Impact Analysis (Code + Business + Behavioral)
- What-If Business Rule Simulator
- Modernization Risk Scorecard
- Modernization Assurance Report
"""

import pytest
from app.models.business_rule import BusinessRule, RuleStatus, RuleType
from app.models.code_entity import CodeEntity, ComponentType, EntityType
from app.models.project import Project
from app.models.repository import Repository


@pytest.fixture
async def sample_assurance_setup(async_session, sample_repository, sample_project):
    """Sets up an entity and rules on top of sample_repository for assurance testing."""
    repo = sample_repository

    entity = CodeEntity(
        repository_id=repo.id,
        analysis_id="analysis_assur_01",
        name="AccountService",
        fully_qualified_name="com.legacybank.service.AccountService",
        entity_type=EntityType.CLASS,
        component_type=ComponentType.SERVICE,
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
    )
    async_session.add(entity)
    await async_session.flush()

    # Rule 1: High Value Approval Threshold
    rule1 = BusinessRule(
        repository_id=repo.id,
        analysis_id="analysis_assur_01",
        entity_id=entity.id,
        rule_type=RuleType.THRESHOLD,
        title="High Value Transfer Approval",
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        line_start=45,
        line_end=55,
        condition_expression="amount > 50000",
        action_expression="REQUIRES_APPROVAL",
        threshold_value="50000.0",
        threshold_operator=">",
        source_construct="IF_STATEMENT",
        extraction_reason="High value threshold check",
        business_meaning="Enforces transaction threshold policy: requires approval when amount > 50000.",
        inputs=[{"name": "amount", "type": "double", "sample_value": 50000.0}],
        outputs=[{"name": "decision", "value": "REQUIRES_APPROVAL"}],
        dependencies=["AccountRepository", "TransactionValidator"],
        related_apis=["POST /api/v1/accounts/transfer"],
        related_business_processes=["Transaction Approval", "Risk Evaluation"],
        confidence=1.0,
        is_critical=True,
    )

    # Rule 2: Validation Rule
    rule2 = BusinessRule(
        repository_id=repo.id,
        analysis_id="analysis_assur_01",
        entity_id=entity.id,
        rule_type=RuleType.VALIDATION,
        title="Active Account Check",
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        line_start=30,
        line_end=35,
        condition_expression="account.status != ACTIVE",
        action_expression="THROW_EXCEPTION",
        source_construct="IF_STATEMENT",
        extraction_reason="Validation check for active status",
        business_meaning="Guards account operation integrity: halts on inactive or blocked account.",
        confidence=1.0,
        is_critical=True,
    )

    async_session.add_all([rule1, rule2])
    await async_session.commit()

    return {
        "project": sample_project,
        "repository": repo,
        "entity": entity,
        "rules": [rule1, rule2],
        "analysis_id": "analysis_assur_01",
    }


@pytest.mark.asyncio
async def test_decision_contract_generation(async_client, sample_assurance_setup):
    """Test generating Decision Contracts from Business Rule DNA."""
    repo = sample_assurance_setup["repository"]
    analysis_id = sample_assurance_setup["analysis_id"]

    res = await async_client.post(
        f"/api/v1/analysis/{analysis_id}/contracts/generate",
        params={"repository_id": repo.id},
    )
    assert res.status_code == 201
    contracts = res.json()
    assert len(contracts) >= 2

    # Check contract structure
    contract_0 = contracts[0]
    assert "contract_id" in contract_0
    assert "inputs" in contract_0
    assert "conditions" in contract_0
    assert "expected_decision" in contract_0
    assert contract_0["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_decision_replay_and_silent_drift_detection(async_client, sample_assurance_setup):
    """Test running Decision Replay and detecting silent business drift."""
    repo = sample_assurance_setup["repository"]
    analysis_id = sample_assurance_setup["analysis_id"]

    # First generate contracts
    await async_client.post(
        f"/api/v1/analysis/{analysis_id}/contracts/generate",
        params={"repository_id": repo.id},
    )

    # Execute replay
    res = await async_client.post(
        f"/api/v1/repositories/{repo.id}/decision-replay",
        json={"include_deliberate_drift": True},
    )
    assert res.status_code == 201
    replay = res.json()

    assert replay["total_scenarios"] >= 8
    assert replay["preserved_count"] > 0
    assert replay["drift_count"] > 0
    assert replay["status"] == "COMPLETED"

    # Verify scenario results
    results = replay["results"]
    assert len(results) == replay["total_scenarios"]

    # Check boundary drift scenario
    drift_case = next(r for r in results if r["comparison_status"] == "BEHAVIOR_DRIFT")
    assert drift_case is not None
    assert drift_case["drift_type"] in [
        "THRESHOLD_SHIFT",
        "BOUNDARY_CONDITION",
        "CURRENCY_CALCULATION",
        "FRAUD_EVALUATION",
    ]

    # Verify Root Cause Trace Chain: Decision -> Rule -> Method -> Changed Code -> Dependency
    root_cause = drift_case["drift_root_cause"]
    assert "chain_steps" in root_cause
    layers = [step["layer"] for step in root_cause["chain_steps"]]
    assert "DECISION" in layers
    assert "BUSINESS_RULE" in layers
    assert "METHOD" in layers
    assert "TRANSFORMATION_DIFF" in layers

    # Test review of drift scenario
    review_res = await async_client.post(
        f"/api/v1/decision-scenarios/{drift_case['id']}/review",
        params={"reviewed_by": "chief_auditor", "notes": "Audited boundary drift"},
    )
    assert review_res.status_code == 200
    reviewed_sc = review_res.json()
    assert reviewed_sc["reviewed"] is True
    assert reviewed_sc["reviewed_by"] == "chief_auditor"


@pytest.mark.asyncio
async def test_three_layer_impact_analysis(async_client, sample_assurance_setup):
    """Test 3-layer impact analysis: Code + Business + Behavioral."""
    analysis_id = sample_assurance_setup["analysis_id"]
    entity = sample_assurance_setup["entity"]

    res = await async_client.get(
        f"/api/v1/analysis/{analysis_id}/impact/three-layer",
        params={"target_id": entity.id},
    )
    assert res.status_code == 200
    data = res.json()

    # Verify all 3 layers exist
    assert "code_impact" in data
    assert "business_impact" in data
    assert "behavioral_impact" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

    # Verify layer node distribution
    node_layers = {n["layer"] for n in data["nodes"]}
    assert "CODE" in node_layers
    assert "BUSINESS" in node_layers
    assert "BEHAVIORAL" in node_layers


@pytest.mark.asyncio
async def test_what_if_business_rule_simulator(async_client, sample_assurance_setup):
    """Test what-if simulator projecting blast radius when a business threshold changes."""
    rules = sample_assurance_setup["rules"]
    threshold_rule = rules[0]

    res = await async_client.post(
        f"/api/v1/rules/{threshold_rule.id}/what-if",
        json={
            "business_rule_id": threshold_rule.id,
            "modified_parameter": "threshold_value",
            "original_value": "50000",
            "simulated_value": "45000",
            "simulated_operator": ">=",
        },
    )
    assert res.status_code == 200
    sim = res.json()

    assert sim["rule_id"] == threshold_rule.id
    assert sim["original_value"] == "50000"
    assert sim["simulated_value"] == "45000"
    assert len(sim["affected_rules"]) > 0
    assert len(sim["affected_services"]) > 0
    assert len(sim["affected_apis"]) > 0
    assert sim["projected_drift_scenarios"] > 0
    assert sim["projected_drift_rate_pct"] > 0
    assert sim["projected_risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@pytest.mark.asyncio
async def test_modernization_risk_scorecard(async_client, sample_assurance_setup):
    """Test multi-dimensional modernization risk scorecard."""
    repo = sample_assurance_setup["repository"]

    res = await async_client.get(f"/api/v1/repositories/{repo.id}/risk-score")
    assert res.status_code == 200
    scorecard = res.json()

    assert "overall_risk_score" in scorecard
    assert "overall_status" in scorecard
    assert len(scorecard["dimensions"]) == 6
    dims = [d["dimension"] for d in scorecard["dimensions"]]
    assert "Architecture Risk" in dims
    assert "Business Rule Risk" in dims
    assert "Behavioral Drift Risk" in dims
    assert len(scorecard["recommended_actions"]) > 0


@pytest.mark.asyncio
async def test_modernization_assurance_report(async_client, sample_assurance_setup):
    """Test generating comprehensive Modernization Assurance Report."""
    repo = sample_assurance_setup["repository"]

    res = await async_client.get(f"/api/v1/repositories/{repo.id}/assurance-report")
    assert res.status_code == 200
    report = res.json()

    assert "report_id" in report
    assert report["motto"] == "Modernize the Code. Preserve the Decision. Prove the Difference."
    assert "executive_summary" in report
    assert "architecture_status" in report
    assert "risk_scorecard" in report
    assert "watsonx_narrative" in report
    assert len(report["evidence_hash_tree"]) > 0
    assert report["signoff_status"] in ["APPROVED", "CONDITIONALLY_APPROVED", "PENDING_AUDIT"]
