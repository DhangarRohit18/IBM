# LEGACYX — Architecture: Business Logic Recovery (Phase 4)

## 1. Executive Summary

Business Logic Recovery is the Phase 4 engine of LEGACYX. It extracts explainable business decisions, validation rules, threshold checks, calculation formulas, actions, and state transitions encoded inside legacy Java applications.

---

## 2. Architecture & Layer Discipline

```
Java AST Representation (Phase 3 ASTs)
         │
         ▼
 ┌──────────────────────────────────────┐
 │  BusinessRuleExtractor               │ ── Pattern matcher & deduplicator
 └──────────────────────────────────────┘
         │
         ▼
 ┌──────────────────────────────────────┐
 │  BusinessRule Persistence Model      │ ── PostgreSQL DB (Facts + Evidence)
 └──────────────────────────────────────┘
         │
   ┌─────┴────────────────────────┐
   ▼                              ▼
FastAPI Business Rules API    AIGateway (Mock / watsonx)
(/api/v1/analysis/.../rules)  (Supplementary Explanations)
   │                              │
   └─────┬────────────────────────┘
         ▼
 ┌──────────────────────────────────────┐
 │  Business Logic Recovery Web UI      │ ── Inspector Drawer, Flow Trace, Source Viewer
 └──────────────────────────────────────┘
```

---

## 3. Mandatory Design Principles

1. **Deterministic Facts as Source of Truth**: All conditions, thresholds, calculations, and line numbers are extracted by AST parsing. AI never invents facts.
2. **Deterministic Deduplication**: Extracted statements belonging to the same control flow site are merged into unified rule candidates.
3. **Conservative State Inference**: Previous state in state transitions remains `UNKNOWN` unless proven by static analysis evidence.
4. **Action Promotion**: Method calls are promoted to ACTION rules only when associated with control flow, conditions, validations, or state changes.
5. **Strict AI Boundary**: AI explanations are supplementary, stored in `ai_explanation`, and requested on-demand. AI failure never invalidates deterministic facts.
6. **No Confidence Percentages**: Pure factual representation backed by line numbers and AST construct descriptions.

---

## 4. Controlled Taxonomy

- `VALIDATION`: Checks that guard operation execution (e.g. `balance < amount`).
- `CONDITIONAL`: Generic control-flow branch execution (`if` / `switch`).
- `THRESHOLD`: Variable comparison against literal (`50000`) or symbolic constant (`MAX_TRANSFER_LIMIT`).
- `CALCULATION`: Formula derivation or math assignment (`fee = amount * 0.02`).
- `ACTION`: Promoted operational side-effect invoked in control flow (`sendNotification()`).
- `STATE_TRANSITION`: Explicit state assignment (`account.setStatus(BLOCKED)`).

---

*Phase 4 Architecture Specification — LEGACYX*
