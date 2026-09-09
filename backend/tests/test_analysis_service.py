"""Integration tests for AnalysisService pipeline on LegacyBank fixture."""

from pathlib import Path
import pytest
from app.analysis_engine.service import AnalysisService
from app.models.analysis_run import AnalysisRunStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


@pytest.mark.asyncio
async def test_analysis_service_full_pipeline(async_session, sample_project, sample_repository):
    service = AnalysisService()

    # Trigger analysis on extracted LegacyBank directory
    run = await service.run_analysis(
        session=async_session,
        repository_id=sample_repository.id,
        extracted_path=FIXTURES_DIR,
    )

    assert run.classes_count >= 7
    assert run.interfaces_count >= 2
    assert run.relationships_count > 0
    assert run.parser_name == "javalang"
    assert run.parser_version == "0.13.0"

    # Verify Summary statistics
    summary = await service.get_summary(async_session, run.id)
    assert summary is not None
    assert summary["total_classes"] >= 8
    assert "CONTROLLER" in summary["component_breakdown"]
    assert "SERVICE" in summary["component_breakdown"]
    assert "REPOSITORY" in summary["component_breakdown"]
    assert "MODEL" in summary["component_breakdown"]

    # Verify Graph data
    graph = await service.get_graph(async_session, run.id)
    assert graph is not None
    assert len(graph["nodes"]) >= 8
    assert len(graph["edges"]) > 0

    # Verify Search functionality
    search_res = await service.search_entities(async_session, run.id, "transfer")
    assert search_res is not None
    assert len(search_res["methods"]) > 0
