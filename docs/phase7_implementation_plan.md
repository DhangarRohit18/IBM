# Phase 7 — Modernization Execution Plan Implementation Plan

## Executive Summary

Phase 7 bridges **Phase 6 Modernization Strategy Recommendations** to an **Actionable, Traceable Modernization Execution Plan**.

Given a legacy component (e.g. `AccountService.processTransfer()`) with:
- Observed AST responsibilities (validation, threshold enforcement, fee calculation, state mutation, persistence, notification)
- Extracted business rules (`amount > 50000`, `balance < amount`, `fee = amount * 0.02`, state transitions)
- Direct & transitive impact surface (`AccountController`, `AccountRepository`, `FraudService`)
- Selected modernization strategy (`MODULARIZE` / `STRANGLER`)

Phase 7 deterministically decomposes the modernization effort into an **ordered sequence of execution tasks**, maps explicit **business rules to preserve**, attaches **impact-aware caller migration steps**, defines **verification checkpoints**, and records **auditable human review & task status updates**.

---

## 1. Architectural Principles & Strict Design Boundaries

1. **Deterministic Execution Plan Generation**:
   All tasks, dependencies, preservation constraints, and verification checkpoints are computed deterministically from static analysis facts, AST responsibility signals, extracted business rules, and impact graphs. LLMs are NEVER used to invent tasks or refactoring steps.

2. **Zero Fake Scores**:
   No confidence percentages, risk scores, modernization progress percentages, or arbitrary effort estimates. All metrics rely on observable facts: task count, preserved business rules count, direct/transitive dependent count, and verification checkpoint count.

3. **Strict Business Logic Preservation**:
   Every generated plan compiles a `rules_to_preserve` catalog linking each rule ID, condition/formula expression, file path, line range, and assigned execution task ID(s).

4. **Dependency-Aware Acyclic Task Ordering (DAG)**:
   Tasks form a topologically sorted sequence where responsibility isolation and business rule separation precede interface creation, caller migration, and verification checkpoints.

5. **Auditable Human Control State Machine**:
   - Plan Status: `PROPOSED` → `REVIEWED` → `APPROVED` → `REJECTED`
   - Task Status: `PENDING` → `IN_PROGRESS` → `COMPLETED` → `DEFERRED` / `SKIPPED`
   Architects can reorder, modify, or update task statuses without automatic source code mutation.

6. **Strict AI Boundary**:
   AI Gateway generates plain-language explanations ONLY for established plan facts. AI NEVER creates tasks, alters task ordering, invents rules, or generates transformation code.

---

## 2. Controlled Task Taxonomy & Dependency Rules

### Task Taxonomy (`TaskType`)

| Task Type | Category | Description | Dependency Rule |
|---|---|---|---|
| `EXTRACT_RESPONSIBILITY` | Responsibility | Isolate AST responsibility signals into dedicated domain components | Base level (no task deps) |
| `SEPARATE_BUSINESS_RULE` | Rule | Decouple extracted Phase 4 business rules (validation, threshold, calculation) | Base level (no task deps) |
| `EXTRACT_CALCULATION` | Calculation | Isolate financial derivations and mathematical formulas | Base level (no task deps) |
| `ISOLATE_PERSISTENCE` | Persistence | Isolate database mutations and entity manager operations | Base level (no task deps) |
| `ISOLATE_STATE_TRANSITION` | State | Isolate domain lifecycle transitions (e.g. `PENDING` -> `COMPLETED`) | Base level (no task deps) |
| `ISOLATE_EXTERNAL_NOTIFICATION` | Notification | Isolate asynchronous event publishing or notification dispatch | Base level (no task deps) |
| `DEFINE_INTERFACE` | Interface | Define clean contract interfaces for extracted modules | Depends on isolation tasks |
| `INTRODUCE_ADAPTER` | Pattern | Provide protocol or interface mapping between legacy and modern | Depends on interface tasks |
| `INTRODUCE_FACADE` | Pattern | Wrap legacy component to preserve caller compatibility | Depends on interface tasks |
| `REDUCE_DEPENDENCY` | Coupling | Decouple unnecessary direct dependencies | Depends on isolation tasks |
| `SPLIT_COMPONENT` | Refactoring | Decompose class into modular domain helpers | Depends on interface/facade tasks |
| `MIGRATE_CALLER` | Impact | Update direct dependents identified in Phase 5 impact analysis | Depends on facade/interface tasks |
| `PRESERVE_BEHAVIOR` | Rule | Enforce explicit invariant preservation for rules | Depends on caller migration tasks |
| `ADD_VERIFICATION_CHECKPOINT` | Verification | Attach verifiable assertion criteria to major refactoring milestones | Final verification step |

