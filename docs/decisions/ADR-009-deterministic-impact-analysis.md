# ADR-009 — Deterministic Impact Analysis Architecture & Strict AI Boundary

**Status:** Accepted  
**Date:** Phase 5  
**Deciders:** Project Lead  

---

## Context

LEGACYX requires evaluating the ripple effect of changes to legacy components or business rules.

Two approaches were evaluated:

**Option A — AI Graph & Impact Assessment:**  
Ask an LLM to predict what components and business rules would be affected by changing a legacy component.

**Option B — Deterministic Graph Traversal + Bidirectional Business Rule Linking (Chosen):**  
Perform deterministic graph traversal over Phase 3 structural relationship tables (`CodeRelationship`, `CodeEntity`, `CodeMethod`) and Phase 4 `BusinessRule` records. Traverse in both forward (dependencies) and reverse (dependents) directions, linking business rules bidirectionally. AI is strictly confined to explaining established impact paths and must never invent impact facts.

---

## Decision

LEGACYX adopts **Option B — Deterministic Graph Traversal + Bidirectional Business Rule Linking.**

### Key Rules
1. **Direct Impact Evidence**: Direct impact must be based on an immediately evidenced static relationship (or direct method/entity containment for rules), not loose depth=1 semantics.
2. **Bidirectional Impact Traversal**: Support both `forward` (what does target depend on?) and `reverse` (what components depend on target?).
3. **Bidirectional Business Rule Impact**: Support component-to-rule (`Component → Rule`) and rule-to-component (`Rule → Containing Method/Entity → Upstream/Downstream Dependencies`) impact resolution.
4. **Explicit NO EVIDENCED IMPACT**: When no static relationship or business rule association exists within the requested depth, return an explicit `NO EVIDENCED IMPACT` status rather than guessing.
5. **Strict AI Boundary**: All nodes, edges, relationships, and rule connections in an impact result are 100% established by static graph traversal. AI may only explain established paths.
6. **Reuse Existing Models**: Reuses Phase 3 relationships/entities and Phase 4 `BusinessRule` instances without creating a duplicate graph engine or schema.
7. **Strict Phase 5 Scope Boundary**: No Phase 6+ features (modernization recommendations, target architecture, code transformation, or validation) are included.

---

## Consequences

- Implemented in `backend/app/analysis_engine/impact_analyzer.py`.
- API exposed under `/api/v1/analysis/{analysis_id}/impact` and `/api/v1/impact/explain`.
- Frontend provides interactive forward/reverse traversal visualization with direct vs. transitive impact classification and rule linking.
