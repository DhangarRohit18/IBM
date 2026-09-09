# ARCHITECTURE.md — LEGACYX Architecture Reference

> This document is the architecture contract for LEGACYX.
> It must not be changed without an approved ADR.

---

## 1. Architecture Philosophy

LEGACYX is built on three foundational principles:

1. **Deterministic analysis precedes AI reasoning.** The analysis engine establishes facts about the repository. AI reasons over those facts.
2. **Immutability of the original source.** The repository under analysis is never modified. Generated artifacts are isolated.
3. **Explicit human control over migration.** Every impactful action requires a recorded approval. No automatic progression past validation failure.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  React · TypeScript · Vite · Tailwind · shadcn/ui        │
│  React Flow · TanStack Query · React Router · Zustand    │
└─────────────────────────────────┬───────────────────────┘
                                  │  HTTP / WebSocket
┌─────────────────────────────────▼───────────────────────┐
│                  FastAPI API Layer                        │
│  Request validation · Response shaping · Auth            │
└─────────────────────────────────┬───────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────┐
│               Application Services                       │
│  Orchestration of domain services / cross-cutting logic  │
└──┬──────────┬──────────┬──────────┬──────────┬──────────┘
   │          │          │          │          │
┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌──▼───┐  ┌──▼──────────┐
│Ana- │  │  AI   │  │Modern-│  │Valid-│  │ Background  │
│lysis│  │Gate-  │  │ization│  │ation │  │  Workers    │
│Eng. │  │way    │  │Engine │  │Eng.  │  │ (Redis Q)   │
└──┬──┘  └───┬───┘  └───┬───┘  └──┬───┘  └──────────┬──┘
   │         │           │         │                  │
┌──▼─────────▼───────────▼─────────▼──────────────────▼──┐
│          Persistence Layer                               │
│  PostgreSQL (SQLAlchemy 2.x / Alembic)                   │
│  Redis (cache + job queue)                               │
│  Object Storage (local filesystem now, S3-compat future) │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Backend Directory Structure

```
backend/
├── app/
│   ├── api/                  # FastAPI routers, request/response schemas
│   │   ├── projects.py
│   │   ├── repositories.py
│   │   ├── analysis.py
│   │   ├── architecture.py
│   │   ├── business_rules.py
│   │   ├── impact.py
│   │   ├── modernization.py
│   │   ├── migration.py
│   │   ├── validation.py
│   │   └── audit.py
│   │
│   ├── core/                 # App configuration, lifespan, logging, middleware
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── events.py
│   │
│   ├── models/               # SQLAlchemy ORM models (database schema)
│   │   ├── base.py
│   │   ├── project.py
│   │   ├── repository.py
│   │   ├── analysis.py
│   │   ├── code_entities.py
│   │   ├── business_rules.py
│   │   ├── migration.py
│   │   ├── validation.py
│   │   └── audit.py
│   │
│   ├── schemas/              # Pydantic v2 request/response models (API contract)
│   │   ├── project.py
│   │   ├── repository.py
│   │   ├── analysis.py
│   │   ├── code_entities.py
│   │   ├── business_rules.py
│   │   ├── migration.py
│   │   ├── validation.py
│   │   └── audit.py
│   │
│   ├── services/             # Application-level orchestration
│   │   ├── project_service.py
│   │   ├── repository_service.py
│   │   ├── analysis_service.py
│   │   ├── modernization_service.py
│   │   ├── migration_service.py
│   │   ├── validation_service.py
│   │   └── audit_service.py
│   │
│   ├── analysis_engine/      # Deterministic static analysis — source of truth
│   │   ├── scanner/          # File discovery, tech detection
│   │   ├── parser/           # Language AST parsing (Phase 3: Java)
│   │   ├── dependency/       # Dependency graph construction
│   │   ├── call_graph/       # Method call graph
│   │   ├── database/         # Database interaction detection
│   │   ├── api_detection/    # REST endpoint detection
│   │   └── business_rules/   # Business-rule candidate identification
│   │
│   ├── ai/                   # Provider-agnostic AI gateway
│   │   ├── base.py           # AIProvider abstract base class
│   │   ├── gateway.py        # AI gateway (capability routing)
│   │   ├── prompts/          # Prompt templates
│   │   └── providers/
│   │       ├── ibm_watsonx.py  # IBM watsonx (primary target)
│   │       └── openai.py       # OpenAI (fallback / testing)
│   │
│   ├── modernization/        # Migration planning, code transformation
│   │   ├── strategy.py       # Strategy recommendation engine
│   │   ├── planner.py        # Migration plan generation
│   │   └── transformer.py    # Code transformation (Phase 8+)
│   │
│   ├── validation/           # Build, test, behavioral validation
│   │   ├── scenario_generator/
│   │   ├── runner/
│   │   ├── comparator/
│   │   └── behavioral/
│   │
│   └── workers/              # Background job execution
│       ├── analysis_worker.py
│       ├── migration_worker.py
│       └── validation_worker.py
│
├── alembic/                  # Database migrations
├── tests/                    # Automated tests
├── pyproject.toml
└── requirements.txt
```