---

## 3. Database Architecture & Schema Specification

### ORM Models (`backend/app/models/modernization_plan.py`)

#### `ModernizationPlan` Table: `modernization_plans`
- `id`: String(36), PK
- `analysis_id`: String(36), FK → `analysis_runs.id` (CASCADE)
- `repository_id`: String(36), FK → `repositories.id` (CASCADE)
- `entity_id`: String(36), FK → `code_entities.id` (CASCADE)
- `strategy_id`: String(36), FK → `modernization_strategies.id` (CASCADE, nullable)
- `entity_name`: String(255), Not Null
- `strategy_type`: String(64), Not Null (e.g., `MODULARIZE`, `STRANGLER`)
- `status`: String(32), Default `PROPOSED` (`PROPOSED`, `REVIEWED`, `APPROVED`, `REJECTED`)
- `summary`: Text, Not Null
- `rules_to_preserve`: JSON (List of preserved rule records with conditions & line ranges)
- `impact_summary`: JSON (Direct and transitive dependent summaries)
- `verification_checkpoints`: JSON (List of verification criteria)
- `reviewed_by`: String(128), Nullable
- `reviewed_at`: DateTime(timezone=True), Nullable
- `review_notes`: Text, Nullable
- `ai_explanation`: Text, Nullable
- `ai_explanation_status`: String(32), Default `NOT_REQUESTED`
- `created_at`, `updated_at`: DateTime(timezone=True)

#### `ModernizationTask` Table: `modernization_tasks`
- `id`: String(36), PK
- `plan_id`: String(36), FK → `modernization_plans.id` (CASCADE)
- `sequence_order`: Integer, Not Null (1-indexed topological order)
- `title`: String(255), Not Null
- `description`: Text, Not Null
- `task_type`: String(64), Not Null (`TaskType` enum)
- `status`: String(32), Default `PENDING` (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `DEFERRED`, `SKIPPED`)
- `target_component`: String(255), Not Null
- `target_file_path`: String(512), Not Null
- `depends_on_task_ids`: JSON (List of prerequisite task UUIDs)
- `rule_ids`: JSON (List of associated Phase 4 BusinessRule UUIDs)
- `evidence_references`: JSON (Line ranges, file snippets, AST responsibility category)
- `created_at`, `updated_at`: DateTime(timezone=True)

### Alembic Migration
- `backend/alembic/versions/006_modernization_execution_plan.py`
- Implements portable DDL supporting both PostgreSQL and SQLite.

---

## 4. Modernization Plan Generator Engine Design

### Engine Module (`backend/app/modernization/plan_generator.py`)

#### Primary Methods:
1. `generate_plan(entity, strategy, responsibilities, business_rules, impact_data)`:
   - Evaluates input facts and produces a structured `ModernizationPlan` payload with topologically ordered `ModernizationTask` items.
2. `_build_tasks(...)`:
   - Decomposes responsibilities into isolation tasks (`EXTRACT_RESPONSIBILITY`, `SEPARATE_BUSINESS_RULE`, `EXTRACT_CALCULATION`, `ISOLATE_PERSISTENCE`, `ISOLATE_STATE_TRANSITION`, `ISOLATE_EXTERNAL_NOTIFICATION`).
   - Generates interface definition tasks (`DEFINE_INTERFACE`, `INTRODUCE_FACADE`).
   - Generates caller migration tasks (`MIGRATE_CALLER`) based on Phase 5 direct dependents.
   - Generates behavior preservation and verification checkpoint tasks (`PRESERVE_BEHAVIOR`, `ADD_VERIFICATION_CHECKPOINT`).
