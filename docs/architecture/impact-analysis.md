# Impact Analysis Architecture

The Impact Analysis engine in LEGACYX answers the critical question:
> **"If I change this legacy component or business rule, what other technical components and business rules could be affected, and why?"**

---

## 1. Core Principles

1. **100% Deterministic Traversal**: All impact paths are computed directly from Phase 3 static relationships (`CodeRelationship`) and Phase 4 `BusinessRule` records.
2. **Strict AI Boundary**: AI is strictly limited to explaining established impact paths (`POST /api/v1/impact/explain`). AI never invents or predicts unproven impacts.
3. **Bidirectional Traversal**:
   - **Forward Impact**: What does the target rely on/call/import?
   - **Reverse Impact**: What other components call, import, extend, or depend on the target?
4. **Bidirectional Business Rule Impact**:
   - **Component Target**: Identifies rules contained inside the component AND rules in dependent components.
   - **Business Rule Target**: Traces from rule to containing method/class, then executes forward/reverse component traversal.
5. **Direct vs. Transitive Classification**: Direct impact is established by immediate evidence at depth=1. Transitive impact is propagated beyond depth=1.
6. **Cycle Prevention & Depth Limits**: Uses explicit cycle detection (`visited` set) and bounded recursion depth (`max_depth`).
7. **Explicit Empty State**: Returns `NO EVIDENCED IMPACT` when no deterministic relationships exist within the traversal boundary.

---

## 2. Impact Analysis Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 SELECT TARGET & DIRECTION                   │
│   (Class / Method / Field / Package / Business Rule Target) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   IMPACT ANALYZER ENGINE                    │
│   1. Resolve Target Node in Phase 3 AST / Phase 4 Rules     │
│   2. Traverse CodeRelationship Graph (Forward / Reverse)    │
│   3. Link Associated Business Rules (Phase 4 Database)      │
│   4. Classify Direct (Immediate) vs Transitive Impact       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     IMPACT ANALYSIS RESULT                  │
│   - Target Info (ID, name, type, source evidence)           │
│   - Direct Affected Components & Rules                      │
│   - Transitive Affected Components & Rules                  │
│   - Evidenced Impact Paths (nodes + edge evidence)           │
│   - NO EVIDENCED IMPACT Flag (if empty)                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI GATEWAY EXPLANATION                   │
│   Translates established impact paths into business text    │
│   (Strictly reasoning over verified graph facts)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Schema & API Surface

- `GET /api/v1/analysis/{analysis_id}/impact`: Computes deterministic impact given `target_type`, `target_id`, `direction` (`forward` | `reverse`), and `max_depth`.
- `POST /api/v1/impact/explain`: Generates natural language impact summaries via `AIGateway` using established traversal paths only.
