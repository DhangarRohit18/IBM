# LEGACYX

**Legacy Application Modernization & Behavioral Validation Platform**

> LEGACYX does not merely generate replacement code.
> It creates an evidence-backed understanding of the existing system, connects that understanding to modernization decisions, assists controlled transformation, and verifies whether behavior was preserved.

---

## Why LEGACYX?

Organizations running large legacy applications face a painful reality:

- **Invisible Complexity**: Codebases are undocumented, fragile, and difficult to modify safely.
- **Entangled Logic**: Core business rules are buried in procedural spaghetti code mixed with database persistence.
- **Implicit Blast Radius**: Dependencies are hidden; no one knows the true downstream impact of modifying a class.
- **Ungrounded AI Output**: Generic "AI → New Code" tools produce modern syntax without proving behavioral equivalence.
- **Unverified rewrites**: A migration that passes no empirical behavioral verification is not a successful migration.

Generic AI code generators solve the wrong problem. They produce output—they do not produce **trust**.

---

## What LEGACYX Does

LEGACYX implements a structured, evidence-backed 5-stage modernization pipeline:

```
DISCOVER  ──>  UNDERSTAND  ──>  DECIDE  ──>  CHANGE  ──>  VERIFY
```

| Stage | Capability | What Happens |
|---|---|---|
| **DISCOVER** | Repository Ingestion | Parse, checksum, and index repository files and technology stacks safely. |
| **UNDERSTAND** | System X-Ray & Logic Recovery | Parse Java ASTs, classify components, map call graphs, and extract business rules. |
| **DECIDE** | Impact & Strategy Planning | Trace blast radius graph traversal, score strategies, and generate topological DAG execution plans. |
| **CHANGE** | Controlled Transformation | Generate isolated modernization artifacts and side-by-side diffs with original source immutability. |
| **VERIFY** | Empirical Behavioral Validation | Run compilation, unit tests, and deterministic scenario comparisons in an isolated sandbox. |

---

## Key Differentiators

1. **Deterministic First. AI Second. Human Always in Control.**
   * Repository facts (AST nodes, call graphs, diffs, test exit codes, scenario comparisons) are established 100% deterministically.
   * AI reasons over established facts to provide explanations, risk narratives, and candidate code proposals.
   * Humans retain total decision authority to approve or reject all rules, strategies, plans, and code artifacts.
2. **Original Legacy Source is Immutably Preserved.**
   * Legacy source code in `storage/extracted/` is strictly read-only.
   * All transformed artifacts are written to isolated directories (`storage/modernized/`).
3. **Empirical Behavioral Validation.**
   * Code generation is not success. Verification requires execution evidence from `javac`, unit tests, and scenario matching.

---

## Built with IBM Bob

LEGACYX was developed with **IBM Bob** as an AI-assisted engineering environment.

IBM Bob supported codebase exploration, AST engine implementation, database migration creation, Pydantic schema validation, unit test writing, frontend React component building, and iterative verification across the project's modernization pipeline.

For a detailed account of how IBM Bob was used during development:

-> See [IBM_BOB_USAGE.md](IBM_BOB_USAGE.md)

---

## For Judges

### Core Workflow Overview

LEGACYX addresses the high-risk enterprise challenge of legacy system migration through an end-to-end evidence pipeline:

1. **Repository Ingestion & System X-Ray**: Safely ingests legacy application archives (ZIP format with Zip Slip protection), performs pure-Python Java AST parsing (`javalang`), classifies components into 8 architectural categories (Controller, Service, Entity, etc.), and generates an interactive SVG architecture graph with line-level evidence tracking.
2. **Business Logic Recovery & Impact Analysis**: Extracts deterministic business rule candidates from source constructs, generates natural language explanations via the central `AIGateway`, and calculates the complete downstream blast radius using recursive graph traversal.
3. **Modernization Strategy & DAG Execution Planning**: Scores candidate strategies (MODULARIZE, REFACTOR, STRANGLER_FIG), generates a topological Directed Acyclic Graph (DAG) task plan, and enforces human review approval state gates (`PROPOSED` -> `APPROVED`).
4. **Controlled Transformation & Empirical Validation**: Produces modernized Java code artifacts in isolated storage, generates side-by-side unified diffs, and executes compilation (`javac`), unit tests, and deterministic input/output scenario comparisons inside an isolated execution sandbox.

### Key Documentation