3. `_topological_sort_tasks(tasks)`:
   - Assigns sequential `sequence_order` enforcing acyclic dependency execution.

---

## 5. REST API Specifications

### Endpoints (`backend/app/api/modernization.py`)

| Method | Endpoint Path | Description |
|---|---|---|
| `POST` | `/api/v1/analysis/{analysis_id}/modernization/plans/generate` | Triggers deterministic plan generation for all candidate strategies or specific target entity |
| `GET` | `/api/v1/analysis/{analysis_id}/modernization/plans` | Lists generated modernization plans |
| `GET` | `/api/v1/modernization/plans/{plan_id}` | Gets detailed modernization plan payload including ordered tasks and dependencies |
| `GET` | `/api/v1/modernization/plans/{plan_id}/tasks` | Gets ordered modernization tasks |
| `POST` | `/api/v1/modernization/plans/{plan_id}/review` | Records audited human plan approval, review, or rejection |
| `POST` | `/api/v1/modernization/tasks/{task_id}/status` | Updates individual task execution status (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `DEFERRED`) |
| `POST` | `/api/v1/modernization/tasks/{task_id}/reorder` | Updates task execution sequence order |
| `POST` | `/api/v1/modernization/plans/{plan_id}/explain` | Requests AI Gateway narrative explanation for established plan |

---

## 6. Frontend Modernization Plan Workspace Design

### Location: `frontend/src/features/modernization/ModernizationPlanPage.tsx`

### UI Visual Hierarchy:
1. **Header Overview Card**:
   - Modernization Candidate (`AccountService.processTransfer()`)
   - Recommended Strategy (`MODULARIZE` / `STRANGLER`)
   - Plan Status (`PROPOSED`, `REVIEWED`, `APPROVED`) & Action buttons (**Approve Plan**, **AI Explain**)
2. **Execution Task List & Dependency Graph**:
   - Interactive list of ordered tasks with sequence numbers, task type badges, target file links, status toggle buttons, and prerequisite task badges.
3. **Business Rules to Preserve Table**:
   - Summary of Phase 4 rules mapped to execution tasks with condition expressions, line ranges, and source links.
4. **Impact Surface & Caller Verification Panel**:
   - Direct dependents (`AccountController`) requiring contract verification.
5. **Verification Checkpoints List**:
   - Verifiable criteria checklist (rule representation, state invariant, caller interface equivalence).

---

## 7. Canonical LegacyBank Demo Target Walkthrough

Target: `AccountService.processTransfer()`

1. **Observed Responsibilities**:
   - `INPUT_VALIDATION`: Precondition null checks
   - `BUSINESS_RULE_ENFORCEMENT`: `amount > 50000` approval check
   - `CALCULATION_DERIVATION`: `fee = amount * 0.02` formula
   - `PERSISTENCE_MUTATION`: `AccountRepository.save()`
   - `STATE_TRANSITION`: `PENDING_APPROVAL` -> `COMPLETED`
   - `EXTERNAL_NOTIFICATION`: `NotificationService.sendNotification()`
2. **Rules to Preserve**:
   - `amount > 50000` (THRESHOLD)
   - `balance < amount` (VALIDATION)
   - `fee = amount * 0.02` (CALCULATION)
   - `AccountStatus.BLOCKED` (CONDITIONAL)
   - `PENDING_APPROVAL` / `COMPLETED` (STATE_TRANSITION)
3. **Impact Surface**:
   - Direct Dependents: `AccountController`
   - Transitive Dependents: `AccountRepository`, `FraudService`