### 3.1 Layer Responsibilities

| Directory | Responsibility |
|---|---|
| `api/` | HTTP routing. Input validation. Call services. Shape responses. No business logic. |
| `core/` | Configuration, logging, security utilities, app lifespan events. |
| `models/` | SQLAlchemy ORM models. Defines database schema. No business logic. |
| `schemas/` | Pydantic v2 request/response models. API contract. |
| `services/` | Application-level orchestration. Calls analysis engine, AI gateway, validation engine. |
| `analysis_engine/` | Deterministic static analysis. Produces facts. No AI calls. |
| `ai/` | AI gateway abstraction. Routes capability calls to providers. No domain logic. |
| `modernization/` | Strategy recommendation and migration plan generation. |
| `validation/` | Runs builds, tests, behavioral scenarios. Records evidence. |
| `workers/` | Executes long-running jobs from Redis queue. Reports progress events. |

---

## 4. Analysis Engine Detail

The analysis engine is the most critical component of LEGACYX.
It must produce deterministic, reproducible results given the same input repository.

```
analysis_engine/
├── scanner/
│   ├── file_discoverer.py      # Enumerate all files in the repository
│   ├── tech_detector.py        # Detect language, framework, build tool
│   └── build_detector.py       # Detect Maven, Gradle, etc.
│
├── parser/
│   ├── java_parser.py          # Java AST parsing (Phase 3)
│   └── base_parser.py          # Language-agnostic parser interface
│
├── dependency/
│   ├── import_extractor.py     # Extract import statements
│   ├── dependency_resolver.py  # Resolve class-level dependencies
│   └── graph_builder.py        # Build dependency graph
│
├── call_graph/
│   ├── call_extractor.py       # Extract method call relationships
│   └── graph_builder.py        # Build call graph
│
├── database/
│   ├── query_detector.py       # Detect SQL, JPA, Hibernate usage
│   ├── table_extractor.py      # Extract referenced table names
│   └── operation_classifier.py # Classify CRUD operations
│
├── api_detection/
│   ├── endpoint_extractor.py   # Detect REST endpoints (Spring annotations)
│   └── contract_extractor.py   # Extract request/response contracts
│
└── business_rules/
    ├── candidate_detector.py   # Identify business-rule candidates
    └── rule_extractor.py       # Extract source evidence for each rule
```

---

## 5. AI Gateway Detail

```
ai/
├── base.py
│   └── AIProvider (abstract)
│       ├── explain_component(component_fact) → Explanation
│       ├── explain_business_rule(rule_fact) → Explanation
│       ├── recommend_strategy(component_facts) → StrategyRecommendation
│       ├── generate_migration_plan(analysis_result) → MigrationPlan
│       ├── transform_code(source_fragment, target_spec) → TransformationCandidate
│       ├── generate_tests(component_fact) → TestSuite
│       └── explain_validation_failure(mismatch_result) → Explanation
│
├── gateway.py
│   └── AIGateway
│       ├── resolve_provider() → AIProvider
│       └── capability routing
│
└── providers/
    ├── ibm_watsonx.py    # IBM watsonx implementation
    └── openai.py         # OpenAI implementation (testing/fallback)
```

**Rules enforced by the gateway:**
- Secrets detected in source fragments must be redacted before transmission.
- Prompt templates must be versioned.
- AI responses must be stored alongside the analysis results that prompted them.
- AI responses are never treated as deterministic facts.

---

## 6. Validation Engine Detail

