"""
LEGACYX — Demo Acceptance Test (Clean State End-to-End User Journey).

Executes complete pipeline:
Ingestion → System X-Ray → Business Logic Recovery → Impact Analysis → Modernization Strategy → AI Explanation → Human Override.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models.base import Base

FIXTURES_DIR = Path(__file__).parent / "fixtures"
LEGACY_BANK_ZIP = FIXTURES_DIR / "valid-legacybank-app.zip"


@pytest.mark.asyncio
async def test_full_demo_user_journey_from_clean_state(async_client, async_session):
    """
    Executes complete demo user journey from a clean state.
    """
    # ── STEP 1: Create Project & Upload Repository ───────────────────────────
    res_proj = await async_client.post(
        "/api/v1/projects",
        json={"name": "LegacyBank Demo Project", "description": "Canonical banking demo"},
    )
    assert res_proj.status_code == 201
    proj_data = res_proj.json()
    project_id = proj_data["id"]

    assert LEGACY_BANK_ZIP.exists(), f"Fixture missing: {LEGACY_BANK_ZIP}"

    with open(LEGACY_BANK_ZIP, "rb") as f:
        res_repo = await async_client.post(
            f"/api/v1/projects/{project_id}/repositories",
            files={"file": ("legacybank.zip", f, "application/zip")},
        )
    assert res_repo.status_code == 201
    repo_data = res_repo.json()
    repository_id = repo_data["id"]
    assert repo_data["status"] in ["UPLOADED", "COMPLETED"]

    # ── STEP 2: Trigger System X-Ray Analysis ─────────────────────────────────
    res_analysis = await async_client.post(f"/api/v1/repositories/{repository_id}/analysis")
    assert res_analysis.status_code == 201
    analysis_data = res_analysis.json()
    analysis_id = analysis_data["id"]
    assert analysis_data["status"] == "COMPLETED"

    # Verify Packages
    res_pkgs = await async_client.get(f"/api/v1/analysis/{analysis_id}/packages")
    assert res_pkgs.status_code == 200
    pkgs = res_pkgs.json()
    pkg_names = [p["name"] for p in pkgs]
    assert any("com.legacybank.service" in name for name in pkg_names)

    # Verify Classes/Entities
    res_classes = await async_client.get(f"/api/v1/analysis/{analysis_id}/classes")
    assert res_classes.status_code == 200
    classes = res_classes.json()
    class_names = [c["name"] for c in classes]
    assert "AccountService" in class_names
    assert "AccountController" in class_names
    assert "AccountRepository" in class_names

    account_service = next(c for c in classes if c["name"] == "AccountService")
    assert account_service["component_type"] == "SERVICE"
    assert account_service["relative_file_path"] == "src/main/java/com/legacybank/service/AccountService.java"

    # Verify Relationships
    res_rels = await async_client.get(f"/api/v1/analysis/{analysis_id}/relationships")
    assert res_rels.status_code == 200
    rels = res_rels.json()
    assert len(rels) > 0

    # ── STEP 3: Business Logic Recovery ───────────────────────────────────────
    res_rules = await async_client.get(f"/api/v1/analysis/{analysis_id}/business-rules")
    assert res_rules.status_code == 200
    rules = res_rules.json()
    assert len(rules) >= 4, f"Expected >= 4 business rules, found {len(rules)}"

    # Check for canonical threshold rule
    threshold_rule = next(r for r in rules if r.get("threshold_value") == "50000")
    assert threshold_rule is not None
    assert threshold_rule["threshold_operator"] == ">"
    assert threshold_rule["rule_type"] == "THRESHOLD"
    assert threshold_rule["entity_id"] == account_service["id"]
    assert "src/main/java/com/legacybank/service/AccountService.java" in threshold_rule["relative_file_path"]

    # ── STEP 4: AI Explanation on Business Rule ───────────────────────────────
    res_explain = await async_client.post(f"/api/v1/business-rules/{threshold_rule['id']}/explain")
    assert res_explain.status_code == 200
    explained_rule = res_explain.json()
    assert explained_rule["status"] in ["COMPLETED", "EXPLAINED"]
    assert explained_rule["explanation"] is not None

    # Fetch updated rule details to verify threshold_value evidence remains intact
    res_rule_detail = await async_client.get(f"/api/v1/business-rules/{threshold_rule['id']}")
    assert res_rule_detail.status_code == 200
    rule_detail = res_rule_detail.json()
    assert rule_detail["threshold_value"] == "50000"

    # Review Rule
    res_review = await async_client.post(
        f"/api/v1/business-rules/{threshold_rule['id']}/review",
        json={"reviewed_by": "lead_auditor", "status": "REVIEWED", "review_notes": "Verified against Java source L39"},
    )
    assert res_review.status_code == 200
    reviewed_rule = res_review.json()
    assert reviewed_rule["status"] == "REVIEWED"
    assert reviewed_rule["reviewed_by"] == "lead_auditor"

    # ── STEP 5: Impact Analysis ───────────────────────────────────────────────
    res_impact = await async_client.get(
        f"/api/v1/analysis/{analysis_id}/impact",
        params={
            "target_type": "class",
            "target_id": account_service["id"],
            "direction": "forward",
            "max_depth": 3,
        },
    )
    assert res_impact.status_code == 200
    impact_data = res_impact.json()
    assert impact_data["has_evidenced_impact"] is True
    assert impact_data["status"] == "EVIDENCED_IMPACT_FOUND"
    assert impact_data["target"]["id"] == account_service["id"]
    assert len(impact_data["direct_affected_rules"]) > 0 or len(impact_data["transitive_affected_rules"]) > 0

    # ── STEP 6: Modernization Strategy Evaluation ─────────────────────────────
    res_eval = await async_client.post(f"/api/v1/analysis/{analysis_id}/modernization/evaluate")
    assert res_eval.status_code == 201
    strategies = res_eval.json()
    assert len(strategies) > 0

    account_service_strat = next(s for s in strategies if s["entity_id"] == account_service["id"])
    assert account_service_strat["recommended_strategy"] in ["MODULARIZE", "EXTRACT_SERVICE"]
    assert len(account_service_strat["observed_responsibilities"]) > 0
    assert len(account_service_strat["rules_to_preserve"]) > 0
    assert len(account_service_strat["decision_trace"]) > 0

    strategy_id = account_service_strat["id"]

    # ── STEP 7: AI Explanation on Modernization Strategy ──────────────────────
    res_strat_explain = await async_client.post(f"/api/v1/modernization/strategies/{strategy_id}/explain")
    assert res_strat_explain.status_code == 200
    explained_strat = res_strat_explain.json()
    assert explained_strat["status"] in ["COMPLETED", "EXPLAINED"]
    assert explained_strat["explanation"] is not None

    # ── STEP 8: Human Override on Modernization Strategy ─────────────────────
    res_override = await async_client.post(
        f"/api/v1/modernization/strategies/{strategy_id}/override",
        json={
            "status": "OVERRIDDEN",
            "user_override_strategy": "EXTRACT_SERVICE",
            "user_name": "lead_architect",
            "notes": "Extract AccountService into autonomous microservice",
        },
    )
    assert res_override.status_code == 200
    overridden_strat = res_override.json()
    assert overridden_strat["status"] == "OVERRIDDEN"
    assert overridden_strat["user_override_strategy"] == "EXTRACT_SERVICE"
    assert overridden_strat["user_override_by"] == "lead_architect"
    assert overridden_strat["user_override_notes"] == "Extract AccountService into autonomous microservice"
    # Ensure original recommendation is preserved in auditable record
    assert overridden_strat["recommended_strategy"] in ["MODULARIZE", "EXTRACT_SERVICE"]
