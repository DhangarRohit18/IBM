# PRODUCT_SPEC.md — LEGACYX Product Specification

> This document defines LEGACYX product requirements, features, UI model, data domain model, and the demonstration target.
> It complements ARCHITECTURE.md (technical) and IMPLEMENTATION_PLAN.md (timeline).

---

## 1. Product Vision

LEGACYX is a **legacy application modernization and behavioral validation platform**.

It helps engineering organizations answer three questions that generic AI tools cannot reliably answer:

1. **What exactly does this legacy system do?** (Evidence-backed, not hallucinated.)
2. **What is the safest modernization path?** (Explainable, not scored.)
3. **Did the modernization preserve behavior?** (Verified, not assumed.)

The platform follows the workflow:

```
DISCOVER → UNDERSTAND → DECIDE → CHANGE → VERIFY
```

LEGACYX is not a chatbot. It is an engineering platform.

---

## 2. Core Design Principles

| Principle | Manifestation |
|---|---|
| Evidence over assertion | Every claim links to source evidence or execution evidence |
| Determinism over AI inference | Static analysis establishes facts; AI reasons over them |
| Human control over automation | Approval gates at every impactful step |
| Explainability over metrics | Human-readable reasoning instead of numerical scores |
| Immutability of source | Original code never modified; generated code always isolated |
| Auditability | Complete immutable record of all platform actions |

---

## 3. Information Architecture

### 3.1 Workspace → Projects

The top-level organizational unit is a **Workspace**, which contains one or more **Projects**.
A Project corresponds to one legacy system (one repository).

### 3.2 Project Navigation

```
Project
├── Overview              — Summary, status, key metrics
├── System X-Ray          — Interactive architecture visualization
├── Business Logic        — Recovered business rules with evidence
├── Change Impact         — Blast radius explorer for any component
├── Modernization Plan    — Strategy recommendations, rationale
├── Migration             — Step-by-step migration with approval workflow
├── Validation            — Build, test, and behavioral validation results
└── Audit Trail           — Immutable history of all platform actions
```

### 3.3 Page Purposes

#### Overview
- Project status (ingestion status, analysis status, migration status, validation status)
- Key counts: files, classes, APIs, business rules, migration steps
- No decorative charts; only actionable status information

#### System X-Ray
- Interactive dependency graph (React Flow)
- File tree with metadata
- Class and method browser
- Call relationship visualization
- API endpoint table
- Database interaction table
- Click any node to see: dependencies, dependents, related business rules, related APIs

#### Business Logic
- List of identified business-rule candidates
- Each rule shows: human-readable summary, source file, line range, related classes/methods, workflow context, AI explanation (clearly labelled)
- Source evidence is mandatory — rules without source references are not shown

#### Change Impact
- Input: select any component (class, method, API, database table)
- Output: direct dependencies, transitive dependents, affected workflows, potentially affected tests
- Visual graph of impact radius
- Export impact report

#### Modernization Plan
- Per-component strategy recommendations: Refactor / Replatform / Extract / Replace / Retain
- Each recommendation includes: rationale (human-readable), supporting evidence, estimated complexity
- No "AI confidence scores" — recommendations are labelled as AI-assisted and require human review
- Group by: domain, complexity, risk

#### Migration
- Ordered list of migration steps with explicit states
- Per-step view: objective, affected components, prerequisites, expected changes, validation requirements, approval status
- Approval workflow: PROPOSED → REVIEW → APPROVED → EXECUTING → VALIDATING → VERIFIED / FAILED
- Execution log visible per step
- Validation evidence visible per step

#### Validation
- Per validation run: build result, test result, behavioral comparison result
- Behavioral results: scenario name, legacy output, modern output, match/mismatch, diff view
- AI explanation for mismatches (clearly labelled as AI-generated)
- Execution logs (actual, untruncated where feasible)

#### Audit Trail
- Chronological list of all platform events for this project
- Filters: actor, event type, date range
- Immutable — no editing or deletion

---

## 4. Features

### 4.1 Repository Ingestion (Phase 2)

**Inputs:**
- ZIP upload containing repository
- Git repository URL (future)

**Outputs:**
- Ingested repository stored in object storage
- Repository metadata: detected language, framework, build tool, file count
- Repository status: `PENDING | INGESTING | READY | FAILED`

**Rules:**
- ZIP extraction must prevent path traversal
- Repository source is immutable after ingestion
- Technology detection is deterministic (not AI)

---

### 4.2 System X-Ray (Phase 3)

Deterministic static analysis of the repository producing:

