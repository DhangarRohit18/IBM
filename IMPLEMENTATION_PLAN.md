# IMPLEMENTATION_PLAN.md — LEGACYX Phase Roadmap

> This document is the authoritative phase-by-phase development roadmap for LEGACYX.
> Each phase has explicit objectives, scope, acceptance criteria, and explicit exclusions.
> No phase may begin without explicit approval from the project lead.

---

## Phase Overview

| Phase | Name | Depends On |
|---|---|---|
| 0 | Architecture Contract & Repository Foundation | — |
| 1 | Foundation Stack | 0 |
| 2 | Repository Ingestion | 1 |
| 3 | System X-Ray / Deterministic Analysis | 2 |
| 4 | Business Logic Recovery | 3 |
| 5 | Change Impact Explorer | 3 |
| 6 | Modernization Strategy Engine | 4, 5 |
| 7 | Migration Planner | 6 |
| 8 | AI-Assisted Transformation / IBM Bob Integration | 7 |
| 9 | Behavioral Validation | 8 |
| 10 | Migration Governance & Audit | 9 |
| 11 | Real-Time Progress Experience | 3, 7, 9 |
| 12 | End-to-End Demo Hardening | 11 |
| 13 | Final UI / UX / Reliability Polish | 12 |

---

## Phase 0 — Architecture Contract & Repository Foundation

### Objective
Establish the architecture contract, engineering rules, repository structure, product specification, data model proposal, implementation roadmap, and development conventions that all future phases must follow.

### Features
- Complete documentation suite
- Architecture Decision Records
- Engineering rules (AGENTS.md)
- Phase roadmap

### Technical Work
- Create `AGENTS.md`
- Create `README.md`
- Create `ARCHITECTURE.md`
- Create `PRODUCT_SPEC.md`
- Create `IMPLEMENTATION_PLAN.md`
- Create `docs/decisions/ADR-001` through `ADR-006`
- Establish `docs/` directory structure

### Dependencies
None.

### Tests
No automated tests. Documentation consistency review.

### Acceptance Criteria
- [ ] AGENTS.md exists and defines all mandatory engineering rules
- [ ] ARCHITECTURE.md defines all layers, directories, and API boundaries
- [ ] PRODUCT_SPEC.md defines all features and the domain model
- [ ] IMPLEMENTATION_PLAN.md covers all phases
- [ ] All 6 initial ADRs exist
- [ ] No application code has been written
- [ ] No architectural ambiguity remains for Phase 1

### Must NOT Be Implemented Yet
- Application features of any kind
- Database models
- API endpoints
- Frontend components
- AI integration
- Analysis engine
- Migration logic
- Validation logic

---

## Phase 1 — Foundation Stack

### Objective
Stand up the complete development environment with running frontend and backend, CI structure, database, and infrastructure.

### Features
- Runnable backend (FastAPI, hello-world health endpoint)
- Runnable frontend (React/Vite/Tailwind, blank shell)
- Database connectivity (PostgreSQL + SQLAlchemy)
- Redis connectivity
- Docker Compose for all infrastructure
- Alembic migration setup
- Logging infrastructure
- Environment configuration system
- Basic project and user ORM models with initial migration

### Technical Work

#### Backend
- Initialize FastAPI application (`backend/app/`)
- Core configuration module (`backend/app/core/config.py`)
- Structured JSON logging (`backend/app/core/logging.py`)
- SQLAlchemy 2.x async setup
- Alembic configuration
- Health endpoint: `GET /api/v1/health`
- Base ORM model (timestamp mixin)
- `users` and `projects` ORM models
- Initial Alembic migration for users + projects

#### Frontend
- Vite + React + TypeScript project scaffold
- Tailwind CSS configuration
- shadcn/ui setup
- React Router setup
- TanStack Query setup
- Blank layout shell (header, sidebar placeholder, content area)
- API base client

#### Infrastructure
- `docker-compose.yml` with: postgres, redis, backend, frontend, worker
- Environment variable management (`.env.example`)

### Dependencies
Phase 0 complete.

### Tests
- Backend: health endpoint returns 200
- Backend: database connection is healthy
- Backend: Redis connection is healthy
- Frontend: application renders without errors

