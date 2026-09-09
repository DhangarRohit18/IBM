# Modernization Strategy Architecture

The Modernization Strategy Engine in LEGACYX answers the critical question:
> **"Given what we have learned about this legacy system, what modernization approach is appropriate, and why?"**

---

## 1. Core Architecture

The engine composes findings across all prior phases:

```
┌─────────────────────────────────────────────────────────────┐
│                 SYSTEM X-RAY (PHASE 3)                      │
│   Entities, Methods, Fields, Packages, Imports, Annotations │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             BUSINESS LOGIC RECOVERY (PHASE 4)               │
│   Extracted Business Rules (Validation, Threshold, etc.)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 IMPACT ANALYSIS (PHASE 5)                   │
│   Direct & Transitive Dependents, Call Paths, Rule Linking  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             RESPONSIBILITY ANALYZER ENGINE (AST)            │
│   Input Validation, Business Rules, Calculations,           │
│   Service Coordination, Persistence, State, Notifications   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            DETERMINISTIC STRATEGY SELECTOR ENGINE           │
│   1. Apply Rules Matrix over Observable Metrics             │
│   2. Build Explicit Decision Trace                          │
│   3. Map Preserved Business Rules & Impact Surface          │
│   4. Generate Recommended + Alternative Strategies          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI GATEWAY NARRATIVE                    │
│   Translates established decision trace into plain text     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              HUMAN AUDIT & OVERRIDE WORKFLOW                │
│   Audited status: PROPOSED -> REVIEWED / OVERRIDDEN         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Observable Metrics (No Fake Scores)

Rather than inventing arbitrary percentage scores (*No "Modernization Score: 94%"*), LEGACYX uses observable metrics:

- `responsibility_count`: Number of distinct AST responsibility categories observed.
- `business_rule_count`: Count of extracted Phase 4 business rules within the component.
- `direct_dependent_count`: Number of immediate callers/dependents at depth=1.
- `transitive_dependent_count`: Number of indirect dependents at depth > 1.
- `impact_depth`: Maximum depth of ripple impact established by Phase 5 traversal.

---

## 3. Controlled Strategy Taxonomy & Decision Rules

1. `MODULARIZE`:
   - `responsibility_count >= 4` AND `direct_dependent_count <= 3`
2. `EXTRACT_SERVICE`:
   - `responsibility_count >= 3` AND `business_rule_count >= 3` AND `direct_dependent_count > 2` AND `transitive_dependent_count <= 5`
3. `STRANGLER`:
   - `responsibility_count >= 3` AND `transitive_dependent_count > 5` (high downstream ripple impact)
4. `REFACTOR_IN_PLACE`:
   - `responsibility_count <= 2` AND `business_rule_count <= 2` AND `direct_dependent_count <= 2`
5. `RETAIN_AND_WRAP`:
   - High stateful complexity OR low change frequency OR high extraction risk.
6. `NO_MODERNIZATION_NEEDED`:
   - `responsibility_count <= 1` AND `business_rule_count == 0` (e.g., simple DTO, Model, Enum, Utility).

---

## 4. Decision Trace & Preservation Structure

Every strategy record contains:
- **Observed Responsibilities**: Array of AST responsibility items with file paths, line ranges, and method signatures.
- **Business Rules to Preserve**: List of Phase 4 business rules that must be preserved during modernization.
- **Known Impact Surface**: Summary of Phase 5 direct & transitive dependents.
- **Decision Trace**:
  1. `Observed Fact`: Facts extracted from codebase.
  2. `Architectural Implication`: Structural consequence of observed facts.
  3. `Strategy Consideration`: Trade-off evaluation between candidate strategies.
  4. `Recommended Strategy`: Concluded strategy choice.
- **Auditable Human Override**: Recorded status, engineer identity, timestamp, and override rationale.