| Entity | What is captured |
|---|---|
| Files | Path, size, language, module |
| Classes | Name, package, file, line range, type (class/interface/enum/annotation) |
| Methods | Name, class, signature, line range, visibility, annotations |
| Imports | Source class, imported class/package |
| Dependencies | Source class, target class, dependency type (extends/implements/uses) |
| Call edges | Caller method, callee method, call site line |
| API endpoints | HTTP method, path, handler class, handler method |
| Database tables | Table name, referenced by class/method, operation type (SELECT/INSERT/UPDATE/DELETE) |
| Database operations | Operation type, entity/table, method containing query |

**Outputs used in:**
- System X-Ray visualization
- Business Logic Recovery
- Change Impact Explorer
- Modernization Strategy Engine

---

### 4.3 Business Logic Recovery (Phase 4)

**Purpose:** Identify code regions that likely encode business rules, and surface them with evidence.

**Business Rule Candidate definition:**
A code region is a business rule candidate if it contains logic that:
- Enforces constraints (e.g., validation, eligibility rules)
- Makes decisions with domain-specific conditions
- Applies transformations with domain-specific meaning (e.g., fee calculation, discount application)
- Defines domain-specific thresholds or constants

**Each recovered rule must include:**
- Human-readable name
- Source file path
- Line range (start → end)
- Related class(es)
- Related method(s)
- Related workflow (if identifiable)
- AI explanation (labelled as AI-generated, linked to the source evidence)
- Confidence classification (HIGH / MEDIUM / LOW) — based on heuristics, not AI scoring

---

### 4.4 Change Impact Explorer (Phase 5)

Given any component, the system computes:

```
Component
  ├── direct dependencies (components this component calls/uses)
  ├── dependents (components that call/use this component)
  ├── transitive dependents (full blast radius)
  ├── affected API endpoints
  ├── affected business rules
  └── potentially affected tests
```

Output: interactive graph + tabular detail + exportable report.

---

### 4.5 Modernization Strategy Engine (Phase 6)

**Strategies:**

| Strategy | Meaning |
|---|---|
| Refactor | Improve code structure within same technology |
| Replatform | Move to modern equivalent with minimal code change |
| Extract | Extract to a separate service / module |
| Replace | Replace functionality with a new implementation |
| Retain | Keep as-is temporarily; defer modernization |

**Recommendation includes:**
- Recommended strategy
- Human-readable rationale
- Supporting evidence (dependencies, complexity, business criticality)
- Dependencies that must be resolved first
- Risk level (Low / Medium / High)

**Rules:**
- No arbitrary numerical scores determine strategy
- Strategy is labelled as AI-recommended; human must review
- Human can override the recommendation with a recorded reason

---

### 4.6 Migration Planner (Phase 7)

**Generates an ordered migration plan:**

Each step contains:
- Step number
- Objective
- Affected components
- Prerequisites (other steps that must complete first)
- Expected changes (what will be generated or modified)
- Validation requirements (what must pass before this step is verified)
- Current approval state

**State machine:** See ARCHITECTURE.md §10.

**Rules:**
- Plan cannot be executed without passing through REVIEW and APPROVED states
- No step may execute if a prerequisite step is FAILED or not VERIFIED

---

### 4.7 AI-Assisted Transformation (Phase 8)

**Generates candidate modernized code without overwriting the original source.**

- Original source is read-only
- Generated code stored in isolated artifact storage
- Generated code labelled as "candidate" until validated
- Transformation linked to the migration step that produced it
- Transformation linked to the analysis facts that informed it

**AI operations available:**
- `transform_code(source_fragment, target_spec)` → candidate code
- `generate_tests(component_fact)` → test suite candidate

---

### 4.8 Behavioral Validation (Phase 9)

**The core differentiating feature.**

Same scenario is executed against both the legacy system and the modern system.
Outputs are captured and compared.

```
Test Scenario
      │
      ├── Legacy System Execution ──▶ Legacy Output
      │
      └── Modern System Execution ──▶ Modern Output
                                             │
                              ┌──────────────▼────────────────┐
                              │        Output Comparator       │
                              └──────────────┬────────────────┘
                                             │
                              ┌──────────────▼────────────────┐
                              │   MATCH / MISMATCH + Evidence  │
                              └──────────────┬────────────────┘
                                             │
                              ┌──────────────▼────────────────┐
                              │  AI Explanation (if mismatch)  │
                              └───────────────────────────────┘
```

**Validation evidence includes:**
- Build logs (legacy and modern)
- Test execution logs
- Output diff (actual values, not descriptions)
- Execution environment metadata (timestamp, version)

