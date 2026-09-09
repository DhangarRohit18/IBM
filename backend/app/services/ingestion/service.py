"""
LEGACYX — Ingestion Service (Phase 2).

Orchestrates the repository ingestion pipeline:
1. Storage & SHA-256 calculation
2. Secure ZIP validation & extraction
3. File indexing & metadata capture
4. Deterministic technology detection
5. Repository manifest generation
6. Explicit state machine transitions
7. Database persistence (Repository, RepositoryFile, IngestionRun)
8. Structured audit logging
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logging import get_logger
from app.core.storage import LocalStorageProvider
from app.models.ingestion_run import IngestionRun, IngestionStatus
from app.models.project import Project, ProjectStatus
from app.models.repository import Repository, RepositoryStatus
from app.models.repository_file import RepositoryFile
from app.services.ingestion.detector import TechnologyDetector
from app.services.ingestion.extractor import (
    IngestionSecurityException,
    SecureZipExtractor,
)
from app.services.ingestion.indexer import FileIndexer
from app.services.ingestion.manifest import ManifestGenerator
from app.services.ingestion.state_machine import validate_transition

logger = get_logger(__name__)


class IngestionService:
    """Service orchestrator for repository ingestion pipeline."""

    def __init__(self, storage_provider: LocalStorageProvider | None = None) -> None:
        self.storage = storage_provider or LocalStorageProvider()
        self.extractor = SecureZipExtractor()
        self.indexer = FileIndexer()
        self.detector = TechnologyDetector()
        self.manifest_gen = ManifestGenerator()

    async def create_repository_record(
        self,
        session: AsyncSession,
        project: Project,
        filename: str,
        file_bytes: bytes,
    ) -> tuple[Repository, IngestionRun]:
        """Save raw artifact bytes immutably and initialize Repository and IngestionRun DB records."""
        # Calculate SHA-256 checksum
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        artifact_size = len(file_bytes)

        # Generate unique storage key: <project_id>/<sha256>.zip
        storage_key = f"{project.id}/{sha256}.zip"
        self.storage.save_artifact(storage_key, file_bytes)

        # Check if repository already exists for this project
        stmt = select(Repository).where(Repository.project_id == project.id)
        result = await session.execute(stmt)
        repository = result.scalar_one_or_none()

        if repository:
            repository.original_filename = filename
            repository.artifact_size = artifact_size
            repository.sha256 = sha256
            repository.storage_key = storage_key
            repository.status = RepositoryStatus.UPLOADED
        else:
            repository = Repository(
                project_id=project.id,
                original_filename=filename,
                artifact_size=artifact_size,
                sha256=sha256,
                storage_key=storage_key,
                status=RepositoryStatus.UPLOADED,
            )
            session.add(repository)

        await session.flush()

        # Update Project status to INGESTING
        project.status = ProjectStatus.INGESTING

        # Create IngestionRun audit record
        ingestion_run = IngestionRun(
            repository_id=repository.id,
            status=IngestionStatus.STARTED,
            started_at=datetime.now(timezone.utc),
        )
        session.add(ingestion_run)
        await session.commit()
        await session.refresh(repository)
        await session.refresh(ingestion_run)

        logger.info(
            "repository.uploaded",
            repository_id=repository.id,
            project_id=project.id,
            filename=filename,
            sha256=sha256,
            size_bytes=artifact_size,
        )

        return repository, ingestion_run

    async def run_ingestion_pipeline(
        self,
        session: AsyncSession,
        repository_id: str,
        ingestion_run_id: str,
    ) -> tuple[Repository, dict[str, Any]]:
        """Run the complete synchronous ingestion pipeline for a repository artifact."""
        stmt = select(Repository).where(Repository.id == repository_id)
        result = await session.execute(stmt)
        repository = result.scalar_one_or_none()
        if not repository:
            raise ValueError(f"Repository not found: {repository_id}")

        stmt_run = select(IngestionRun).where(IngestionRun.id == ingestion_run_id)
        result_run = await session.execute(stmt_run)
        ingestion_run = result_run.scalar_one_or_none()
        if not ingestion_run:
            raise ValueError(f"Ingestion run not found: {ingestion_run_id}")

        # Fetch parent project
        stmt_proj = select(Project).where(Project.id == repository.project_id)
        result_proj = await session.execute(stmt_proj)
        project = result_proj.scalar_one_or_none()

        try:
            # ── 1. State: VALIDATING ─────────────────────────────────────────────
            self._update_status(repository, RepositoryStatus.VALIDATING)
            await session.commit()
            logger.info("repository.validation_started", repository_id=repository_id)

            # Read raw immutable artifact
            raw_bytes = self.storage.read_artifact(repository.storage_key)

            # ── 2. State: EXTRACTING ─────────────────────────────────────────────
            self._update_status(repository, RepositoryStatus.EXTRACTING)
            await session.commit()
            logger.info("repository.extraction_started", repository_id=repository_id)

            extracted_dir = self.storage.get_extracted_path(repository.id)
            extraction_metrics = self.extractor.validate_and_extract(raw_bytes, extracted_dir)

            repository.extracted_path = str(extracted_dir)
            ingestion_run.bytes_extracted = extraction_metrics["total_bytes"]

            logger.info(
                "repository.extraction_completed",
                repository_id=repository_id,
                extracted_dir=str(extracted_dir),
                bytes_extracted=extraction_metrics["total_bytes"],
            )

            # ── 3. State: INDEXING ───────────────────────────────────────────────
            self._update_status(repository, RepositoryStatus.INDEXING)
            await session.commit()
            logger.info("repository.indexing_started", repository_id=repository_id)

            indexed_items = self.indexer.index_directory(extracted_dir)

            # Clear any existing file entries for this repo
            del_stmt = select(RepositoryFile).where(RepositoryFile.repository_id == repository_id)
            del_res = await session.execute(del_stmt)
            for old_file in del_res.scalars().all():
                await session.delete(old_file)

            # Insert new RepositoryFile records
            file_count = 0
            dir_count = 0
            for item in indexed_items:
                if item.is_directory:
                    dir_count += 1
                else:
                    file_count += 1

                repo_file = RepositoryFile(
                    repository_id=repository.id,
                    relative_path=item.relative_path,
                    filename=item.filename,
                    extension=item.extension,
                    size_bytes=item.size_bytes,
                    is_directory=item.is_directory,
                    checksum=item.checksum,
                )
                session.add(repo_file)

            ingestion_run.files_discovered = file_count
            ingestion_run.directories_discovered = dir_count

            logger.info(
                "repository.indexing_completed",
                repository_id=repository_id,
                files=file_count,
                directories=dir_count,
            )

            # ── 4. Technology Detection & Manifest ───────────────────────────────
            technologies = self.detector.detect_technologies(extracted_dir, indexed_items)
            manifest = self.manifest_gen.generate_manifest(
                repository_id=repository.id,
                original_filename=repository.original_filename,
                artifact_size=repository.artifact_size,
                sha256=repository.sha256,
                indexed_items=indexed_items,
                technologies=technologies,
            )

            # ── 5. State: COMPLETED ──────────────────────────────────────────────
            self._update_status(repository, RepositoryStatus.COMPLETED)
            ingestion_run.status = IngestionStatus.COMPLETED
            ingestion_run.completed_at = datetime.now(timezone.utc)

            if project:
                project.status = ProjectStatus.READY

            await session.commit()
            await session.refresh(repository)
            await session.refresh(ingestion_run)

            logger.info(
                "repository.ingestion_completed",
                repository_id=repository_id,
                status="COMPLETED",
                technologies=[t.name for t in technologies],
            )

            return repository, manifest

        except IngestionSecurityException as exc:
            await session.rollback()
            self._mark_failed(repository, ingestion_run, project, exc.code, exc.message)
            await session.commit()
            logger.error(
                "repository.ingestion_failed",
                repository_id=repository_id,
                error_code=exc.code,
                error_message=exc.message,
            )
            raise exc

        except Exception as exc:
            await session.rollback()
            self._mark_failed(
                repository,
                ingestion_run,
                project,
                "EXTRACTION_FAILED",
                f"Ingestion processing failed: {str(exc)}",
            )
            await session.commit()
            logger.error(
                "repository.ingestion_failed",
                repository_id=repository_id,
                error=str(exc),
            )
            raise exc

    def _update_status(self, repository: Repository, target_status: RepositoryStatus) -> None:
        """Validate and set target status on repository record."""
        validate_transition(repository.status, target_status)
        repository.status = target_status

    def _mark_failed(
        self,
        repository: Repository,
        ingestion_run: IngestionRun,
        project: Project | None,
        error_code: str,
        error_message: str,
    ) -> None:
        """Mark repository, ingestion run, and project as failed."""
        repository.status = RepositoryStatus.FAILED
        ingestion_run.status = IngestionStatus.FAILED
        ingestion_run.completed_at = datetime.now(timezone.utc)
        ingestion_run.error_code = error_code
        ingestion_run.error_message = error_message
        if project:
            project.status = ProjectStatus.FAILED