### Acceptance Criteria
- [ ] `docker compose up` starts all services without errors
- [ ] `GET /api/v1/health` returns 200 with status details
- [ ] Frontend loads at `http://localhost:5173`
- [ ] PostgreSQL migrations apply cleanly
- [ ] All 4 tests pass
- [ ] No analysis, AI, or migration code exists

### Must NOT Be Implemented Yet
- Repository ingestion
- Analysis engine
- Business logic features
- AI integration
- Migration features
- Validation features
- Any substantive UI beyond the shell

---

## Phase 2 — Repository Ingestion

### Objective
Allow users to create a project and upload a repository (ZIP). The repository is stored safely and its basic metadata (language, framework, build tool) is detected deterministically.

### Features
- Project CRUD (create, read, list, delete)
- Repository ZIP upload
- Path traversal prevention
- Repository storage in object storage
- Deterministic technology detection (language, framework, build tool)
- Repository status tracking

### Technical Work

#### Backend
- `projects` API endpoints (POST, GET, LIST, DELETE)
- `repositories` API endpoints (POST, GET)
- Object storage abstraction (`backend/app/services/storage.py`)
- Local filesystem implementation of storage abstraction
- ZIP extraction with path sanitization
- Technology detection:
  - Language detection (file extensions)
  - Framework detection (pom.xml contents, Spring imports)
  - Build tool detection (pom.xml, build.gradle presence)
- `repositories` ORM model + migration

#### Frontend
- Project creation form
- Project list page
- Repository upload form (drag-and-drop ZIP)
- Repository status display
- Technology detection result display

### Dependencies
Phase 1 complete.

### Tests
- Project CRUD operations
- ZIP upload stores file correctly
- Path traversal attempt is rejected
- Technology detection correctly identifies Java/Spring/Maven

### Acceptance Criteria
- [ ] User can create a project
- [ ] User can upload a ZIP
- [ ] Path traversal attempt returns 400/422 error
- [ ] Technology is detected correctly for a sample Java/Spring/Maven project
- [ ] Repository status transitions work correctly
- [ ] All tests pass

### Must NOT Be Implemented Yet
- AST parsing
- Dependency analysis
- Business logic analysis
- AI calls of any kind

---

## Phase 3 — System X-Ray / Deterministic Analysis

### Objective
Implement the core analysis engine for Java/Spring repositories. Produce a complete deterministic map: files, classes, methods, imports, dependencies, call relationships, API endpoints, and database interactions.

### Features
- Analysis run triggering (async job)
- File discovery and cataloguing
- Java AST parsing (class, method, annotation extraction)
- Import extraction
- Class-level dependency graph
- Method call graph
- Spring REST endpoint detection
- JPA/JDBC database interaction detection
- System X-Ray visualization (interactive graph)

### Technical Work

#### Analysis Engine
- Scanner: file discovery, language filtering
- Java parser: class, method, annotation extraction (using javalang or similar)
- Import extractor
- Dependency graph builder
- Call graph builder
- Spring endpoint detector (Controller/RestController annotations)
- JPA entity detector, JPQL/SQL query extractor
- Analysis results persisted to PostgreSQL

#### Backend
- Analysis run API endpoints
- Background worker: analysis job
- Redis job queue integration
- Architecture API endpoints (classes, methods, dependencies, call graph, APIs, database ops)

#### Frontend
- Analysis trigger button
- Analysis progress display
- System X-Ray page:
  - Interactive dependency graph (React Flow)
  - File tree browser
  - Class/method browser
  - API endpoint table
  - Database interaction table

### Dependencies
Phase 2 complete.

### Tests
- File discovery finds all Java files
- Java parser correctly extracts classes and methods from sample source
- Dependency graph correctly identifies import relationships
- Call graph correctly identifies method call relationships
- Spring endpoint detector finds REST endpoints
- Database interaction detector finds JPA entities and queries

