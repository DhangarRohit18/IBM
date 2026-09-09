# LEGACYX Phase 9 — Build, Unit Test & Behavioral Equivalence Validation Implementation Plan

Phase 9 (**Build, Unit Test & Behavioral Equivalence Validation**) establishes an executable, empirical validation engine for modernized code artifacts generated in Phase 8.

---

## 1. Core Architectural Requirements

1. **Prerequisite Approval Gate**: Validation runs require an `APPROVED` or `APPLIED` Phase 8 `TransformationProposal`.
2. **Immutable Source Repository (AGENTS.md §4.1)**: Original legacy source files under `storage/extracted/` are strictly read-only. Validation operates inside isolated temporary workspaces (`storage/temp_validation/{run_id}/`).
3. **Deterministic Execution Evidence (AGENTS.md §2.2, §5.2)**: Validation statuses (`PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`, `MATCH`, `MISMATCH`) originate exclusively from subprocess execution and scenario evaluation. No fake confidence scores or percentage metrics.
4. **Honest Environment Reporting**: If JDK/`javac` tools are absent from PATH, system returns `ENVIRONMENT_UNAVAILABLE` cleanly without erroring or fabricating results.
5. **AI Boundary (AGENTS.md §3.1, §3.2)**: AI Gateway explains established validation evidence. AI cannot determine pass/fail status or modify validation records.
6. **Explicit Phase Boundaries**: Production deployment, automatic repository replacement, and CI/CD rollouts belong strictly to Phase 10+.

---

## 2. Proposed System Components & File Scope

### [Backend Components]

#### [NEW] `backend/app/models/validation.py`
ORM Models:
- `ValidationRun`: `id`, `transformation_proposal_id`, `project_id`, `plan_id`, `status` (`ValidationStatus`), `started_at`, `completed_at`, `environment_status`, `build_status`, `test_status`, `behavioral_status`, `overall_status`, `reviewed_by`, `reviewed_at`, `review_notes`, `ai_explanation`, `ai_explanation_status`.
- `ValidationEvidence`: `id`, `validation_run_id`, `stage` (`BUILD`, `UNIT_TEST`, `BEHAVIORAL_TEST`), `command`, `exit_code`, `stdout`, `stderr`, `duration_ms`, `status`, `evidence_json`.
- `BehavioralScenario`: `id`, `validation_run_id`, `business_rule_id`, `scenario_name`, `input_json`, `legacy_output_json`, `modernized_output_json`, `comparison_result` (`MATCH`, `MISMATCH`, `UNABLE_TO_VALIDATE`), `evidence_json`.

#### [NEW] `backend/alembic/versions/008_validation.py`
Alembic migration for `validation_runs`, `validation_evidence`, and `behavioral_scenarios` tables.

#### [NEW] `backend/app/validation/validation_engine.py`
Validation Engine:
- Detects JDK `javac` compiler on host PATH.
- Creates isolated workspace under `storage/temp_validation/{run_id}/`.
- Compiles modernized artifacts, executing javac subprocess.
- Executes unit tests, capturing test counts and log output.
- Evaluates behavioral scenarios derived from Phase 4 `BusinessRule` records.
- Compares legacy vs modernized outputs deterministically (`MATCH`, `MISMATCH`, `UNABLE_TO_VALIDATE`).

#### [MODIFY] `backend/app/schemas/modernization.py`
Adds Pydantic schemas:
- `ValidationRunResponse`
- `ValidationEvidenceResponse`
- `BehavioralScenarioResponse`
- `ValidationReviewRequest`
- `ValidationExplainResponse`

#### [MODIFY] `backend/app/ai/base.py`, `backend/app/ai/gateway.py`, `backend/app/ai/providers/mock_provider.py`, `backend/app/ai/providers/watsonx_provider.py`
Adds `explain_validation_evidence(context)` method to explain established validation facts.

#### [NEW] `backend/app/api/validation.py`
Validation REST API endpoints:
- `POST /api/v1/transformations/{transformation_id}/validation/run`
- `GET  /api/v1/transformations/{transformation_id}/validation`
- `GET  /api/v1/validation/{id}`
- `GET  /api/v1/validation/{id}/evidence`
- `GET  /api/v1/validation/{id}/scenarios`
- `POST /api/v1/validation/{id}/review`
- `POST /api/v1/validation/{id}/explain`

### [Frontend Components]

#### [NEW] `frontend/src/features/modernization/ValidationWorkspacePage.tsx`
Validation Workspace UI:
- Validation Header & Proposal Selector
- Build Validation Card (`PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`) with expandable stdout/stderr
- Unit Tests Execution Summary Card (total, passed, failed, skipped)
- Behavioral Equivalence Scenario Table (`✓ MATCH`, `✕ MISMATCH`, `— UNABLE TO VALIDATE`)
- Evidence Timeline & Log Viewer
- Human Review Action Controls
- AI Validation Explanation Card

#### [MODIFY] [ProjectWorkspacePage.tsx](file:///d:/LegacyX/frontend/src/features/projects/ProjectWorkspacePage.tsx)
Integrates **Validation** tab into the project workspace navigation header.

#### [MODIFY] [api.ts](file:///d:/LegacyX/frontend/src/services/api.ts)
Adds TypeScript interfaces and API client methods for Phase 9 validation.

---

## 3. Automated Test Suite

- `backend/tests/test_validation_engine.py`: Tests JDK detection, isolated compilation, unit test execution, and path traversal protection.
- `backend/tests/test_api_validation.py`: Tests validation run triggering, prerequisite approval check, evidence retrieval, review, and AI explanation.
- `backend/tests/test_behavioral_equivalence.py`: Tests deterministic scenario evaluators (`MATCH`, `MISMATCH`, `UNABLE_TO_VALIDATE`).

---

## 4. Verification Plan

1. Backend Test Suite: `python -m pytest tests/ -v` (100% pass)
2. Frontend Build: `npm run build` in `frontend/` (0 errors)
3. Database Migration: `alembic upgrade head`
4. Source Code Immutability Check: Verification that `storage/extracted/` remains byte-for-byte unchanged.
