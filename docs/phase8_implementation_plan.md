# LEGACYX Phase 8 — Controlled Modernization & Code Transformation Implementation Plan

Phase 8 bridges **Approved Phase 7 Modernization Plans** to **Isolated Code Transformation Proposals**. It generates modernized target code artifacts (e.g., decomposing monolithic services into domain services, facades, and updated callers) while strictly adhering to original source immutability, deterministic rule preservation, and human-in-the-loop audit controls.

---

## 1. Architectural Principles & Requirements

1. **Approved Plan Input**: Phase 8 requires an **APPROVED** Phase 7 `ModernizationPlan` as input.
2. **Immutable Source Repository (AGENTS.md §4.1)**: Original legacy source files are never overwritten. All generated artifacts are written to `backend/storage/modernized/{project_id}/{plan_id}/`.
3. **Deterministic Evidence Grounding (AGENTS.md §2.1)**: Target code generation is grounded in Phase 3 AST entities, Phase 4 business rules, Phase 5 impact callers, and Phase 6 strategy selections.
4. **AI Gateway Isolation (AGENTS.md §3.1)**: AI is invoked strictly via `app/ai/gateway.py` to generate candidate transformation code proposals. AI cannot invent business rules, dependencies, or class signatures.
5. **4-State Machine (AGENTS.md §4.2)**: Proposals enforce `PROPOSED` → `REVIEWED` → `APPROVED` → `APPLIED` (or `REJECTED`).
6. **Zero Fake Metrics (AGENTS.md §5.2)**: No confidence percentages, no refactoring risk scores, no unverified behavioral claims.
7. **Explicit Phase Boundaries**: Code compilation, unit test execution, and behavioral equivalence testing belong strictly to Phase 9. Production deployment belongs to Phase 11.

---

## 2. Proposed System Components & File Scope

### [Backend Components]

#### [NEW] `backend/app/models/transformation.py`
ORM Models:
- `TransformationProposal`: Stores metadata for a transformation attempt linked to `plan_id`, `analysis_id`, `repository_id`, status (`PROPOSED`, `REVIEWED`, `APPROVED`, `APPLIED`, `REJECTED`), human review audit fields (`reviewed_by`, `reviewed_at`, `review_notes`), and AI explanation status.
- `TransformationArtifact`: Stores individual target code files (`artifact_type`, `target_file_path`, `source_file_path`, `source_line_start`, `source_line_end`, `generated_code`, `diff_content`, `rules_preserved_json`).

#### [NEW] `backend/alembic/versions/007_controlled_modernization.py`
Alembic schema migration for `transformation_proposals` and `transformation_artifacts` tables.

#### [NEW] `backend/app/modernization/transformation_engine.py`
Core transformation generator:
- Consumes approved `ModernizationPlan` and `ModernizationTask` items.
- Extracts mapped Phase 4 rules and Phase 5 caller impact items.
- Generates deterministic code templates for `EXTRACTED_CLASS`, `EXTRACTED_INTERFACE`, `FACADE`, `ADAPTER`, `REFACTORED_METHOD`, `MIGRATED_CALLER`, and `SUPPORTING_TEST_STUB`.
- Formats git-style unified diffs between legacy source snippet and modernized artifact.

#### [MODIFY] `backend/app/schemas/modernization.py`
Adds Pydantic schemas:
- `TransformationProposalResponse`
- `TransformationArtifactResponse`
- `TransformationReviewRequest`
- `TransformationApplyRequest`

#### [MODIFY] `backend/app/ai/base.py`, `backend/app/ai/gateway.py`, `backend/app/ai/providers/mock_provider.py`, `backend/app/ai/providers/watsonx_provider.py`
Adds `generate_code_proposal(context)` to AI abstraction layer to prompt AI provider for refined target implementation snippets.

#### [MODIFY] `backend/app/api/modernization.py`
Adds Phase 8 API endpoints:
- `POST /api/v1/modernization/plans/{plan_id}/transformations/propose`
- `GET  /api/v1/modernization/plans/{plan_id}/transformations`
- `GET  /api/v1/transformations/{id}`
- `GET  /api/v1/transformations/{id}/artifacts`
- `POST /api/v1/transformations/{id}/review`
- `POST /api/v1/transformations/{id}/apply`

### [Frontend Components]

