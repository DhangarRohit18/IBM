# ADR-013 — Deterministic Build, Unit Test & Behavioral Equivalence Validation

**Status:** Proposed  
**Date:** Phase 9 Planning  
**Deciders:** Project Lead  

---

## Context

Phases 7 and 8 produce approved modernization plans and generated target code artifacts (e.g. `TransferDomainService.java`, `AccountServiceFacade.java`, `AccountController.java`, `TransferDomainServiceTest.java`) stored in isolated workspaces (`storage/modernized/{project_id}/{plan_id}/`).

LEGACYX now requires an architectural blueprint for **Phase 9 — Build, Unit Test & Behavioral Equivalence Validation** to verify whether generated modernization candidates compile, pass unit tests, and preserve the observable behavior of original legacy components.

Two design options were considered:

**Option A — LLM-Based Code Assessment & Arbitrary Scoring:**  
Prompt an LLM to review the generated code and legacy source and output a fabricated "94% behavioral equivalence score" or "AI Pass/Fail verdict" without compiling or executing code.

**Option B — Executable Evidence Pipeline with Isolated Subprocess Workspaces, Deterministic Scenario Evaluators, and Honest Environment Reporting (Chosen):**  
Execute a multi-stage validation pipeline inside isolated temporary execution workspaces:
1. Detect JDK/build environment availability. Report `ENVIRONMENT_UNAVAILABLE` honestly if `javac` or build tools are absent.
2. Compile modernization target artifacts using isolated subprocess execution.
3. Execute unit tests inside the isolated workspace, capturing exact stdout, stderr, exit code, duration, and test counts.
4. Execute deterministic behavioral test scenarios derived directly from authoritative Phase 4 `BusinessRule` records. Compare legacy observable outputs vs modernized outputs to classify each scenario as `MATCH`, `MISMATCH`, or `UNABLE_TO_VALIDATE`.
5. Require explicit human review of established evidence. AI is strictly restricted to explaining established evidence in plain language.

---

## Decision

LEGACYX adopts **Option B — Executable Evidence Pipeline with Isolated Subprocess Workspaces, Deterministic Scenario Evaluators, and Honest Environment Reporting.**

### Key Rules & Constraints

1. **Original Source Immutability (AGENTS.md §4.1)**:
   Original legacy repository source files (`storage/extracted/`) are strictly read-only and immutable. Validation operates exclusively on isolated temporary workspaces.

2. **Prerequisite Approval Gate (AGENTS.md §4.2)**:
   Validation runs can only be triggered for `APPROVED` or `APPLIED` Phase 8 transformation proposals. Unapproved or rejected proposals cannot enter validation.

3. **Zero Fake Metrics & Zero AI-Invented Evidence (AGENTS.md §2.2, §5.2)**:
   No fake confidence scores, no arbitrary similarity percentages, and no LLM-invented test results. Every pass/fail status must originate from subprocess execution evidence.

4. **Honest Environment Reporting**:
   If system compilation tools (`javac`) are absent, return `ENVIRONMENT_UNAVAILABLE` cleanly without erroring out or fabricating build results.

5. **AI Boundary (AGENTS.md §3.1, §3.2)**:
   AI operates strictly through `AIGateway.generate_validation_explanation()` to explain established evidence facts. AI cannot determine test outcomes or approve validation runs.

6. **Deterministic Behavioral Comparison**:
   Scenarios reference original Phase 4 `BusinessRule` IDs. Observable outputs (return values, state transitions, exception types, fees) are compared deterministically.

7. **Phase 10+ Non-Goals**:
   Production deployment, automatic source replacement, CI/CD merges, and infrastructure provisioning belong strictly to later phases.

---

## Consequences

### Positive
- Guarantees 100% empirical evidence for all build, test, and behavioral claims.
- Zero risk to customer codebases through isolated sandbox execution.
- High transparency through expandable execution logs, stdout/stderr streams, and scenario comparison tables.

### Negative / Trade-offs
- Subprocess build execution requires JDK availability (`javac`) on the host system to produce active compilation binaries; falls back to `ENVIRONMENT_UNAVAILABLE` when uninstalled.