### Acceptance Criteria
- [ ] Analysis completes on a sample Java/Spring repository without errors
- [ ] All files, classes, methods catalogued
- [ ] Dependency graph is correct and complete for the sample
- [ ] Call graph is correct for the sample
- [ ] REST endpoints are detected
- [ ] Database interactions are detected
- [ ] System X-Ray page renders the interactive graph
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Business logic recovery
- Impact analysis
- Modernization strategy
- AI calls (other than scaffolding)
- Migration planner
- Behavioral validation

---

## Phase 4 — Business Logic Recovery

### Objective
Identify business-rule candidates from the analyzed source code and surface them with source evidence. Use the AI gateway to generate human-readable explanations, clearly labelled.

### Features
- Business-rule candidate detection (heuristic-based, deterministic)
- Source evidence for every rule (file, line range)
- AI explanation generation (IBM watsonx via AI gateway)
- Business logic page with source evidence display

### Technical Work

#### Analysis Engine
- Business rule candidate detector:
  - Validation logic patterns
  - Calculation patterns
  - Eligibility/condition patterns
  - Domain constant patterns
- Rule evidence extractor (source fragment, line range)

#### AI Gateway (First Real Use)
- Implement `AIProvider` abstract base class
- Implement `AIGateway`
- Implement IBM watsonx provider (or stub)
- Implement `explain_business_rule()` capability
- Prompt template for business rule explanation

#### Backend
- Business rules API endpoints
- AI explanation endpoint (on-demand, not automatic)

#### Frontend
- Business Logic page
- Rule list with source reference
- Source code viewer (highlight relevant lines)
- AI explanation panel (labelled "AI-generated")

### Dependencies
Phase 3 complete.

### Tests
- Business rule candidate detection finds expected rules in LegacyBank sample
- AI gateway correctly routes to provider
- AI explanation is returned and stored
- Source evidence links are correct

### Acceptance Criteria
- [ ] Business rule candidates detected in LegacyBank sample
- [ ] Every rule has source file + line range
- [ ] AI explanation is generated and correctly labelled
- [ ] AI must not invent evidence for a rule that does not exist in the source
- [ ] Business Logic page renders correctly
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Change impact analysis
- Modernization strategy
- Migration planning
- Code transformation
- Behavioral validation

---

## Phase 5 — Change Impact Explorer

### Objective
Given any component (class, method, API), compute and display its full blast radius: direct dependencies, transitive dependents, affected workflows, and potentially affected tests.

### Features
- Impact computation for any component
- Transitive dependency traversal
- Affected workflow identification
- Impact visualization (graph)
- Impact report export

### Technical Work

#### Analysis Engine
- Transitive dependency resolver (graph traversal)
- Impact scoring (component → dependents → workflows → tests)

#### Backend
- Impact API endpoint

#### Frontend
- Change Impact page
- Component selector
- Impact graph (React Flow)
- Tabular impact detail

### Dependencies
Phase 3 complete.

### Tests
- Transitive dependency traversal is correct for known graph
- Impact of removing a known component is computed correctly

### Acceptance Criteria
- [ ] Impact computed correctly for known LegacyBank component
- [ ] Impact graph renders in UI
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Modernization strategy
- Migration planning
- Code transformation
- Behavioral validation

---

## Phase 6 — Modernization Strategy Engine

### Objective
For each significant component, recommend a modernization strategy (Refactor / Replatform / Extract / Replace / Retain) with an evidence-backed, human-readable rationale. No numerical scores.

### Features
- Per-component strategy recommendation
- Rationale generation (AI-assisted, labelled)
- Risk and complexity classification
- Human review and override

### Technical Work

#### AI Gateway
- `recommend_strategy()` capability
- Prompt template: strategy recommendation with component facts

#### Modernization Module
- Strategy classifier (heuristic pre-filtering before AI)
- Rationale generator

#### Backend
- Modernization API endpoints
- Strategy storage

#### Frontend
- Modernization Plan page
- Per-component recommendation cards
- Human override UI (dropdown + rationale field)

### Dependencies
Phase 4, Phase 5 complete.

### Tests
- Strategy classifier heuristics produce expected output for known component patterns
- AI rationale is returned and stored
- Human override is persisted correctly

