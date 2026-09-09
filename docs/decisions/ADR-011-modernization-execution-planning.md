# ADR-011 — Deterministic Modernization Execution Plan Generation

**Status:** Accepted  
**Date:** Phase 7  
**Deciders:** Project Lead  

---

## Context

Phase 6 produces evidence-backed modernization strategy recommendations (e.g. `MODULARIZE`, `EXTRACT_SERVICE`, `STRANGLER`, `REFACTOR_IN_PLACE`).  
LEGACYX now requires bridging these recommendations to an **actionable, traceable modernization execution plan** for candidate components (e.g. `AccountService.processTransfer()`).

Two design options were considered:

**Option A — AI-Generated Step Plan:**  
Prompt an LLM with code or component names and ask it to invent refactoring steps, estimated effort hours, and confidence scores.

**Option B — Deterministic Multi-Phase Reasoning + Task Taxonomy + Business Rule Preservation Mapping + AI Gateway Explanation (Chosen):**  
Consume Phase 3 System X-Ray entities & relationships, AST-observed responsibilities (Phase 6), Phase 4 Business Rules, Phase 5 Impact Surface, and Phase 6 Strategy choices. Use a deterministic rule engine to generate a topological sequence of modernization tasks, assign explicit task types from a controlled taxonomy, map business rules to preserve, link verification checkpoints, and compute caller migration tasks. AI is strictly restricted to explaining established plan facts in plain language.

---

## Decision

LEGACYX adopts **Option B — Deterministic Multi-Phase Reasoning + Task Taxonomy + Business Rule Preservation Mapping + AI Gateway Explanation.**

### Key Rules
1. **Deterministic Plan Generation**:
   Execution tasks, dependencies, preservation constraints, and verification checkpoints must be derived 100% from static analysis facts, AST responsibility signals, extracted business rules, and graph impact boundaries.

2. **Controlled Task Taxonomy**:
   - `EXTRACT_RESPONSIBILITY`: Isolate AST responsibility signals into dedicated domain components.
   - `SEPARATE_BUSINESS_RULE`: Decouple extracted Phase 4 business rules (validation, threshold, calculation).
   - `EXTRACT_CALCULATION`: Isolate financial derivations and mathematical formulas.
   - `ISOLATE_PERSISTENCE`: Isolate database mutations and entity manager operations.
   - `ISOLATE_STATE_TRANSITION`: Isolate domain lifecycle transitions (e.g. `PENDING` -> `COMPLETED`).
   - `ISOLATE_EXTERNAL_NOTIFICATION`: Isolate asynchronous event publishing or notification dispatch.
   - `DEFINE_INTERFACE`: Define clean contract interfaces for extracted modules.
   - `INTRODUCE_ADAPTER`: Provide protocol or interface mapping between legacy and modern.
   - `INTRODUCE_FACADE`: Wrap legacy component to preserve caller compatibility.
   - `REDUCE_DEPENDENCY`: Decouple unnecessary direct dependencies.
   - `SPLIT_COMPONENT`: Decompose class into modular domain helpers.
   - `MIGRATE_CALLER`: Update direct dependents identified in Phase 5 impact analysis.
   - `PRESERVE_BEHAVIOR`: Enforce explicit invariant preservation for rules.
   - `ADD_VERIFICATION_CHECKPOINT`: Attach verifiable assertion criteria to major refactoring milestones.

3. **Dependency-Aware Acyclic Ordering**:
   Tasks must form a deterministic Directed Acyclic Graph (DAG) topologically sorted into an execution sequence. Isolation tasks precede interface definition tasks, which precede caller updates and verification checkpoints.

4. **Preservation of Business Logic**:
   Every plan explicitly compiles a `rules_to_preserve` catalog linking each rule ID, condition/formula, line evidence, and affected task ID(s). No step may alter established business rules.

5. **Zero Fake Scores**:
   No fake percentage progress, no arbitrary LLM risk/effort numbers. Metrics reflect observable facts: task count, preserved rule count, direct/transitive dependent count, and verification checkpoint count.

6. **Auditable Human Controls**:
   Human architects review, approve, reject, reorder, or update task statuses (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `DEFERRED`). Source code is NEVER automatically modified in Phase 7.

---

## Consequences

- Implemented via `ModernizationPlanGenerator` engine in `backend/app/modernization/plan_generator.py`.
- Persistence managed via `ModernizationPlan` and `ModernizationTask` SQLAlchemy models in `backend/app/models/modernization_plan.py`.
- Migration managed via `backend/alembic/versions/006_modernization_execution_plan.py`.
- REST APIs exposed under `/api/v1/analysis/{analysis_id}/modernization/plans`.
- Frontend workspace tab **Modernization Plan** integrated in `frontend/src/features/modernization/ModernizationPlanPage.tsx`.