4. **Generated Execution Plan Sequence**:
   1. Task 1 (`SEPARATE_BUSINESS_RULE`): Separate transfer validation rules (`balance < amount`)
   2. Task 2 (`SEPARATE_BUSINESS_RULE`): Isolate transfer threshold approval rule (`amount > 50000`)
   3. Task 3 (`EXTRACT_CALCULATION`): Extract transfer fee calculation (`fee = amount * 0.02`)
   4. Task 4 (`ISOLATE_STATE_TRANSITION`): Isolate account state transition (`PENDING` -> `COMPLETED`)
   5. Task 5 (`ISOLATE_PERSISTENCE`): Isolate account balance persistence mutations
   6. Task 6 (`ISOLATE_EXTERNAL_NOTIFICATION`): Isolate transfer notification event dispatch
   7. Task 7 (`DEFINE_INTERFACE`): Define `TransferDomainService` contract interface (depends on Tasks 1–6)
   8. Task 8 (`INTRODUCE_FACADE`): Introduce `AccountServiceFacade` for caller backward compatibility (depends on Task 7)
   9. Task 9 (`MIGRATE_CALLER`): Update `AccountController` to consume facade interface (depends on Task 8)
   10. Task 10 (`PRESERVE_BEHAVIOR`): Verify invariant preservation for transfer business rules (depends on Task 9)
   11. Task 11 (`ADD_VERIFICATION_CHECKPOINT`): Execute verification checkpoint suite for `AccountService` (depends on Task 10)

---

## 8. Verification & Test Plan

### Automated Unit & Integration Tests:
- `tests/test_modernization_plan_generator.py`:
  - Plan generation logic, task taxonomy mapping, DAG topological sort, preservation rules mapping, verification checkpoint generation, zero fake score assertions.
- `tests/test_api_modernization_plan.py`:
  - REST endpoints (`/plans/generate`, `/plans/{id}`, `/plans/{id}/review`, `/tasks/{id}/status`, `/tasks/{id}/reorder`, `/plans/{id}/explain`).

### End-to-End Live Browser Verification:
1. Start PostgreSQL backend and Vite frontend.
2. Ingest `LegacyBank` repository, run System X-Ray, Business Logic Recovery, Impact Analysis, and Modernization Strategy.
3. Open **Modernization Plan** workspace tab.
4. Verify generated tasks for `AccountService`, inspect dependencies, rules to preserve, impact surface, and verification checkpoints.
5. Perform human review (mark plan `APPROVED`, update task status, reorder task).
6. Request AI Gateway plan explanation and verify narrative response.

---

## 9. Proposed File Changes Summary

### [NEW] Backend & Alembic Files
- `d:/LegacyX/backend/app/models/modernization_plan.py`
- `d:/LegacyX/backend/app/modernization/plan_generator.py`
- `d:/LegacyX/backend/alembic/versions/006_modernization_execution_plan.py`
- `d:/LegacyX/backend/tests/test_modernization_plan_generator.py`
- `d:/LegacyX/backend/tests/test_api_modernization_plan.py`

### [MODIFY] Existing Backend Files
- `d:/LegacyX/backend/app/models/__init__.py`
- `d:/LegacyX/backend/app/schemas/modernization.py`
- `d:/LegacyX/backend/app/api/modernization.py`
- `d:/LegacyX/backend/app/ai/gateway.py`

### [NEW / MODIFY] Frontend Files
- `d:/LegacyX/frontend/src/features/modernization/ModernizationPlanPage.tsx`
- `d:/LegacyX/frontend/src/features/projects/ProjectWorkspacePage.tsx`
- `d:/LegacyX/frontend/src/services/api.ts`
- `d:/LegacyX/frontend/src/types/index.ts`

### [NEW] Documentation Files
- `d:/LegacyX/docs/decisions/ADR-011-modernization-execution-planning.md` (Already Created)
- `d:/LegacyX/docs/architecture/modernization-execution-plan.md` (Already Created)
- `d:/LegacyX/docs/phase7_implementation_plan.md` (This File)