### Acceptance Criteria
- [ ] All significant LegacyBank components have strategy recommendations
- [ ] Every recommendation has a human-readable rationale
- [ ] Human override works and is audited
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Migration planning
- Code transformation
- Behavioral validation

---

## Phase 7 — Migration Planner

### Objective
Generate an ordered migration plan from the strategy recommendations. Each step has explicit state, prerequisites, objective, and validation requirements.

### Features
- Migration plan generation (AI-assisted ordering, labelled)
- Ordered step list with prerequisites
- State machine enforcement
- Human approval workflow (REVIEW → APPROVED)
- Migration plan page

### Technical Work

#### AI Gateway
- `generate_migration_plan()` capability
- Prompt template: ordered plan from strategy recommendations

#### Modernization Module
- Plan generator
- Prerequisite resolver (topological sort)

#### Backend
- Migration plan API endpoints
- Migration step state machine
- Approval endpoints

#### Frontend
- Migration page
- Step list with state indicators
- Approval UI
- Step detail modal

### Dependencies
Phase 6 complete.

### Tests
- Plan generation produces an ordered list
- Prerequisite ordering is correct (topological sort)
- State transitions enforce rules (cannot skip REVIEW)
- Approval action is audited

### Acceptance Criteria
- [ ] Migration plan generated for LegacyBank
- [ ] Steps are ordered with correct prerequisites
- [ ] State machine transitions are enforced
- [ ] Human approval is required before EXECUTING state
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Code transformation
- Behavioral validation
- Execution of migration steps

---

## Phase 8 — AI-Assisted Transformation / IBM Bob Integration

### Objective
Generate candidate modernized code for approved migration steps. Original source remains immutable. Generated code is isolated in artifact storage.

### Features
- Code transformation candidate generation
- Test generation candidate
- IBM watsonx full integration
- Generated artifact storage and display

### Technical Work

#### AI Gateway
- Full IBM watsonx provider implementation
- `transform_code()` capability
- `generate_tests()` capability
- Secret detection and redaction before prompts

#### Modernization Module
- Transformer: generates code candidate from source fragment + target spec
- Artifact storage: write candidate to isolated path

#### Backend
- Transformation trigger endpoints
- Candidate retrieval endpoints

#### Frontend
- Code diff viewer (original vs. candidate)
- Transformation trigger button (in Migration step detail)
- Candidate artifact display

### Dependencies
Phase 7 complete.

### Tests
- Transformation generates output without error
- Original source file is unchanged after transformation
- Generated artifact is stored in isolated path
- Secret in source fragment is redacted before AI call

### Acceptance Criteria
- [ ] Transformation generates candidate for a LegacyBank migration step
- [ ] Original source is unchanged
- [ ] Candidate is stored in isolated path
- [ ] Secret redaction is verified
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Behavioral validation
- Full governance/audit

---

## Phase 9 — Behavioral Validation

### Objective
Execute the same scenarios against the legacy system and the modern candidate system, capture outputs, compare them, and produce evidence-backed validation results.

### Features
- Scenario execution against legacy system
- Scenario execution against modern candidate
- Output comparison
- Mismatch detection and display
- AI explanation of mismatches (labelled)
- Validation result persistence (immutable)

### Technical Work

#### Validation Engine
- Scenario generator (from analysis results)
- Legacy runner (build + execute in isolated environment)
- Modern runner (build + execute in isolated environment)
- Output comparator (field-level diff)
- Behavioral result recorder

#### AI Gateway
- `explain_validation_failure()` capability

#### Backend
- Validation run API endpoints
- Validation results API

#### Frontend
- Validation page
- Run list
- Scenario results table
- Output diff viewer
- AI mismatch explanation panel

### Dependencies
Phase 8 complete.

### Tests
- Scenario execution produces output for known Java method
- Output comparator correctly detects match and mismatch
- Mismatch is persisted with diff details
- AI explanation is requested only on mismatch

### Acceptance Criteria
- [ ] Behavioral validation runs successfully on LegacyBank scenario
- [ ] Match case correctly reports VERIFIED
- [ ] Mismatch case correctly reports MISMATCH with diff evidence
- [ ] AI explanation is labelled correctly
- [ ] Validation results are immutable after recording
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Full governance/audit
- Real-time progress
- UI polish