```
validation/
├── scenario_generator/
│   └── generate scenarios from analysis results
│
├── runner/
│   ├── legacy_runner.py    # Execute scenario against legacy system
│   └── modern_runner.py    # Execute scenario against modern system
│
├── comparator/
│   └── compare outputs, detect mismatches
│
└── behavioral/
    └── record behavioral evidence
```

**Key invariant:** Validation results must always record:
- build result (success/failure + logs)
- test result (pass/fail counts + logs)
- behavioral result (match/mismatch + output diff)
- execution timestamp and environment

---

## 7. Frontend Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   ├── Router.tsx
│   │   └── Providers.tsx        # React Query, Router, Zustand
│   │
│   ├── components/              # Shared, reusable UI components
│   │   ├── layout/
│   │   ├── navigation/
│   │   ├── data-display/
│   │   ├── forms/
│   │   └── feedback/
│   │
│   ├── features/                # Feature-scoped modules (see below)
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── architecture/
│   │   ├── business-logic/
│   │   ├── impact/
│   │   ├── modernization/
│   │   ├── migration/
│   │   ├── validation/
│   │   └── audit/
│   │
│   ├── services/                # API clients (wraps fetch/axios)
│   │   ├── api.ts               # Base HTTP client
│   │   ├── projects.ts
│   │   ├── analysis.ts
│   │   ├── migration.ts
│   │   └── validation.ts
│   │
│   ├── hooks/                   # Reusable React hooks
│   │   ├── useProject.ts
│   │   ├── useAnalysis.ts
│   │   └── useWebSocket.ts
│   │
│   ├── stores/                  # Zustand stores (global UI state only)
│   │   └── workspaceStore.ts
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── project.ts
│   │   ├── analysis.ts
│   │   ├── migration.ts
│   │   └── validation.ts
│   │
│   └── utils/                   # Pure utility functions
│       ├── format.ts
│       ├── graph.ts
│       └── diff.ts
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 7.1 Feature Module Structure

Each feature module follows this internal structure:

```
features/[feature]/
├── components/       # Feature-specific UI components
├── hooks/            # Feature-specific hooks (TanStack Query)
├── services/         # Feature-specific API calls
├── types/            # Feature-specific types (if distinct from global)
└── index.ts          # Public API of the feature
```

### 7.2 UI Design Principles

- Prioritize **evidence** over decoration.
- Show **source references** (file, line range) for every analysis claim.
- Show **dependency relationships** as visual graphs (React Flow).
- Show **actual test results** and **execution logs**, not summaries.
- Show **approval states** as explicit labeled statuses.
- Avoid excessive scores, percentages, "AI confidence" numbers, and decorative metrics.
- Avoid generic chatbot interfaces.

---

## 8. API Architecture

All API routes are prefixed with `/api/v1`.

### Project Management
```
POST   /api/v1/projects                          Create project
GET    /api/v1/projects                          List projects
GET    /api/v1/projects/{id}                     Get project
DELETE /api/v1/projects/{id}                     Delete project
```

### Repository
```
POST   /api/v1/projects/{id}/repository          Upload / connect repository
GET    /api/v1/projects/{id}/repository          Repository status
```

### Analysis
```
POST   /api/v1/projects/{id}/analysis            Start analysis run
GET    /api/v1/projects/{id}/analysis            List analysis runs
GET    /api/v1/projects/{id}/analysis/{run_id}   Get analysis result
```

### System X-Ray
```
GET    /api/v1/projects/{id}/architecture        Architecture graph
GET    /api/v1/projects/{id}/files               File list
GET    /api/v1/projects/{id}/classes             Class list
GET    /api/v1/projects/{id}/dependencies        Dependency graph
GET    /api/v1/projects/{id}/call-graph          Call graph
GET    /api/v1/projects/{id}/apis                Detected API endpoints
GET    /api/v1/projects/{id}/database-ops        Database operations
```

### Business Logic
```
GET    /api/v1/projects/{id}/business-rules      Business rule candidates
GET    /api/v1/projects/{id}/business-rules/{rule_id}
POST   /api/v1/projects/{id}/business-rules/{rule_id}/explain  (AI)
```

### Impact
```
GET    /api/v1/projects/{id}/impact/{component_id}   Component impact
```

### Modernization
```
POST   /api/v1/projects/{id}/modernization/analyze   Strategy analysis
GET    /api/v1/projects/{id}/modernization/recommendations
```