#### [NEW] `frontend/src/features/modernization/TransformationStudioPage.tsx`
Interactive Transformation Studio UI:
- Modernization Plan & Task Selector
- Transformation Proposal Status Badge (`PROPOSED`, `REVIEWED`, `APPROVED`, `APPLIED`, `REJECTED`)
- Side-by-side Code & Diff Viewer (Legacy Source vs Modernized Artifact)
- Preserved Business Rules Verification Checklist
- Human Review Action Controls (Approve, Reject, Apply to Isolated Storage)
- AI Explanation & Code Refinement Card

#### [MODIFY] `frontend/src/features/projects/ProjectWorkspacePage.tsx`
Integrates **Code Transformation** tab into the project navigation header.

#### [MODIFY] `frontend/src/services/api.ts`
Adds Phase 8 API client methods for proposals, artifacts, human review, and artifact application.

---

## 3. Detailed Data Flow & Transformation Lifecycle

```text
Approved Modernization Plan (Phase 7)
       │
       ▼
Transformation Engine (`transformation_engine.py`)
       │
       ├── Reads AST Entity Signatures (Phase 3)
       ├── Reads Business Rules to Preserve (Phase 4)
       ├── Reads Affected Callers (Phase 5)
       └── Consumes Strategy Selection (Phase 6)
       │
       ▼
AI Gateway (`app/ai/gateway.py`) [Optional Code Refinement]
       │
       ▼
TransformationProposal & TransformationArtifact Created (Status: PROPOSED)
       │
       ▼
Human Architect Review in Frontend (`TransformationStudioPage.tsx`)
       │
       ├── Inspects Unified Code Diff
       ├── Verifies Preserved Business Rules Checklist
       └── Evaluates Target File Structure
       │
       ▼
Human Action:
  ├── REJECT → Status set to REJECTED (Audited with notes)
  └── APPROVE → Status set to APPROVED (Audited with notes)
       │
       ▼
Human Action: APPLY
       │
       ▼
Artifact Written to Isolated Storage (`storage/modernized/{project_id}/{plan_id}/`)
Status set to APPLIED (Ready for Phase 9 Validation)
```

---

## 4. Canonical LegacyBank Demonstration Flow

### Target Component: `AccountService.processTransfer()`

#### Input:
- Approved Phase 7 execution plan for `AccountService`.
- 4 Preserved Business Rules: `amount > 50000`, `balance < amount`, `fee = amount * 0.02`, `status == BLOCKED`.
- 1 Impacted Caller: `AccountController.java`.

#### Generated Artifacts:
1. `TransferDomainService.java` (`EXTRACTED_CLASS`):
   Contains isolated domain logic for validation, threshold checks, fee calculation, and state transition.
2. `AccountServiceFacade.java` (`FACADE`):
   Provides backward-compatible `processTransfer()` method delegating to `TransferDomainService`.
3. `AccountController.java` (`MIGRATED_CALLER`):
   Updated controller delegating to `AccountServiceFacade`.
4. `TransferDomainServiceTest.java` (`SUPPORTING_TEST_STUB`):
   Generated test skeleton with assertion stubs for preserved rules.

---

## 5. Security & Sandbox Considerations

1. **Source Code Immutability**: Customer repository files in `storage/extracted/` are strictly read-only.
2. **Isolated Output Workspace**: Artifacts are created only in `storage/modernized/{project_id}/{plan_id}/`.
3. **Path Sanitization**: All file paths derived from artifact proposals are sanitized (`Path(path).name` / traversal prevention).
4. **Project Authorization**: API endpoints validate that the requesting user owns the parent project.

---

## 6. Verification & Testing Plan

### Automated Backend Tests
- `tests/test_transformation_engine.py`: Tests deterministic template generation and diff calculation.
- `tests/test_api_transformation.py`: Tests Phase 8 API endpoints and state machine transitions (`PROPOSED` → `APPROVED` → `APPLIED`).

### Frontend Production Verification
- `npm run build`: Verifies TypeScript compilation and Vite build with 0 errors.

### End-to-End Browser DOM Demo
- Interactive browser DOM verification of Transformation Studio using the canonical `LegacyBank` fixture.

---

## 7. Explicit Non-Goals & Phase Boundaries

- **No Source File Mutation**: Phase 8 does NOT mutate legacy repository files.
- **No Code Compilation / Build Execution**: Deferred to Phase 9 (Validation Engine).
- **No Test Execution**: Deferred to Phase 9.
- **No Behavioral Equivalence Claims**: Deferred to Phase 9.
- **No Production Deployment**: Deferred to Phase 11.
