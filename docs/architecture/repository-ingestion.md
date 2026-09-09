# LEGACYX — Repository Ingestion Architecture

> **Phase 2 Architecture Specification**

---

## 1. Executive Overview

The Repository Ingestion layer provides a secure, deterministic pipeline for accepting legacy application source code archives (ZIP), calculating integrity checksums (SHA-256), performing safe archive extraction, indexing file hierarchies, and executing evidence-backed technology detection.

---

## 2. Ingestion Pipeline & Workflow

```
CREATE PROJECT
    ↓
REPOSITORY UPLOAD (ZIP)
    ↓
VALIDATE ARTIFACT (Size limits, ZIP format)
    ↓
SECURE EXTRACTION (Zip Slip & path traversal protection)
    ↓
INDEX FILES (Recursive file enumeration & SHA-256 capture)
    ↓
DETECT TECHNOLOGY (Deterministic evidence matching)
    ↓
CREATE REPOSITORY MANIFEST (JSON metadata output)
    ↓
INGESTION COMPLETE (Project READY for analysis)
```

---

## 3. Storage Abstraction Layer

All repository artifacts are managed through the `StorageProvider` abstract base class:

- `LocalStorageProvider` isolates raw uploaded archives under `storage/repositories/<project_id>/<sha256>.zip` from extracted working copies in `storage/extracted/<repository_id>/`.
- **Original Source Immutability**: Uploaded ZIP archives are saved once and treated as strictly immutable. All subsequent analysis reads from extracted working copies.

---

## 4. Extraction Security & Validation

The `SecureZipExtractor` enforces configurable security limits configured in `Settings`:

1. **Zip Slip Protection**: Verifies that canonical target paths remain strictly inside `storage/extracted/<repository_id>/`.
2. **Absolute Path Rejection**: Rejects entries with leading slashes, drive letters, or UNC paths.
3. **File Count Limits**: Enforces `MAX_FILE_COUNT` (default 10,000 files).
4. **Extracted Size Limits**: Enforces `MAX_EXTRACTED_SIZE_MB` (default 250MB).
5. **Single File Size Limits**: Enforces `MAX_SINGLE_FILE_SIZE_MB` (default 25MB).
6. **Clean Error Handling**: Emits structured error codes (`PATH_TRAVERSAL_DETECTED`, `FILE_TOO_LARGE`, `ARCHIVE_TOO_LARGE`, `TOO_MANY_FILES`, `INVALID_ARCHIVE`) without leaking internal filesystem paths.

---

## 5. Ingestion State Machine

The repository lifecycle is governed by an explicit state machine:

```
[UPLOADED] ──> [VALIDATING] ──> [EXTRACTING] ──> [INDEXING] ──> [COMPLETED]
     │              │               │               │
     └──────────────┴───────────────┴───────────────┴──> [FAILED]
```

State transitions are validated by `state_machine.py`. Illegal state transitions raise `IngestionStateException`.

---

## 6. Deterministic Technology Detection

Technology detection is 100% deterministic and evidence-backed (AGENTS.md §2.1). AI is **never** used for technology detection.

- **Java**: Discovers `.java` files (e.g. `127 .java files discovered`).
- **Maven**: Detects `pom.xml` build descriptor.
- **Gradle**: Detects `build.gradle` or `build.gradle.kts` build descriptors.
- **Spring**: Scans build descriptors and configuration files (`application.properties`, `application.yml`) for `spring-boot` and `springframework` dependencies.

Every detected technology report includes a verifiable `evidence` string array.

---

## 7. Database Entities

- `Repository`: `id`, `project_id`, `original_filename`, `artifact_size`, `sha256`, `storage_key`, `status`, timestamps.
- `RepositoryFile`: `id`, `repository_id`, `relative_path`, `filename`, `extension`, `size_bytes`, `is_directory`, `checksum`, `created_at`.
- `IngestionRun`: `id`, `repository_id`, `status`, `started_at`, `completed_at`, `files_discovered`, `directories_discovered`, `bytes_extracted`, `error_code`, `error_message`, `created_at`.

---

## 8. API Endpoints

- `POST /api/v1/projects` — Create project
- `GET /api/v1/projects` — List projects
- `POST /api/v1/projects/{project_id}/repositories` — Upload ZIP artifact & trigger ingestion
- `POST /api/v1/repositories/{repository_id}/ingest` — Re-trigger ingestion
- `GET /api/v1/repositories/{repository_id}` — Get repository overview
- `GET /api/v1/repositories/{repository_id}/files` — List repository files
- `GET /api/v1/repositories/{repository_id}/manifest` — Get JSON manifest
- `GET /api/v1/repositories/{repository_id}/ingestion` — Get ingestion audit runs
- `GET /api/v1/repositories/{repository_id}/files/content` — Read safe source file text
