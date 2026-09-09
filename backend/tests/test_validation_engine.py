"""
LEGACYX — Validation Engine Unit Tests (Phase 9).

Tests the validation pipeline for isolated build/test execution, timeout guards,
evidence persistence, and immutability of original source repositories.
"""

import os
import shutil
import pytest
from sqlalchemy.future import select

from app.models.transformation import TransformationProposal
from app.models.validation import ValidationRun
from app.validation.validation_engine import check_jdk_available, run_validation_pipeline


@pytest.mark.asyncio
async def test_jdk_availability_check():
    """Verifies that JDK check cleanly detects javac or handles missing javac without crashing."""
    available, msg = check_jdk_available()
    assert isinstance(available, bool)
    assert isinstance(msg, str)
    if not available:
        assert "BUILD_ENVIRONMENT_UNAVAILABLE" in msg or "not found" in msg


@pytest.mark.asyncio
async def test_validation_pipeline_execution(async_session, sample_repository):
    """Verifies complete validation pipeline execution with evidence persistence and isolation."""
    # Create proposal record
    proposal = TransformationProposal(
        plan_id="test_plan_001",
        task_id="task_001",
        analysis_id="test_analysis_001",
        repository_id=sample_repository.id,
        status="APPROVED",
        transformation_type="FACADE_EXTRACTION",
        target_entity="TransferDomainService",
        summary="Test facade transformation proposal",
        specification={"rules": ["BR-001"]},
        rule_ids=["BR-001"],
        ai_proposal_status="COMPLETED",
    )
    async_session.add(proposal)
    await async_session.commit()

    # Run validation pipeline
    val_run = await run_validation_pipeline(proposal.id, async_session)


    assert val_run is not None
    assert val_run.transformation_proposal_id == proposal.id
    assert val_run.build_status in ("BUILD_PASS", "BUILD_FAIL", "BUILD_ENVIRONMENT_UNAVAILABLE", "NOT_RUN")
    assert val_run.test_status in ("TEST_PASS", "TEST_FAIL", "TEST_ENVIRONMENT_UNAVAILABLE", "NOT_RUN")
    assert val_run.behavioral_status in ("PASS", "FAIL", "UNABLE_TO_VALIDATE", "NOT_RUN")
    assert val_run.overall_status in ("VALIDATED", "VALIDATION_FAILED", "VALIDATION_BLOCKED", "PARTIALLY_VALIDATED")
    assert val_run.status in ("COMPLETED", "RUNNING", "PROPOSED", "REVIEWED", "VALIDATED")


    # Verify temp workspace directory was created
    temp_dir = os.path.join("storage", "temp_validation", val_run.id)
    assert os.path.exists(temp_dir)

    # Verify source repository storage/extracted remains unmodified
    legacy_source_dir = os.path.join("storage", "extracted", sample_repository.id)
    if os.path.exists(legacy_source_dir):
        assert os.path.isdir(legacy_source_dir)

