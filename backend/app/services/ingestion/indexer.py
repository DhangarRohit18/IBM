"""
LEGACYX — File Indexer (Phase 2).

Recursively enumerates extracted repository files, ignoring OS junk entries.
Captures relative paths, extensions, sizes, and file checksums.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path

# Common OS junk files/directories to ignore during indexing
IGNORE_NAMES = {
    ".ds_store",
    "thumbs.db",
    "desktop.ini",
    "__macosx",
    ".git",
    ".idea",
    ".vscode",
}


@dataclass
class IndexedFileItem:
    relative_path: str
    filename: str
    extension: str
    size_bytes: int
    is_directory: bool
    checksum: str | None


class FileIndexer:
    """Recursively indexes files in an extracted repository directory."""

    def index_directory(self, target_dir: Path) -> list[IndexedFileItem]:
        """Scan directory and return list of IndexedFileItem data objects."""
        target_dir = target_dir.resolve()
        items: list[IndexedFileItem] = []

        if not target_dir.exists() or not target_dir.is_dir():
            return items

        for path in target_dir.rglob("*"):
            rel_parts = path.relative_to(target_dir).parts
            # Check if any parent component is in IGNORE_NAMES
            if any(p.lower() in IGNORE_NAMES for p in rel_parts):
                continue

            rel_path_str = "/".join(rel_parts)
            is_dir = path.is_dir()
            filename = path.name
            extension = path.suffix.lstrip(".").lower() if (not is_dir and path.suffix) else ""
            size_bytes = path.stat().st_size if not is_dir else 0

            checksum = None
            if not is_dir:
                try:
                    checksum = self._calculate_file_hash(path)
                except Exception:
                    checksum = None

            items.append(
                IndexedFileItem(
                    relative_path=rel_path_str,
                    filename=filename,
                    extension=extension,
                    size_bytes=size_bytes,
                    is_directory=is_dir,
                    checksum=checksum,
                )
            )

        return items

    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of a single file."""
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
