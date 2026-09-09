"""Security & Extraction unit tests for SecureZipExtractor (Phase 2)."""

import pytest
from pathlib import Path

from app.services.ingestion.extractor import (
    InvalidArchiveException,
    SecureZipExtractor,
    ZipSecurityException,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_extract_valid_legacy_java(tmp_path: Path):
    zip_bytes = (FIXTURES_DIR / "valid-legacy-java.zip").read_bytes()
    extractor = SecureZipExtractor()
    metrics = extractor.validate_and_extract(zip_bytes, tmp_path)

    assert metrics["files_extracted"] == 2
    assert (tmp_path / "src/com/bank/Account.java").exists()
    assert (tmp_path / "src/com/bank/Transaction.java").exists()


def test_reject_zip_slip_malicious_archive(tmp_path: Path):
    zip_bytes = (FIXTURES_DIR / "malicious-zip-slip.zip").read_bytes()
    extractor = SecureZipExtractor()

    with pytest.raises(ZipSecurityException) as exc_info:
        extractor.validate_and_extract(zip_bytes, tmp_path)

    assert exc_info.value.code == "PATH_TRAVERSAL_DETECTED"


def test_reject_invalid_corrupt_zip(tmp_path: Path):
    bad_bytes = b"NOT_A_ZIP_FILE_HEADER"
    extractor = SecureZipExtractor()

    with pytest.raises(InvalidArchiveException):
        extractor.validate_and_extract(bad_bytes, tmp_path)
