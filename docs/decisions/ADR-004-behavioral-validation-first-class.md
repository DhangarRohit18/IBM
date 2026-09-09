# ADR-004 — Behavioral Validation as a First-Class Feature

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

Most AI code modernization tools produce output (new code) and consider the task complete. Some additionally run unit tests. The question of whether the modernized system behaves identically to the legacy system is often left to the development team to answer independently.

Two approaches:

**Option A — Code generation + optional unit tests:**  
Generate the code. Run unit tests if they exist. Report pass/fail. Consider migration complete.

**Option B — Behavioral validation as a first-class feature:**  
Execute the same scenarios against both the legacy system and the modern candidate. Capture outputs. Compare field by field. Detect mismatches. Surface evidence. Do not mark a migration step as verified without behavioral evidence.

---

## Decision

LEGACYX implements **Option B — Behavioral Validation as a first-class feature.**

Behavioral validation is not a phase 12 afterthought. It is defined in the architecture from Phase 0 and implemented in Phase 9 as a core product differentiator.

---

## Rationale

### 1. Build Success ≠ Test Success ≠ Behavioral Equivalence

These three outcomes are distinct:
- **Build success**: the code compiles. This says nothing about runtime behavior.
- **Test success**: existing unit tests pass. If the legacy system has < 30% test coverage (as LegacyBank intentionally does), the remaining 70% of behavior is unverified.
- **Behavioral equivalence**: the same input produces the same output in both systems under the same conditions.

A modernization that achieves build success and test success but fails behavioral equivalence has not successfully modernized the system.

### 2. It Is the Core Safety Guarantee

Organizations cannot replace a legacy system with a modern candidate unless they can demonstrate, with evidence, that behavior is preserved for their critical workflows. This is what LEGACYX provides that generic AI code generators do not.

### 3. It Differentiates LEGACYX in the Market

The ability to show an actual output comparison — "legacy produced X, modern produced Y, they match / do not match" — is a credible, verifiable claim. "AI generated new code" is not.

### 4. Mismatches Are Informative

Behavioral mismatches reveal hidden coupling, undocumented legacy behavior, and implicit contracts that the static analysis and AI could not detect. They are not failures of the platform — they are the platform working correctly. Surfacing them is the entire point.

---

## Consequences

- The validation engine (Phase 9) must support: scenario generation, isolated legacy and modern execution, output capture, field-level comparison, mismatch evidence, and AI explanation of mismatches.
- The migration state machine must include a `VALIDATING` state that cannot be bypassed.
- A `VERIFIED` state requires documented behavioral validation evidence (stored in `behavioral_results`).
- The UI must display actual output diffs, not summaries.
- Code execution must eventually occur in isolated environments (containers) to prevent interference and enable reproducibility.
