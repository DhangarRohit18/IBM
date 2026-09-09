"""
LEGACYX — Repository Manifest Generator (Phase 2).

Constructs the structured JSON manifest for an ingested repository.
Includes repository metadata, file/directory counts, extension breakdown,
detected technologies with evidence arrays, and key project files.
"""

from typing import Any
from app.services.ingestion.detector import TechnologyEvidence
from app.services.ingestion.indexer import IndexedFileItem

KEY_PROJECT_FILENAMES = {
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "readme.md",
    "readme.txt",
    "application.properties",
    "application.yml",
    "application.yaml",
    "dockerfile",
    "docker-compose.yml",
}


class ManifestGenerator:
    """Generates a comprehensive JSON manifest for an ingested repository."""

    def generate_manifest(
        self,
        repository_id: str,
        original_filename: str,
        artifact_size: int,
        sha256: str,
        indexed_items: list[IndexedFileItem],
        technologies: list[TechnologyEvidence],
    ) -> dict[str, Any]:
        """Produce the repository manifest dict structure."""
        file_items = [item for item in indexed_items if not item.is_directory]
        dir_items = [item for item in indexed_items if item.is_directory]

        # Extension breakdown
        extension_counts: dict[str, int] = {}
        for file in file_items:
            ext = file.extension.lower() if file.extension else "(no extension)"
            extension_counts[ext] = extension_counts.get(ext, 0) + 1

        # Key project files
        key_files: list[str] = [
            item.relative_path
            for item in file_items
            if item.filename.lower() in KEY_PROJECT_FILENAMES
        ]

        # Technology objects
        tech_list = [
            {"name": tech.name, "evidence": tech.evidence}
            for tech in technologies
        ]

        return {
            "repository": {
                "id": repository_id,
                "original_filename": original_filename,
                "artifact_size": artifact_size,
                "sha256": sha256,
            },
            "summary": {
                "total_files": len(file_items),
                "total_directories": len(dir_items),
                "total_bytes": sum(item.size_bytes for item in file_items),
            },
            "extension_breakdown": extension_counts,
            "technologies": tech_list,
            "key_files": key_files,
        }
