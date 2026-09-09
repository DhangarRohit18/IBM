"""
Tests for Phase 5 Deterministic Impact Analyzer engine.
"""

from pathlib import Path
import pytest

from app.analysis_engine.impact_analyzer import ImpactDirection, ImpactTargetType, impact_analyzer
from app.models.code_entity import CodeEntity, EntityType, ComponentType
from app.models.code_relationship import CodeRelationship, RelationshipType
from app.models.business_rule import BusinessRule, RuleType, RuleStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_impact_analyzer_forward_and_reverse(async_client, async_session, sample_project, sample_repository):
    # Set extracted_path on repository for testing
    sample_repository.extracted_path = str(FIXTURES_DIR)
    async_session.add(sample_repository)
    await async_session.commit()

    # 1. Trigger System X-Ray Analysis
    res_analysis = await async_client.post(f"/api/v1/repositories/{sample_repository.id}/analysis")
    assert res_analysis.status_code == 201
    run_data = res_analysis.json()
    analysis_id = run_data["id"]

    # Fetch entities to select a target
    res_entities = await async_client.get(f"/api/v1/analysis/{analysis_id}/classes")
    entities = res_entities.json()
    assert len(entities) > 0


    transfer_service = next((e for e in entities if "TransferService" in e["name"]), entities[0])

    # 2. Forward Impact Analysis (What does TransferService depend on?)
    res_fwd = await impact_analyzer.analyze(
        session=async_session,
        analysis_id=analysis_id,
        target_type=ImpactTargetType.CLASS,
        target_id=transfer_service["id"],
        direction=ImpactDirection.FORWARD,
        max_depth=3,
    )

    assert res_fwd["analysis_id"] == analysis_id
    assert res_fwd["target"]["id"] == transfer_service["id"]
    assert res_fwd["direction"] == "forward"
    assert "summary" in res_fwd
    assert res_fwd["has_evidenced_impact"] is True
    assert res_fwd["status"] == "EVIDENCED_IMPACT_FOUND"

    # 3. Reverse Impact Analysis (What depends on TransferService / AccountRepository?)
    account_repo = next((e for e in entities if "AccountRepository" in e["name"]), entities[-1])
    res_rev = await impact_analyzer.analyze(
        session=async_session,
        analysis_id=analysis_id,
        target_type=ImpactTargetType.CLASS,
        target_id=account_repo["id"],
        direction=ImpactDirection.REVERSE,
        max_depth=3,
    )

    assert res_rev["direction"] == "reverse"
    assert res_rev["target"]["id"] == account_repo["id"]
    assert res_rev["has_evidenced_impact"] is True


@pytest.mark.asyncio
async def test_impact_analyzer_no_evidenced_impact(async_session, sample_project, sample_repository):
    # Create isolated orphan entity with zero relationships or rules
    isolated = CodeEntity(
        analysis_id="dummy_analysis",
        repository_id=sample_repository.id,
        name="IsolatedComponent",
        fully_qualified_name="com.legacybank.IsolatedComponent",
        entity_type=EntityType.CLASS,
        component_type=ComponentType.UTILITY,
        relative_file_path="src/main/java/com/legacybank/IsolatedComponent.java",
        line_start=1,
        line_end=10,
    )

    async_session.add(isolated)
    await async_session.commit()

    res = await impact_analyzer.analyze(
        session=async_session,
        analysis_id="dummy_analysis",
        target_type=ImpactTargetType.CLASS,
        target_id=isolated.id,
        direction=ImpactDirection.FORWARD,
        max_depth=3,
    )

    # Must return explicit NO EVIDENCED IMPACT result
    assert res["has_evidenced_impact"] is False
    assert res["status"] == "NO_EVIDENCED_IMPACT"
    assert res["summary"]["direct_component_count"] == 0
    assert res["summary"]["transitive_component_count"] == 0
    assert res["summary"]["direct_rule_count"] == 0
    assert res["summary"]["transitive_rule_count"] == 0
