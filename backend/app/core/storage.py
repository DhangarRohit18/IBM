"""
LEGACYX — Storage Abstraction Layer (Phase 2).

Provides an abstract interface for artifact storage (StorageProvider)
and a local filesystem implementation (LocalStorageProvider).

Decouples domain logic from filesystem operations (AGENTS.md & Phase 2 contract).
Ensures original uploaded artifacts remain strictly immutable.
"""

import abc
import os
import shutil
from pathlib import Path


class StorageProvider(abc.ABC):
    """Abstract storage interface for repository artifacts."""

    @abc.abstractmethod
    def save_artifact(self, key: str, data: bytes) -> str:
        """Save a raw artifact by key and return its absolute or relative reference."""
        pass

    @abc.abstractmethod
    def read_artifact(self, key: str) -> bytes:
        """Read and return raw artifact bytes for a given key."""
        pass

    @abc.abstractmethod
    def delete_artifact(self, key: str) -> bool:
        """Delete an artifact if it exists. Returns True if deleted."""
        pass

    @abc.abstractmethod
    def artifact_exists(self, key: str) -> bool:
        """Check whether an artifact exists at the specified key."""
        pass

    @abc.abstractmethod
    def get_artifact_metadata(self, key: str) -> dict:
        """Get metadata (e.g. size_bytes, path) for an artifact."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem implementation of StorageProvider."""

    def __init__(self, root_dir: str = "./storage") -> None:
        self.root_dir = Path(root_dir).resolve()
        self.repositories_dir = self.root_dir / "repositories"
        self.extracted_dir = self.root_dir / "extracted"

        # Ensure directory structure exists
        self.repositories_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        """Resolve a storage key to a path within repositories_dir, preventing traversal."""
        path = (self.repositories_dir / key).resolve()
        if not str(path).startswith(str(self.repositories_dir.resolve())):
            raise ValueError(f"Storage path traversal attempt detected for key: {key}")
        return path

    def get_extracted_path(self, repository_id: str) -> Path:
        """Get target directory for extracted repository files."""
        path = (self.extracted_dir / repository_id).resolve()
        if not str(path).startswith(str(self.extracted_dir.resolve())):
            raise ValueError(f"Extracted path traversal attempt for ID: {repository_id}")
        return path

    def save_artifact(self, key: str, data: bytes) -> str:
        """Save raw artifact bytes to storage/repositories/<key>."""
        target_path = self._get_path(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(data)
        return str(target_path)

    def read_artifact(self, key: str) -> bytes:
        """Read raw artifact bytes."""
        target_path = self._get_path(key)
        if not target_path.exists():
            raise FileNotFoundError(f"Artifact not found for key: {key}")
        with open(target_path, "rb") as f:
            return f.read()

    def delete_artifact(self, key: str) -> bool:
        """Delete an artifact file and any associated extracted tree."""
        target_path = self._get_path(key)
        deleted = False
        if target_path.exists():
            target_path.unlink()
            deleted = True

        # Extract stem assuming key format <id>.zip or similar
        repo_id = Path(key).stem
        extracted_path = self.extracted_dir / repo_id
        if extracted_path.exists() and extracted_path.is_dir():
            shutil.rmtree(extracted_path, ignore_errors=True)
            deleted = True

        return deleted

    def artifact_exists(self, key: str) -> bool:
        """Check if artifact file exists."""
        return self._get_path(key).exists()

    def get_artifact_metadata(self, key: str) -> dict:
        """Return size and path for stored artifact."""
        path = self._get_path(key)
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {key}")
        stat = path.stat()
        return {
            "key": key,
            "path": str(path),
            "size_bytes": stat.st_size,
            "modified_at": stat.st_mtime,
        }
