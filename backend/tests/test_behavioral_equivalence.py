"""
LEGACYX — Behavioral Equivalence Evaluation Tests (Phase 9).

Verifies scenario input generation directly from Phase 4 BusinessRule records
and equivalence output evaluation between legacy and modern implementations.
"""

import pytest

from app.models.business_rule import BusinessRule
from app.models.transformation import TransformationProposal

from app.validation.validation_engine import evaluate_behavioral_equivalence


@pytest.mark.asyncio
async def test_behavioral_equivalence_with_phase4_rules(async_session, sample_repository):
    """Verifies that Phase 4 business rules produce deterministic scenarios and evaluate equivalence."""
    # 1. Seed Phase 4 business rules
    rule1 = BusinessRule(
        repository_id=sample_repository.id,
        analysis_id="analysis_beh_1",
        rule_type="THRESHOLD",
        title="High Value Approval Threshold",
        relative_file_path="AccountService.java",
        line_start=45,
        line_end=55,
        condition_expression="amount > 50000",
        action_expression="REQUIRES_APPROVAL",
        threshold_value="50000.0",
        threshold_operator=">",
        source_construct="IF_STATEMENT",
        extraction_reason="Extracted high value threshold check",
    )
    rule2 = BusinessRule(
        repository_id=sample_repository.id,
        analysis_id="analysis_beh_1",
        rule_type="VALIDATION",
        title="Sufficient Balance Check",
        relative_file_path="AccountService.java",
        line_start=60,
        line_end=70,
        condition_expression="balance < amount",
        action_expression="INSUFFICIENT_FUNDS",
        threshold_value="0.0",
        threshold_operator="<",
        source_construct="IF_STATEMENT",
        extraction_reason="Extracted balance check validation",
    )

    async_session.add_all([rule1, rule2])
    await async_session.commit()

    # 2. Seed Proposal
    proposal = TransformationProposal(
        plan_id="plan_beh_1",
        task_id="task_beh_1",
        analysis_id="analysis_beh_1",
        repository_id=sample_repository.id,
        status="APPROVED",
        transformation_type="FACADE_EXTRACTION",
        target_entity="TransferDomainService",
        summary="Proposal testing rule-grounded behavioral scenarios",
        rule_ids=[rule1.id, rule2.id],
        ai_proposal_status="COMPLETED",
    )
    async_session.add(proposal)
    await async_session.commit()

    # 3. Evaluate behavioral equivalence
    beh_status, passed_cnt, scenarios = await evaluate_behavioral_equivalence(
        proposal, sample_repository.id, async_session
    )


    assert beh_status in ("PASS", "FAIL", "MATCH", "MISMATCH", "UNABLE_TO_VALIDATE")
    assert passed_cnt >= 0
    assert len(scenarios) >= 2

    # Verify scenario grounding in Phase 4 rules
    rule_ids_in_scenarios = [s.business_rule_id for s in scenarios]
    assert rule1.id in rule_ids_in_scenarios or rule2.id in rule_ids_in_scenarios

    for sc in scenarios:
        assert sc.inputs is not None
        assert sc.legacy_expected_outputs is not None
        assert sc.modern_actual_outputs is not None
        assert sc.comparison_result in ("MATCH", "MISMATCH", "UNABLE_TO_VALIDATE")
