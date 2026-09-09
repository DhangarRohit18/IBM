# ADR-010 — Deterministic Modernization Strategy Selection & Decision Tracing

**Status:** Accepted  
**Date:** Phase 6  
**Deciders:** Project Lead  

---

## Context

LEGACYX requires recommending modernization strategies (e.g. `MODULARIZE`, `EXTRACT_SERVICE`, `STRANGLER`, `REFACTOR_IN_PLACE`, `ADAPTER`, `ANTI_CORRUPTION_LAYER`, `RETAIN_AND_WRAP`, `NO_MODERNIZATION_NEEDED`) for legacy components.

Two design approaches were evaluated:

**Option A — AI-First Strategy Generator:**  
Pass repository code to an LLM and ask it to output modernization recommendations, confidence scores, and risk percentages.

**Option B — Deterministic Multi-Phase Reasoning + Decision Tracing + AI Gateway Explanation (Chosen):**  
Consume Phase 3 System X-Ray structural facts, AST-observed responsibilities, Phase 4 Business Rules, and Phase 5 Impact Surface. Use deterministic rules to evaluate candidate strategies, generate an auditable Decision Trace (`Observed Facts -> Implications -> Considerations -> Recommended Strategy`), list preserved business rules, and map impact boundaries. AI is strictly confined to generating explanatory narratives for established strategy facts.

---

## Decision

LEGACYX adopts **Option B — Deterministic Multi-Phase Reasoning + Decision Tracing + AI Gateway Explanation.**

### Key Rules
1. **Zero Numerical/Percentage Scores**: No artificial confidence percentages (e.g. *No "94% confidence"*, *No "Risk: 87%"*). All strategy evaluations rely on observable metrics: responsibility count, business rules count, direct dependents, transitive dependents, and max impact depth.
2. **Explicit Controlled Strategy Taxonomy**:
   - `MODULARIZE`: High responsibility count, internal decomposition within current deployment unit.
   - `EXTRACT_SERVICE`: Clear domain boundary, multiple business rules, external callers.
   - `STRANGLER`: High downstream impact surface, complex legacy state, incremental replacement via proxy.
   - `REFACTOR_IN_PLACE`: Low external coupling, clean code cleanup within component.
   - `ADAPTER`: Protocol/interface adaptation between legacy and modern.
   - `ANTI_CORRUPTION_LAYER`: Domain model isolation from legacy database schema.
   - `RETAIN_AND_WRAP`: Stateful logic, low change frequency, or high extraction risk; wrap in facade.
   - `NO_MODERNIZATION_NEEDED`: Well-formed DTO/Utility requiring no architectural changes.
3. **Insufficient Evidence Handling**: When a component lacks static evidence of multiple responsibilities or business rules, the engine defaults to `NO_MODERNIZATION_NEEDED` or `RETAIN_AND_WRAP`. It must NEVER fabricate a modernization recommendation.
4. **Auditable Human Overrides**: Human engineers can accept or override strategy recommendations. Every override records the engineer's identity, timestamp, original strategy, override strategy, and explicit rationale.
5. **Strict AI Boundary**: All strategy recommendations, decision traces, preserved rules, and impact surfaces are 100% established deterministically. AI only translates established facts into plain-language summaries.
6. **Strict Phase Boundary**: Phase 6 strictly produces strategy recommendations and preservation boundaries. No Phase 7+ features (migration planning, code generation, transformation, or behavioral validation) are included.

---

## Consequences

- Implemented in `backend/app/analysis_engine/responsibility_analyzer.py` and `strategy_selector.py`.
- Persistence managed by `ModernizationStrategy` SQLAlchemy model in `backend/app/models/modernization_strategy.py`.
- API endpoints exposed under `/api/v1/analysis/{analysis_id}/modernization/strategies`.
- Frontend provides interactive Modernization Strategy Workspace in `frontend/src/features/modernization/`.
