# ADR-003 — Original Source is Immutable During Migration

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

When LEGACYX generates modernized code or assists with transformation, the generated code must be stored somewhere. Two options exist:

**Option A — In-place modification:**  
Write the generated code directly to the repository source tree, overwriting the original file.

**Option B — Isolated artifact storage:**  
Store the generated code as a separate artifact, completely isolated from the original source. The original source is never modified.

---

## Decision

LEGACYX adopts **Option B — Isolated artifact storage**. The original repository source is immutable after ingestion. Generated code is always stored in separate, isolated artifact storage.

---

## Rationale

### 1. Irreversibility

In-place modification is destructive. If AI-generated code is incorrect, the original may be overwritten and difficult to recover. Source control can help, but the platform should not depend on users having a functioning recovery process.

### 2. Generated Code is a Candidate, Not a Verified Replacement

Generated code must pass validation (build, tests, behavioral equivalence) before it can be considered a replacement. Overwriting the source before validation conflates "AI generated some code" with "the code is correct." These are fundamentally different states.

### 3. Human Review Requires the Original and the Candidate Simultaneously

To meaningfully review a transformation, a human must see the original code and the candidate code side by side. This is only possible if both exist independently.

### 4. Auditability

If the original source can be modified, the audit trail becomes harder to reconstruct. Keeping the original immutable means the analysis is always consistent with what was actually ingested, and the migration artifacts can be compared against the known baseline.

### 5. Safety for Sensitive Production Systems

Legacy systems being modernized are often active production systems. Automated modification of source code without human review is unacceptable in regulated industries.

---

## Consequences

- Object storage must support two distinct namespaces: `repositories/` (immutable) and `artifacts/` (generated, mutable within its lifecycle).
- The UI must clearly distinguish between "original source" and "generated candidate."
- A migration step that generates code must not advance to VERIFIED without explicit human review of the candidate.
- The analysis engine reads from the immutable `repositories/` namespace only.