---

## Phase 10 — Migration Governance & Audit

### Objective
Complete the migration governance layer: full state machine enforcement, audit trail, approval actions, rollback support, and migration artifact management.

### Features
- Full audit trail (all auditable events)
- Audit Trail page
- Rollback capability for FAILED steps
- Migration checkpoint support
- Artifact management (view, download)

### Technical Work

#### Backend
- Audit event writer (called from all services)
- Audit trail API endpoint
- Rollback endpoint
- Artifact listing and download endpoints

#### Frontend
- Audit Trail page (filterable, chronological)
- Rollback UI (in migration step)
- Artifact browser

### Dependencies
Phase 9 complete.

### Tests
- All key actions produce audit events
- Audit events are immutable (update/delete rejected)
- Rollback correctly reverts a FAILED step

### Acceptance Criteria
- [ ] Every auditable event is recorded
- [ ] Audit trail page shows complete history for LegacyBank demo
- [ ] Audit events cannot be modified
- [ ] Rollback works for FAILED steps
- [ ] All tests pass

### Must NOT Be Implemented Yet
- Real-time progress
- UI polish

---

## Phase 11 — Real-Time Progress Experience

### Objective
Surface actual progress from background jobs (analysis, migration, validation) to the frontend via WebSocket events. No fake progress.

### Features
- WebSocket progress events
- Real-time progress display for analysis, migration, validation
- Job history and status

### Technical Work

#### Backend
- WebSocket endpoint
- Event emitter in workers (analysis, migration, validation workers)
- Event schema: `{ job_id, project_id, event_type, progress, message, timestamp }`

#### Frontend
- WebSocket client hook (`useWebSocket`)
- Progress overlays for long-running operations
- Live log stream display

### Dependencies
Phase 3, Phase 7, Phase 9 complete.

### Tests
- WebSocket connection establishes correctly
- Analysis job emits `analysis.started`, `analysis.completed` events
- Frontend receives and displays events

### Acceptance Criteria
- [ ] All long-running jobs emit real progress events
- [ ] Frontend displays real-time progress
- [ ] No simulated / fake progress
- [ ] All tests pass

---

## Phase 12 — End-to-End Demo Hardening

### Objective
Demonstrate the full LEGACYX workflow end-to-end using the LegacyBank sample repository, from upload to behavioral validation.

### Features
- LegacyBank sample repository (complete)
- End-to-end walkthrough: ingest → analyze → review X-Ray → review business logic → explore impact → review strategy → plan migration → transform → validate
- Demo mode (seeded data for reliable demo)

### Technical Work
- Build LegacyBank sample repository (Java/Spring/Maven)
- Seed LegacyBank data into LEGACYX
- Fix any blocking issues found during end-to-end run
- Demo guide documentation

### Dependencies
Phase 11 complete.

### Tests
- Full E2E test for the LegacyBank flow
- Regression tests for all previous phases

### Acceptance Criteria
- [ ] LegacyBank can be uploaded and fully analyzed
- [ ] All platform features work on LegacyBank
- [ ] Behavioral validation produces expected results
- [ ] E2E test passes
- [ ] Demo is reproducible

---

## Phase 13 — Final UI / UX / Reliability Polish

### Objective
Harden the application for a production-quality hackathon demonstration. Focus on UI quality, error handling, reliability, and performance.

### Features
- Polished UI across all pages
- Comprehensive error handling (API errors, validation errors, network errors)
- Loading states
- Empty states
- Responsive layout
- Performance optimization
- Accessibility review

### Technical Work
- UI audit — identify and fix rough edges
- Error boundary implementation
- Toast notifications for all async operations
- Performance profiling
- Accessibility improvements

### Dependencies
Phase 12 complete.

### Tests
- Accessibility checks
- Performance benchmarks
- Error handling test cases

### Acceptance Criteria
- [ ] All pages render cleanly with no visual regressions
- [ ] All errors are handled gracefully (no blank screens)
- [ ] Performance targets met
- [ ] Application is ready for hackathon demonstration

---

*Last updated: Phase 0 — Architecture Contract*
