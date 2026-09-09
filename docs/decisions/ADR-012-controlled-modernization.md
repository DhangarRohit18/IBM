# ADR-012 — Controlled Modernization & Code Transformation Architecture

**Status:** Proposed  
**Date:** Phase 8 Planning  
**Deciders:** Project Lead  

---

## Context

Phase 7 (Modernization Execution Planning) produces approved, topologically ordered task DAGs (`ModernizationPlan` and `ModernizationTask`) backed by static analysis evidence (Phase 3), business rules (Phase 4), impact surface analysis (Phase 5), and strategy recommendations (Phase 6).

LEGACYX now requires an architectural blueprint for **Phase 8 — Controlled Modernization & Code Transformation**, which transforms approved Phase 7 tasks into concrete, modernized target code artifacts (e.g. decomposing `AccountService.processTransfer()` into `TransferDomainService`, `AccountServiceFacade`, and `AccountController` caller updates).

Two design options were considered:

**Option A — Uncontrolled Autonomous AI Code Rewriting:**  
Pass the legacy repository to an LLM agent with open write permissions to rewrite source files directly in-place, relying on AI self-verification and auto-committing changes without human review or isolated artifact storage.

**Option B — Controlled Evidence-Grounded Transformation Pipeline with Storage Isolation, Human-in-the-Loop Review, and Immutable Source Guards (Chosen):**  
Consume approved Phase 7 execution plans and tasks. Generate modernized target code artifacts deterministically or via AI candidate proposals grounded strictly in established Phase 4 rules and Phase 5 impact boundaries. Store all generated code artifacts in isolated, project-scoped storage (`storage/modernized/{project_id}/{plan_id}/`), completely separate from the immutable legacy source. Require explicit human architect review (`PROPOSED` → `REVIEWED` → `APPROVED` → `APPLIED` / `REJECTED`) before any transformation candidate can be accepted.

---

## Decision

LEGACYX adopts **Option B — Controlled Evidence-Grounded Transformation Pipeline with Storage Isolation, Human-in-the-Loop Review, and Immutable Source Guards.**

### Key Rules & Constraints

1. **Original Source Immutability (AGENTS.md §4.1)**:
   The original legacy repository files are strictly immutable. Generated modern code artifacts are stored in isolated, access-controlled storage (`storage/modernized/{project_id}/{plan_id}/`). Original files are NEVER overwritten or mutated.

2. **Grounding in Deterministic Evidence (AGENTS.md §2.1, §2.2)**:
   Code transformations must consume established facts:
   - Approved Phase 7 `ModernizationPlan` & `ModernizationTask`
   - Phase 4 `BusinessRule` conditions, thresholds, and formulas
   - Phase 5 `ImpactSurface` caller dependencies
   - Phase 3 `CodeEntity` AST signatures
   AI is prohibited from inventing business rules, class names, or dependencies not found in the static analysis evidence.

3. **Strict AI Boundary (AGENTS.md §3.1, §3.2)**:
   AI calls must occur exclusively through the central AI Gateway (`app/ai/gateway.py`). AI acts as a candidate proposal generator for code transformation snippets based on deterministic context. AI outputs are NEVER automatically marked as verified, approved, or applied.

4. **Explicit 4-State Transformation Machine (AGENTS.md §4.2)**:
   Every transformation proposal enforces a strict state machine:
   `PROPOSED` → `REVIEWED` → `APPROVED` → `APPLIED` (or `REJECTED`).
   Artifacts cannot skip states. Only human architects can move proposals to `APPROVED` or `APPLIED`.

5. **Full Traceability (AGENTS.md §2.3, §4.6)**:
   Every generated artifact records:
   - `plan_id` & `task_id`
   - `strategy_id` & `analysis_id`
   - Source file path & line range
   - Mapped `rule_ids` preserved
   - Created artifact category (`EXTRACTED_CLASS`, `EXTRACTED_INTERFACE`, `FACADE`, `ADAPTER`, `REFACTORED_METHOD`, `MIGRATED_CALLER`, `SUPPORTING_TEST_STUB`)
   - Human review metadata & audit timestamps

6. **Zero Fake Metrics (AGENTS.md §5.2)**:
   No fake confidence scores, no arbitrary refactoring risk percentages, and no unverified claims of behavioral equivalence.

7. **Phase 9 Verification & Phase 11 Deployment Boundaries**:
   Phase 8 strictly produces and manages transformation code proposals. Code execution, unit test execution, and behavioral equivalence testing belong strictly to Phase 9. Production deployment belongs to Phase 11.

---

## Consequences

### Positive
- Guarantee of zero risk to original customer codebase through strict storage isolation.
- Full compliance with LEGACYX engineering rules (`AGENTS.md`) and architectural contracts.
- High transparency with side-by-side diff viewers, preserved rule checklists, and auditable human approval logs.

### Negative / Trade-offs
- Requires human architect review step before code artifacts are marked `APPROVED`/`APPLIED`.
- Storage footprint increases due to isolated modernized artifact directory structure.