- [IBM Bob Usage](IBM_BOB_USAGE.md) — Detailed report on how IBM Bob technology assisted development
- [Hackathon Submission Checklist](docs/submission_checklist.md) — Complete submission & product verification status
- [Architecture Overview](ARCHITECTURE.md) — System boundaries, layer discipline, and data flows
- [Engineering Rules](AGENTS.md) — Mandatory governance rules for contributors
- [Product Specification](PRODUCT_SPEC.md) — Feature specifications and UI layout contracts
- [Architecture Decision Records (ADRs)](docs/decisions/) — 13 formal ADRs governing platform design
- [Phase Documentation](docs/architecture/) — Architectural deep-dives for Phases 2 through 9
- [Full Phase 3–9 Live Audit Report](docs/full_phase3_to_phase9_live_audit_report.md) — Comprehensive end-to-end verification report

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons | Responsive interactive workspace UI, SVG architecture graphs, diff viewers |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2 | High-performance REST endpoints, request validation, response shaping |
| **Persistence** | PostgreSQL 15 / SQLite, SQLAlchemy 2.x (async), Alembic | Relational storage for AST facts, rules, plans, and validation evidence |
| **Storage Engine** | LocalStorageProvider | Storage isolation for extracted legacy source and modernized code artifacts |
| **Analysis Engine** | Pure-Python Java AST Parser (`javalang` 0.13.0) | Deterministic parsing, component classification, and line evidence extraction |
| **AI Gateway** | `AIGateway` (`MockAIProvider`, `WatsonxProvider`) | Centralized AI abstraction layer for explanations and risk summaries |
| **Validation Sandbox**| `ValidationEngine` | Subprocess compilation (`javac`), unit testing, and output equivalence matching |

---

## Implemented End-to-End Pipeline (Phases 3–9)