### Migration
```
POST   /api/v1/projects/{id}/migration/plan          Generate plan
GET    /api/v1/projects/{id}/migration/plan          Get plan
GET    /api/v1/projects/{id}/migration/{step_id}
POST   /api/v1/projects/{id}/migration/{step_id}/approve
POST   /api/v1/projects/{id}/migration/{step_id}/reject
POST   /api/v1/projects/{id}/migration/{step_id}/execute
```

### Validation
```
POST   /api/v1/projects/{id}/validation/run          Start validation
GET    /api/v1/projects/{id}/validation              List runs
GET    /api/v1/projects/{id}/validation/{run_id}     Get result
```

### Audit
```
GET    /api/v1/projects/{id}/audit                   Audit trail
```

> These are architectural contracts only. Implementation begins in Phase 2+.

---

## 9. Asynchronous Job Architecture

Long-running operations (analysis, migration, validation) execute in background workers.

```
Frontend
   │
   ├─ POST /api/v1/projects/{id}/analysis  ──▶  FastAPI
   │                                              │
   │                                         Enqueue job
   │                                              │
   │                                         Redis Queue
   │                                              │
   │                                         Worker Process
   │                                              │
   │                                    ┌─────────┴─────────┐
   │                                    │   PostgreSQL       │
   │                                    │   Object Storage   │
   │                                    └─────────┬─────────┘
   │                                              │
   │                                    WebSocket Events
   │                                              │
   └─ WebSocket ◀──────────────────────────────────┘
```

### Progress Events

**Analysis:**
```
analysis.started
analysis.scanning
analysis.parsing
analysis.dependencies
analysis.call_graph
analysis.business_logic
analysis.completed
analysis.failed
```

**Migration:**
```
migration.started
migration.generating
migration.building
migration.testing
migration.completed
migration.failed
```

**Validation:**
```
validation.started
validation.running
validation.mismatch
validation.completed
validation.failed
```

Each event carries: `{ job_id, project_id, event_type, progress, message, timestamp }`

---

## 10. Migration State Machine

```
PROPOSED
    │
    ▼
  REVIEW ◀───── (human reviews)
    │
    ▼
APPROVED ◀───── (human approves)
    │
    ▼
EXECUTING ──────▶ FAILED
    │
    ▼
VALIDATING ─────▶ FAILED
    │
    ▼
VERIFIED
```

**State transition rules:**
- `PROPOSED → REVIEW`: automatic on creation
- `REVIEW → APPROVED`: requires explicit human approval action
- `REVIEW → PROPOSED`: human rejects — returned for revision
- `APPROVED → EXECUTING`: system starts execution
- `EXECUTING → VALIDATING`: execution completed successfully
- `EXECUTING → FAILED`: execution error
- `VALIDATING → VERIFIED`: all validation checks passed with evidence
- `VALIDATING → FAILED`: validation failed — human must review before retry

---

## 11. Security Architecture

### Threat Model Summary

| Threat | Mitigation |
|---|---|
| Malicious repository content (path traversal) | Sanitize all extracted paths. Validate against allowed base directory. |
| Secrets in source code sent to AI | Detect and redact secrets before AI prompts. |
| Unauthorized project access | Project-scoped authorization. JWT authentication. |
| Arbitrary code execution | Future: sandbox/container isolation for builds and tests. |
| Generated artifact exposure | Access-controlled object storage. No public URLs. |
| Prompt injection via source code | Sanitize source fragments inserted into prompts. |

### Authentication & Authorization
- Authentication: JWT bearer tokens (Phase 1+)
- Authorization: Project-scoped. Users may only access projects they own or have explicit access to.
- Service-to-service: Internal API keys (not exposed externally)

### Data Handling
- Repository source code is treated as confidential.
- AI providers receive only minimum required source context.
- Secrets detected in source must be redacted before any transmission.

---

## 12. Infrastructure

### Development (Docker Compose)
```yaml
services:
  postgres:    # PostgreSQL 15
  redis:       # Redis 7
  backend:     # FastAPI (uvicorn)
  worker:      # Background worker (arq or celery)
  frontend:    # Vite dev server
  storage:     # Local filesystem mount
```

### Future Production
- Container orchestration (Kubernetes or equivalent)
- S3-compatible object storage
- Managed PostgreSQL
- Managed Redis

---

*Last updated: Phase 0 — Architecture Contract*
