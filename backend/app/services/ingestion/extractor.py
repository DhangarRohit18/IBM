"""
LEGACYX — Secure ZIP Extractor (Phase 2).

Implements security checks for archive extraction:
- Zip Slip / path traversal protection
- Absolute path rejection
- File count limit enforcement
- Total extracted size limit enforcement
- Single file size limit enforcement
- Non-archive / corrupt archive handling
"""

import io
import os
from pathlib import Path
import zipfile

from app.core.config import get_settings


class IngestionSecurityException(Exception):
    """Base exception for ingestion security violations."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InvalidArchiveException(IngestionSecurityException):
    def __init__(self, message: str = "Uploaded file is not a valid ZIP archive") -> None:
        super().__init__("INVALID_ARCHIVE", message)


class ZipSecurityException(IngestionSecurityException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


class SecureZipExtractor:
    """Safely extracts ZIP archives into a target directory."""

    def __init__(self) -> None:
        settings = get_settings()
        self.max_file_count = settings.max_file_count
        self.max_extracted_bytes = settings.max_extracted_size_mb * 1024 * 1024
        self.max_single_file_bytes = settings.max_single_file_size_mb * 1024 * 1024

    def validate_and_extract(self, zip_bytes: bytes, target_dir: Path) -> dict:
        """Validate ZIP archive structure and securely extract files to target_dir.

        Returns dict with metrics: files_extracted, directories_extracted, total_bytes.
        """
        target_dir = target_dir.resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
        except zipfile.BadZipFile as exc:
            raise InvalidArchiveException("Uploaded file is not a valid ZIP archive") from exc

        namelist = zf.namelist()

        # ── Check file count ───────────────────────────────────────────────────
        if len(namelist) > self.max_file_count:
            raise ZipSecurityException(
                "TOO_MANY_FILES",
                f"Archive exceeds maximum file count limit of {self.max_file_count} files",
            )

        total_extracted_bytes = 0
        file_count = 0
        dir_count = 0

        # ── Pre-validate entries for path traversal / Zip Slip ──────────────────
        for member in zf.infolist():
            # Check uncompressed size
            if member.file_size > self.max_single_file_bytes:
                raise ZipSecurityException(
                    "FILE_TOO_LARGE",
                    f"Archive contains a file exceeding maximum size limit of {self.max_single_file_bytes // (1024*1024)}MB",
                )

            total_extracted_bytes += member.file_size
            if total_extracted_bytes > self.max_extracted_bytes:
                raise ZipSecurityException(
                    "ARCHIVE_TOO_LARGE",
                    f"Extracted archive size exceeds maximum limit of {self.max_extracted_bytes // (1024*1024)}MB",
                )

            # Security check for Path Traversal / Zip Slip / Absolute Paths
            raw_path = member.filename
            if raw_path.startswith("/") or raw_path.startswith("\\") or (len(raw_path) > 1 and raw_path[1] == ":"):
                raise ZipSecurityException(
                    "PATH_TRAVERSAL_DETECTED",
                    "Archive contains absolute paths which are not permitted",
                )

            # Resolve canonical path
            resolved_target = (target_dir / raw_path).resolve()
            if not str(resolved_target).startswith(str(target_dir)):
                raise ZipSecurityException(
                    "PATH_TRAVERSAL_DETECTED",
                    "Archive entry attempts path traversal outside target directory",
                )

        # ── Safe Extraction ─────────────────────────────────────────────────────
        for member in zf.infolist():
            resolved_target = (target_dir / member.filename).resolve()

            if member.is_dir():
                resolved_target.mkdir(parents=True, exist_ok=True)
                dir_count += 1
            else:
                resolved_target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(resolved_target, "wb") as target:
                    target.write(source.read())
                file_count += 1

        return {
            "files_extracted": file_count,
            "directories_extracted": dir_count,
            "total_bytes": total_extracted_bytes,
        }