| Phase | Capability | Implementation Status | Verification Evidence |
|---|---|---|---|
| **Phase 0** | Architecture Contract & Foundation | ✅ FROZEN | [AGENTS.md](AGENTS.md), [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Phase 1** | Foundation Stack & DB | ✅ FROZEN | Alembic baseline schema |
| **Phase 2** | Repository Ingestion | ✅ FROZEN | Checksum & Zip Slip tests ([docs/architecture/repository-ingestion.md](docs/architecture/repository-ingestion.md)) |
| **Phase 3** | System X-Ray (AST Analysis) | ✅ COMPLETE | AST parsing & graph tests ([docs/architecture/system-xray.md](docs/architecture/system-xray.md)) |
| **Phase 4** | Business Logic Recovery | ✅ COMPLETE | Candidate rule extraction ([docs/architecture/business-logic-recovery.md](docs/architecture/business-logic-recovery.md)) |
| **Phase 5** | Change Impact Explorer | ✅ COMPLETE | Graph traversal tests ([docs/architecture/impact-analysis.md](docs/architecture/impact-analysis.md)) |
| **Phase 6** | Modernization Strategy Engine | ✅ COMPLETE | Strategy scoring matrix ([docs/architecture/modernization-strategy.md](docs/architecture/modernization-strategy.md)) |
| **Phase 7** | Modernization Execution Plan | ✅ COMPLETE | Topological DAG task plans ([docs/architecture/modernization-execution-plan.md](docs/architecture/modernization-execution-plan.md)) |
| **Phase 8** | Controlled Code Transformation | ✅ COMPLETE | Patch diffs & isolated storage ([docs/architecture/controlled-modernization.md](docs/architecture/controlled-modernization.md)) |
| **Phase 9** | Empirical Behavioral Validation | ✅ COMPLETE | Sandboxed execution & scenarios ([docs/architecture/behavioral-validation.md](docs/architecture/behavioral-validation.md)) |
| **Phase 10** | Continuous Governance & Monitoring | 🔄 PLANNED | Post-hackathon roadmap item |

---

## API Endpoints Overview

* **Ingestion (Phase 2)**: `POST /api/v1/projects`, `POST /api/v1/projects/{id}/repositories/upload`
* **System X-Ray (Phase 3)**: `POST /api/v1/repositories/{id}/analysis`, `GET /api/v1/analysis/{id}/graph`, `GET /api/v1/analysis/{id}/classes`
* **Business Rules (Phase 4)**: `POST /api/v1/analysis/{id}/rules/extract`, `POST /api/v1/rules/{rule_id}/explain`, `PATCH /api/v1/rules/{rule_id}`
* **Impact Analysis (Phase 5)**: `POST /api/v1/analysis/{id}/impact`, `GET /api/v1/impact/{impact_id}`
* **Modernization Strategy (Phase 6)**: `POST /api/v1/impact/{impact_id}/strategies`, `POST /api/v1/strategies/{id}/override`
* **Execution Planning (Phase 7)**: `POST /api/v1/strategies/{id}/plans`, `POST /api/v1/plans/{id}/approve`
* **Code Transformation (Phase 8)**: `POST /api/v1/plans/{id}/transform`, `POST /api/v1/transformations/{id}/approve`
* **Behavioral Validation (Phase 9)**: `POST /api/v1/transformations/{id}/validation/run`, `POST /api/v1/validation/{run_id}/explain`, `POST /api/v1/validation/{run_id}/review`

---

## Testing & Verification Summary

LEGACYX has been thoroughly verified across all architectural layers:

* **Backend Unit & Integration Tests**: 57 passing pytest test cases covering API endpoints, database operations, static analysis, strategy scoring, transformation diffing, and validation sandbox execution.
* **Frontend Production Build**: Clean TypeScript compilation (`tsc -b`) and Vite production bundle verification with zero errors.
* **Database Schema Integrity**: 8 Alembic database migrations up to head (`008_validation.py`).
* **Live Browser End-to-End Audit**: Full journey execution on canonical `LegacyBank.zip` fixture from ZIP ingestion to Phase 9 empirical behavioral scenario validation report.

See [docs/full_phase3_to_phase9_live_audit_report.md](docs/full_phase3_to_phase9_live_audit_report.md) for full test metrics.

---

## Repository Structure

```
LegacyX/
├── IBM_BOB_USAGE.md                 # Hackathon IBM Bob technology usage documentation
├── README.md                        # Master project documentation
├── AGENTS.md                        # Engineering rules & layer discipline
├── ARCHITECTURE.md                  # Architectural specifications & system boundaries
├── PRODUCT_SPEC.md                  # Product feature specification
├── IMPLEMENTATION_PLAN.md           # Multi-phase execution roadmap
├── docker-compose.yml               # Multi-container orchestration
├── backend/                         # FastAPI Python backend application
│   ├── alembic/                     # Database migration scripts (001 to 008)
│   ├── app/
│   │   ├── ai/                      # Centralized AIGateway abstraction
│   │   ├── analysis/                # Deterministic Java AST parser & ComponentClassifier
│   │   ├── api/                     # REST API routers for Phases 2–9
│   │   ├── db/                      # SQLAlchemy database session & initialization
│   │   ├── impact/                  # Graph traversal & blast radius calculator
│   │   ├── models/                  # SQLAlchemy ORM database models
│   │   ├── schemas/                 # Pydantic v2 validation schemas
│   │   ├── strategy/                # StrategySelector matrix
│   │   ├── transformation/          # TransformationEngine & patch diff generator
│   │   └── validation/              # Subprocess execution sandbox & scenario matcher
│   └── tests/                       # Pytest test suite (57 passing tests)
├── frontend/                        # React 19 TypeScript Vite frontend application
│   ├── src/
│   │   ├── components/              # Workspace views, graph SVG, diff drawers
│   │   ├── api/                     # Axios API clients
│   │   └── types/                   # TypeScript interface definitions
│   └── package.json
├── docs/                            # Comprehensive project documentation
│   ├── submission_checklist.md      # Submission readiness verification list
│   ├── architecture/                # Phase 2–9 architectural deep dives
│   ├── decisions/                   # ADRs 001 through 013
│   └── full_phase3_to_phase9_live_audit_report.md
```

---

## Running Locally

```bash
# 1. Environment Configuration
cp .env.example .env

# 2. Run Backend Unit & Integration Tests (57 passing tests)
cd backend
python -m pytest tests/ -v

# 3. Verify Frontend Production Build
cd ../frontend
npm run build

# 4. Launch Full Stack (Option A: Docker Compose)
cd ..
docker compose up --build

# Option B: Manual Local Development
# Backend (Terminal 1):
cd backend
$env:DATABASE_URL="sqlite+aiosqlite:///./legacyx.db"
$env:DATABASE_SYNC_URL="sqlite:///./legacyx.db"
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8002

# Frontend (Terminal 2):
cd frontend
npm run dev
```

---

## Documentation Index

- [IBM Bob Technology Usage](IBM_BOB_USAGE.md)
- [Hackathon Submission Checklist](docs/submission_checklist.md)
- [Engineering Rules (AGENTS.md)](AGENTS.md)
- [System Architecture (ARCHITECTURE.md)](ARCHITECTURE.md)
- [Product Specification (PRODUCT_SPEC.md)](PRODUCT_SPEC.md)
- [Phase Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Architecture Decision Records (ADRs)](docs/decisions/)
- [Phase Architecture Guides](docs/architecture/)
- [Full Phase 3–9 Live Audit Report](docs/full_phase3_to_phase9_live_audit_report.md)
- [Phase 9 Verification Report](docs/phase9_verification_report.md)
