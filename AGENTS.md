# AGENTS.md — LEGACYX Engineering Rules

> These rules are mandatory for every contributor, human or AI agent, across every phase of the LEGACYX project.
> Any deviation requires an explicit Architecture Decision Record (ADR) and written approval from the project lead.

---

## 1. Architecture Rules

### 1.1 No Unauthorized Architecture Changes
Do not redesign the architecture, rename layers, or restructure module boundaries without an approved ADR.
Changes that cross architectural boundaries (e.g., putting analysis logic in the API layer) require explicit approval.

### 1.2 No Unnecessary Dependencies
Do not introduce third-party libraries without justification.
Every new dependency must be listed in the relevant `requirements.txt` or `package.json` with a brief comment explaining its purpose.
Avoid adding dependencies that duplicate functionality already present in the project.

### 1.3 Layer Discipline
Respect the defined layer separation at all times:

| Layer | Responsibility |
|---|---|
| Presentation | UI components and routing only |
| API / Orchestration | FastAPI routes, request validation, response shaping |
| Application Services | Orchestration of domain services |
| Domain Services | Business logic |
| Analysis Engine | Deterministic static analysis of source code |
| AI Intelligence | AI-assisted reasoning only — never source of truth |
| Modernization Engine | Code transformation, migration planning |
| Validation Engine | Build, test, and behavioral validation |
| Persistence | SQLAlchemy models, Alembic migrations, Redis |
| Background Workers | Long-running async jobs |

Do not put domain logic inside React components.
Do not call AI providers directly from API routes.
Do not call the database directly from UI components.

---

## 2. Deterministic Analysis Rules

### 2.1 Deterministic Analysis is the Source of Truth
All repository facts (files, classes, methods, imports, dependencies, call relationships, API endpoints, database references) MUST be established by deterministic static analysis, not by AI inference.

### 2.2 AI Must Not Invent Evidence
AI may reason over established facts.
AI must NEVER:
- Invent file paths, class names, or method names not found in the repository.
- Claim a dependency exists that was not detected by the analysis engine.
- Claim a call relationship exists without static analysis evidence.
- Invent test results.
- Claim behavioral equivalence without execution evidence.

### 2.3 Facts Must Be Traceable
Every system fact must be traceable to the analysis run that produced it.
The data model must record the analysis run ID alongside every derived entity.

---

## 3. AI Gateway Rules

### 3.1 No Scattered AI Calls
AI provider calls must only occur through the central AI abstraction layer (`backend/app/ai/`).
Do not call OpenAI, IBM watsonx, or any other AI API directly from services, routes, or analysis modules.

### 3.2 AI Output is Not Verified Automatically
AI-generated content (explanations, migration plans, transformation candidates) must never be marked as verified without actual execution evidence.

### 3.3 Minimum Context to AI
AI prompts must receive only the minimum source context necessary to answer the question.
Do not send entire repositories, credentials, secrets, or unrelated source files to AI providers.

---

## 4. Migration Safety Rules

### 4.1 Original Source is Immutable
Generated or transformed code must NEVER overwrite the original repository source.
All generated code must be stored in isolated, clearly labelled storage separate from the source repository.

### 4.2 Explicit Migration State
Every migration step must have an explicit state machine:

```
PROPOSED → REVIEW → APPROVED → EXECUTING → VALIDATING → VERIFIED → FAILED
```

A migration step cannot advance to the next state without satisfying that state's entry conditions.

### 4.3 No Verification Without Evidence
A migration step MUST NOT be marked `VERIFIED` without actual validation evidence (build result, test result, or behavioral comparison result).

### 4.4 Validation Failure Halts Progression
Validation failures must stop automatic migration progression.
A human must review the failure before any continuation.

### 4.5 Human Approval Before Impactful Changes
Any migration action that modifies files, infrastructure, or data must have a recorded human approval before execution.

### 4.6 Auditability
Every migration action must produce an immutable audit event recording:
- actor (user or system)
- timestamp
- action
- target
- metadata

---

## 5. Validation Rules

### 5.1 Build, Tests, and Behavior are Distinct
Build success does not imply test success.
Test success does not imply behavioral equivalence.
Do not conflate these three validation dimensions.

### 5.2 No Fake Progress
Progress events during analysis, migration, or validation must originate from actual backend job execution.
Do not fabricate, estimate, or mock progress events in production paths.

### 5.3 Mismatch Must Be Reported
If behavioral comparison detects output mismatch between the legacy and modern systems, the mismatch must be surfaced, explained, and logged — never silently suppressed.

---

## 6. Code Quality Rules

### 6.1 Prefer Small, Testable Modules
Modules must have a single clear responsibility.
Large modules must be decomposed before adding new functionality.

### 6.2 Every Feature Requires Tests
Every major feature must have automated tests.
Do not merge a feature without tests for its core behavior.

### 6.3 Do Not Modify Unrelated Code
When implementing a feature, do not silently modify unrelated modules.
If a side change is needed, document it explicitly in the pull request / commit message.

### 6.4 Follow Phase Lifecycle
Every phase follows: `PLAN → IMPLEMENT → TEST → VERIFY → FREEZE`

Do not skip steps.
Do not implement future-phase features early because they seem convenient.

### 6.5 Phase Gate
Do not proceed to the next phase if required tests for the current phase fail.

---

## 7. Security Rules

### 7.1 No Secrets in Prompts
Secrets, credentials, API keys, and tokens detected in repository source code must never be forwarded to AI providers.
The analysis engine must detect and redact such values before any AI call.

### 7.2 Path Sanitization
All file paths derived from uploaded or cloned repositories must be sanitized.
Repository extraction must prevent path traversal attacks.

### 7.3 Isolated Code Execution
Arbitrary code execution (builds, tests, behavioral validation) must eventually occur inside isolated execution environments (containers, sandboxes).
Do not execute arbitrary user-provided code in the main application process.

### 7.4 Project-Scoped Authorization
Authorization must be project-scoped.
A user may not access, read, or modify artifacts from a project they do not own or have been explicitly granted access to.

### 7.5 Generated Artifacts Are Sensitive
Generated code artifacts must be stored in access-controlled storage.
Source code from customer repositories is confidential and must be handled accordingly.

---

## 8. Documentation Rules

### 8.1 ADR for Major Decisions
Every major architectural decision must produce an ADR in `docs/decisions/`.
ADR format: `ADR-NNN-title.md`

### 8.2 Phase Zero Freeze
Documents created in Phase 0 (`AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT_SPEC.md`, `IMPLEMENTATION_PLAN.md`, ADRs) define the architectural contract.
They may only be updated through an approved change process.

### 8.3 Keep Documentation Current
When implementation contradicts documentation, update the documentation and create an ADR explaining the deviation.
Do not allow implementation and documentation to silently diverge.

---

## 9. Additional Engineering Rules

- Do not expose internal stack traces or database errors directly to the frontend.
- Do not hardcode environment-specific configuration. Use environment variables.
- Do not commit secrets, API keys, or credentials to the repository.
- Use structured logging throughout the backend. Log format must be machine-parseable (JSON).
- Long-running operations must report progress through the defined event system. Do not block API threads.
- Database schema changes require Alembic migrations. Do not alter schema by hand in production.
- All API responses must use defined Pydantic schemas. Do not return raw ORM objects.
- Every API route must validate its inputs. Reject malformed requests with appropriate HTTP status codes.
- Do not assume repository analysis is complete before querying analysis results.
- Background jobs must be idempotent where possible. Failed jobs must be restartable without side effects.

---

*Last updated: Phase 0 — Architecture Contract*
*Approved by: Project Lead*
