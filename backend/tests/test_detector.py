"""Unit tests for TechnologyDetector (Phase 2)."""

from pathlib import Path
from app.services.ingestion.detector import TechnologyDetector
from app.services.ingestion.extractor import SecureZipExtractor
from app.services.ingestion.indexer import FileIndexer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_detect_spring_maven_project(tmp_path: Path):
    zip_bytes = (FIXTURES_DIR / "valid-spring-maven.zip").read_bytes()
    extractor = SecureZipExtractor()
    extractor.validate_and_extract(zip_bytes, tmp_path)

    indexer = FileIndexer()
    items = indexer.index_directory(tmp_path)

    detector = TechnologyDetector()
    technologies = detector.detect_technologies(tmp_path, items)

    tech_names = [t.name for t in technologies]
    assert "Java" in tech_names
    assert "Maven" in tech_names
    assert "Spring" in tech_names

    spring_tech = next(t for t in technologies if t.name == "Spring")
    assert len(spring_tech.evidence) > 0


def test_detect_gradle_project(tmp_path: Path):
    zip_bytes = (FIXTURES_DIR / "valid-gradle.zip").read_bytes()
    extractor = SecureZipExtractor()
    extractor.validate_and_extract(zip_bytes, tmp_path)

    indexer = FileIndexer()
    items = indexer.index_directory(tmp_path)

    detector = TechnologyDetector()
    technologies = detector.detect_technologies(tmp_path, items)

    tech_names = [t.name for t in technologies]
    assert "Java" in tech_names
    assert "Gradle" in tech_names
    assert "Spring" in tech_names