**Rules:**
- A step cannot be VERIFIED without behavioral validation evidence
- Validation failures halt automatic progression
- Output diffs must be stored and displayed — never suppressed

---

### 4.9 Migration Governance & Audit (Phase 10)

**Governance:**
- Approval gates at each state transition
- Rollback capability for FAILED steps
- Migration checkpoint snapshots

**Audit:**

Every platform action produces an immutable audit event:

| Field | Description |
|---|---|
| `id` | Unique event ID |
| `project_id` | Project |
| `actor_id` | User who triggered the action (or SYSTEM) |
| `actor_type` | USER / SYSTEM |
| `event_type` | Enum of all auditable event types |
| `target_type` | What the action was performed on |
| `target_id` | ID of the target |
| `metadata` | JSON — relevant context (step ID, validation ID, etc.) |
| `timestamp` | ISO8601, immutable |

**Auditable event types:**
```
repository.uploaded
analysis.started
analysis.completed
analysis.failed
component.selected
migration.plan.created
migration.step.proposed
migration.step.reviewed
migration.step.approved
migration.step.rejected
migration.step.executing
migration.step.verified
migration.step.failed
validation.started
validation.completed
validation.mismatch_detected
validation.failed
approval.granted
approval.rejected
```

---

## 5. Demonstration Target: LegacyBank

**LegacyBank** is a fictional but realistic Java/Spring legacy application used to demonstrate all LEGACYX capabilities.

### Domain Overview

| Domain | Entities |
|---|---|
| Customer | Customer, Address, ContactInfo |
| Account | Account, AccountBalance |
| Order | Order, OrderLine |
| Payment | Payment, PaymentMethod |
| Invoice | Invoice, InvoiceLine |
| Discount | DiscountPolicy, DiscountApplication |
| Transaction | Transaction, TransactionHistory |
| Notification | Notification, NotificationTemplate |

### Intentional Legacy Characteristics

These must be present to make the demonstration realistic:

- Tightly coupled services (CustomerService calls AccountService directly, not via interface)
- Business logic mixed with persistence logic (calculations inside DAO/repository classes)
- Duplicated validation logic (same validation in multiple service methods)
- Outdated REST patterns (non-REST URLs, inconsistent HTTP status usage)
- Hidden business rules (fee calculation inside a utility class with no documentation)
- Magic numbers and undocumented constants
- God classes (OrderService with 1000+ lines)
- Minimal test coverage (< 30% line coverage)
- Direct JDBC alongside JPA (inconsistent data access patterns)
- No defined domain model (anemic model — all logic in services)

### Build

- Maven-based
- Spring Boot 2.x (intentionally outdated)
- JDK 11

**Note:** LegacyBank is not built during Phase 0. Document only.

---

## 6. Database Domain Model

> Full schema implementation is in Phase 1.
> The model below defines entities, fields, relationships, and lifecycle.

---

### 6.1 Core Entities

#### `users`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `email` | VARCHAR UNIQUE | Authentication identity |
| `display_name` | VARCHAR | |
| `created_at` | TIMESTAMPTZ | Immutable |
| `updated_at` | TIMESTAMPTZ | |

**Lifecycle:** Created on registration. Soft-delete only (set `deleted_at`).
**Relationships:** Has many projects.

---

#### `projects`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `owner_id` | UUID FK → users | |
| `name` | VARCHAR | Human-readable |
| `description` | TEXT | |
| `status` | ENUM | `CREATED, INGESTING, READY, ANALYZING, ANALYZED, FAILED` |
| `created_at` | TIMESTAMPTZ | Immutable |
| `updated_at` | TIMESTAMPTZ | |

**Lifecycle:** Created by user. Status transitions driven by ingestion and analysis events.
**Relationships:** Belongs to user. Has one repository. Has many analysis runs. Has one migration plan.

---

#### `repositories`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `project_id` | UUID FK → projects | UNIQUE (one per project) |
| `source_type` | ENUM | `ZIP, GIT` |
| `storage_path` | VARCHAR | Path in object storage |
| `detected_language` | VARCHAR | e.g. `java` |
| `detected_framework` | VARCHAR | e.g. `spring-boot` |
| `detected_build_tool` | VARCHAR | e.g. `maven` |
| `file_count` | INTEGER | |
| `ingested_at` | TIMESTAMPTZ | Immutable |
| `sha256` | VARCHAR | Integrity hash of archive |

**Lifecycle:** Created on upload/clone. Immutable after ingestion (never modified).
**Relationships:** Belongs to project.

---

