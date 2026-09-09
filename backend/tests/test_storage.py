"""Unit tests for StorageProvider and LocalStorageProvider (Phase 2)."""

import pytest
from pathlib import Path
from app.core.storage import LocalStorageProvider


def test_local_storage_save_and_read(tmp_path: Path):
    storage = LocalStorageProvider(root_dir=str(tmp_path))
    key = "test_project/artifact.zip"
    content = b"test zip payload content"

    path_str = storage.save_artifact(key, content)
    assert Path(path_str).exists()

    read_back = storage.read_artifact(key)
    assert read_back == content

    assert storage.artifact_exists(key) is True
    meta = storage.get_artifact_metadata(key)
    assert meta["size_bytes"] == len(content)

    deleted = storage.delete_artifact(key)
    assert deleted is True
    assert storage.artifact_exists(key) is False


def test_local_storage_path_traversal_prevention(tmp_path: Path):
    storage = LocalStorageProvider(root_dir=str(tmp_path))
    with pytest.raises(ValueError, match="path traversal"):
        storage.save_artifact("../evil.zip", b"content")
