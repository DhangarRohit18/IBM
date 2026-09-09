# docs/decisions/README.md — Architecture Decision Records Index

This directory contains Architecture Decision Records (ADRs) for LEGACYX.

ADRs document significant architectural decisions: the context, the options considered, the decision made, and the consequences.

ADRs are immutable after acceptance. If a decision is superseded, a new ADR is created and the old one is marked as superseded.

---

## ADR Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](./ADR-001-deterministic-analysis-over-ai-only.md) | Deterministic Analysis + AI Reasoning Rather Than AI-Only Analysis | Accepted |
| [ADR-002](./ADR-002-java-spring-initial-ecosystem.md) | Java/Spring as the Initial Supported Ecosystem | Accepted |
| [ADR-003](./ADR-003-original-source-immutable.md) | Original Source is Immutable During Migration | Accepted |
| [ADR-004](./ADR-004-behavioral-validation-first-class.md) | Behavioral Validation as a First-Class Feature | Accepted |
| [ADR-005](./ADR-005-ai-gateway-abstraction.md) | AI Providers Abstracted Behind an AI Gateway | Accepted |
| [ADR-006](./ADR-006-background-jobs-for-long-running-ops.md) | Long-Running Operations Use Background Jobs | Accepted |

---

## ADR Format

Each ADR uses the following structure:

```markdown
# ADR-NNN — Title

**Status:** Proposed | Accepted | Superseded by ADR-NNN | Deprecated
**Date:** Phase N
**Deciders:** ...

## Context
## Decision
## Rationale
## Consequences
```

---

*Last updated: Phase 0*