#### `analysis_runs`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `project_id` | UUID FK → projects | |
| `repository_id` | UUID FK → repositories | |
| `status` | ENUM | `PENDING, RUNNING, COMPLETED, FAILED` |
| `started_at` | TIMESTAMPTZ | |
| `completed_at` | TIMESTAMPTZ | |
| `error_message` | TEXT | Null if successful |
| `file_count` | INTEGER | |
| `class_count` | INTEGER | |
| `method_count` | INTEGER | |

**Lifecycle:** Created when analysis is triggered. Immutable after completion (never updated — create a new run instead).
**Relationships:** Belongs to project and repository. Has many derived entities (files, classes, etc.).

---

### 6.2 Code Entity Entities

All code entities are associated with the analysis run that produced them.

#### `files`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `path` | VARCHAR | Relative path from repo root |
| `language` | VARCHAR | |
| `size_bytes` | INTEGER | |
| `line_count` | INTEGER | |
| `module` | VARCHAR | Maven module or top-level package |

**Lifecycle:** Immutable. Produced by analysis run. Never updated.

#### `classes`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `file_id` | UUID FK → files | |
| `fully_qualified_name` | VARCHAR | e.g. `com.legacybank.account.AccountService` |
| `simple_name` | VARCHAR | |
| `package_name` | VARCHAR | |
| `class_type` | ENUM | `CLASS, INTERFACE, ENUM, ANNOTATION` |
| `line_start` | INTEGER | |
| `line_end` | INTEGER | |
| `is_abstract` | BOOLEAN | |
| `annotations` | JSONB | Spring annotations, etc. |

**Lifecycle:** Immutable. Produced by analysis run.

#### `methods`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `class_id` | UUID FK → classes | |
| `name` | VARCHAR | |
| `signature` | VARCHAR | Full method signature |
| `return_type` | VARCHAR | |
| `visibility` | ENUM | `PUBLIC, PROTECTED, PRIVATE, PACKAGE` |
| `line_start` | INTEGER | |
| `line_end` | INTEGER | |
| `annotations` | JSONB | |
| `is_static` | BOOLEAN | |

**Lifecycle:** Immutable. Produced by analysis run.

---

### 6.3 Relationship Entities

#### `imports`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `source_file_id` | UUID FK → files | |
| `imported_name` | VARCHAR | Fully qualified import |
| `is_wildcard` | BOOLEAN | |

#### `dependencies`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `source_class_id` | UUID FK → classes | |
| `target_class_id` | UUID FK → classes | |
| `dependency_type` | ENUM | `EXTENDS, IMPLEMENTS, USES, INJECTS` |

#### `call_edges`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `caller_method_id` | UUID FK → methods | |
| `callee_class_name` | VARCHAR | May be external |
| `callee_method_name` | VARCHAR | |
| `call_site_line` | INTEGER | |
| `is_external` | BOOLEAN | True if callee not in repository |

---

### 6.4 API and Database Entities

#### `apis`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `http_method` | VARCHAR | GET, POST, PUT, DELETE, PATCH |
| `path_pattern` | VARCHAR | URL pattern |
| `handler_class_id` | UUID FK → classes | |
| `handler_method_id` | UUID FK → methods | |
| `annotations` | JSONB | Spring mapping annotations |

#### `database_tables`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `table_name` | VARCHAR | |
| `detection_method` | ENUM | `ANNOTATION, SQL_LITERAL, JPA_ENTITY, NAMED_QUERY` |

#### `database_operations`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `table_id` | UUID FK → database_tables | |
| `operation_type` | ENUM | `SELECT, INSERT, UPDATE, DELETE, DDL` |
| `method_id` | UUID FK → methods | |
| `query_fragment` | TEXT | Extracted SQL/HQL fragment (sanitized) |

---

### 6.5 Business Logic Entities

#### `business_rules`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `name` | VARCHAR | Human-readable |
| `description` | TEXT | AI-generated, labelled |
| `source_file_id` | UUID FK → files | |
| `line_start` | INTEGER | |
| `line_end` | INTEGER | |
| `primary_class_id` | UUID FK → classes | |
| `primary_method_id` | UUID FK → methods | Nullable |
| `confidence` | ENUM | `HIGH, MEDIUM, LOW` |
| `rule_type` | VARCHAR | e.g. `VALIDATION, CALCULATION, ELIGIBILITY` |

**Lifecycle:** Immutable. Produced by analysis run.

#### `workflows`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `name` | VARCHAR | |
| `description` | TEXT | AI-generated, labelled |
| `entry_api_id` | UUID FK → apis | Nullable |

#### `workflow_components`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `workflow_id` | UUID FK → workflows | |
| `class_id` | UUID FK → classes | |
| `role` | VARCHAR | e.g. `ENTRY, ORCHESTRATOR, VALIDATOR, REPOSITORY` |

---

### 6.6 Modernization Entities

#### `modernization_recommendations`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `analysis_run_id` | UUID FK | |
| `target_class_id` | UUID FK → classes | |
| `strategy` | ENUM | `REFACTOR, REPLATFORM, EXTRACT, REPLACE, RETAIN` |
| `rationale` | TEXT | AI-generated, labelled |
| `risk_level` | ENUM | `LOW, MEDIUM, HIGH` |
| `complexity` | ENUM | `LOW, MEDIUM, HIGH` |
| `reviewed_by` | UUID FK → users | Nullable — set when human reviews |
| `override_strategy` | ENUM | Nullable — human override |
| `override_rationale` | TEXT | Nullable |

---

### 6.7 Migration Entities

#### `migration_plans`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `project_id` | UUID FK → projects | UNIQUE |
| `analysis_run_id` | UUID FK | |
| `created_at` | TIMESTAMPTZ | Immutable |
| `status` | ENUM | `DRAFT, ACTIVE, COMPLETED, ARCHIVED` |

#### `migration_steps`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `plan_id` | UUID FK → migration_plans | |
| `step_number` | INTEGER | Ordered |
| `title` | VARCHAR | |
| `objective` | TEXT | |
| `state` | ENUM | `PROPOSED, REVIEW, APPROVED, EXECUTING, VALIDATING, VERIFIED, FAILED` |
| `affected_class_ids` | UUID[] | PostgreSQL array |
| `prerequisite_step_ids` | UUID[] | Steps that must be VERIFIED first |
| `expected_changes` | JSONB | |
| `validation_requirements` | JSONB | |
| `approved_by` | UUID FK → users | Nullable |
| `approved_at` | TIMESTAMPTZ | Nullable |
| `execution_log` | TEXT | Populated during execution |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

---

### 6.8 Validation Entities

#### `validation_runs`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `project_id` | UUID FK → projects | |
| `migration_step_id` | UUID FK → migration_steps | Nullable |
| `status` | ENUM | `PENDING, RUNNING, COMPLETED, FAILED` |
| `build_passed` | BOOLEAN | Nullable until run |
| `tests_passed` | BOOLEAN | Nullable until run |
| `behavioral_passed` | BOOLEAN | Nullable until run |
| `started_at` | TIMESTAMPTZ | |
| `completed_at` | TIMESTAMPTZ | |

#### `behavioral_tests`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `validation_run_id` | UUID FK | |
| `scenario_name` | VARCHAR | |
| `scenario_description` | TEXT | |
| `input_payload` | JSONB | |

#### `behavioral_results`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `behavioral_test_id` | UUID FK | |
| `legacy_output` | JSONB / TEXT | |
| `modern_output` | JSONB / TEXT | |
| `matched` | BOOLEAN | |
| `diff_details` | JSONB | Field-level diff |
| `legacy_build_log` | TEXT | |
| `modern_build_log` | TEXT | |
| `ai_explanation` | TEXT | Nullable — AI-generated, labelled |
| `executed_at` | TIMESTAMPTZ | |

---

### 6.9 Governance Entities

#### `approval_actions`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `migration_step_id` | UUID FK | |
| `actor_id` | UUID FK → users | |
| `action` | ENUM | `APPROVE, REJECT` |
| `comment` | TEXT | Optional |
| `timestamp` | TIMESTAMPTZ | Immutable |

#### `audit_events`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `project_id` | UUID FK → projects | |
| `actor_id` | UUID FK → users | Nullable (SYSTEM events) |
| `actor_type` | ENUM | `USER, SYSTEM` |
| `event_type` | VARCHAR | Enum of auditable events |
| `target_type` | VARCHAR | |
| `target_id` | UUID | Nullable |
| `metadata` | JSONB | |
| `timestamp` | TIMESTAMPTZ | Immutable |

**Lifecycle:** Strictly immutable. No update or delete operations allowed on this table.

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Analysis of a 50k LOC Java repository | < 10 minutes |
| API response for pre-computed results | < 500ms |
| Audit trail append | Always durable, never lossy |
| Original source | Immutable after ingestion |
| Validation results | Immutable after recording |
| UI real-time updates | WebSocket progress events |
| Authentication | JWT, stateless |
| Authorization | Project-scoped |
| Code execution | Eventually sandboxed |

---

*Last updated: Phase 0 — Architecture Contract*
