# LEGACYX — Phase 5 Implementation Plan
## Evidence-Backed Deterministic Impact Analysis

**Phase Name**: Phase 5: Impact Analysis  
**Status**: PROPOSED FOR REVIEW  
**Target Completion**: Hackathon Phase 5 Sprint  
**Architectural Contract**: Enforced by [`AGENTS.md`](../AGENTS.md), [`ADR-001`](decisions/ADR-001-deterministic-analysis-over-ai-only.md), [`ADR-005`](decisions/ADR-005-ai-gateway-abstraction.md), and [`ADR-008`](decisions/ADR-008-business-logic-deterministic-extraction.md)

---

## 1. Executive Summary & Objective

Phase 5 enables LEGACYX to answer the core modernization question:
**"If I change this legacy component, what other technical components and business rules could be affected, and why?"**

### Core Architectural Guarantees
1. **100% Evidence-Backed**: Impact is derived deterministically from Phase 3 structural relationships (`code_relationships`) and Phase 4 extracted business rules (`business_rules`).
2. **AI Cannot Invent Impact**: AI is used ONLY to produce supplementary explanations for already-established impact paths. AI can never invent affected components, relationships, or line numbers.
3. **No Fake Risk Scores**: Floating-point risk scores (e.g. `87% risk`, `92% confidence`) are **STRICTLY PROHIBITED**.
4. **Explicit Direct vs. Transitive Separation**: Direct dependencies (depth 1) and transitive dependencies (depth > 1) are cleanly categorized with explicit hop chains.
5. **Cycle Detection & Bounded Depth**: Traversal handles circular dependencies safely and respects depth limits.

---

## 2. System Architecture & Scope Boundaries

### 2.1 Impact Engine & Explanation Pipeline

```
          Phase 3 Code Relationships + Phase 4 Business Rules
                                   │
                                   ▼
                 ┌───────────────────────────────────┐
                 │     ImpactAnalyzer Engine         │ ── BFS Traversal + Cycle & Depth Control
                 └───────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
  Direct Impact              Transitive Impact          Business Rule Impact
  (Depth 1 Hop)              (Depth 2..N Hops)          (Associated Rules)
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                 ┌───────────────────────────────────┐
                 │      Impact Response & Paths      │ ── Structured Hop Chains & Line Evidence
                 └───────────────────────────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
          Impact Analysis REST API        Optional AI Explanation
          (/api/v1/analysis/.../impact)   (AIGateway Abstraction)
                     │                           │
                     └─────────────┬─────────────┘
                                   ▼
                 ┌───────────────────────────────────┐
                 │   Impact Analysis Web Workspace   │ ── Target Selector, Path Inspection, Graph
                 └───────────────────────────────────┘
```

### 2.2 Strict Scope Boundaries

#### IMPLEMENT:
- Controlled impact taxonomy (`DIRECT_DEPENDENCY`, `TRANSITIVE_DEPENDENCY`, `CALL_CHAIN`, `INHERITANCE_IMPACT`, `IMPLEMENTATION_IMPACT`, `BUSINESS_RULE_IMPACT`, `STATE_BEHAVIOR_IMPACT`, `SOURCE_IMPACT`)
- Deterministic impact analyzer engine (`impact_analyzer.py`) operating on `CodeRelationship` and `BusinessRule` tables
- Change targets: `class`, `method`, `field`, `package`, `business_rule`
- Cycle detection & bounded traversal depth control
- Direct vs. transitive impact classification with explicit path traces
- Business Rule ↔ Architecture graph integration
- Optional AI Gateway explanation for established impact paths
- REST APIs (`/api/v1/analysis/{analysis_id}/impact`, `/api/v1/impact/explain`)
- Dedicated Impact Analysis frontend workspace (`ImpactPage.tsx`)
- Expanded `LegacyBank` scenario & unit/API tests

#### DO NOT IMPLEMENT:
- Modernization recommendations or target architecture design
- Migration planning or task scheduling
- Code transformation or generated replacement code
- Behavioral validation or containerized sandbox execution
- Generic AI chatbot or natural-language change requests

---

## 3. Controlled Impact Taxonomy

1. **`DIRECT_DEPENDENCY`**: Immediate 1-hop dependency (import, field declaration, constructor parameter).
2. **`TRANSITIVE_DEPENDENCY`**: Multi-hop dependency through intermediate components.
3. **`CALL_CHAIN`**: Chain of method invocations (`CALLS` relationships).
4. **`INHERITANCE_IMPACT`**: Superclass/subclass hierarchy impact (`EXTENDS`).
5. **`IMPLEMENTATION_IMPACT`**: Interface-to-implementer relationship (`IMPLEMENTS`).
6. **`BUSINESS_RULE_IMPACT`**: Business rules extracted from target or affected by target changes.
7. **`STATE_BEHAVIOR_IMPACT`**: State transitions affected by setter or state-modifying invocations.
8. **`SOURCE_IMPACT`**: Line-level file references and AST construct evidence backing each impact hop.

---

## 4. Deterministic Impact Analyzer Engine

### 4.1 Analyzer Implementation (`backend/app/analysis_engine/impact_analyzer.py`)

```python
class ImpactAnalyzer:
    """
    Deterministic Impact Traversal Engine.
    Operates on Phase 3 relationships and Phase 4 business rules.
    """

    async def analyze_impact(
        self,
        session: AsyncSession,
        analysis_id: str,
        target_type: str,  # class, method, field, package, rule
        target_id: str,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        ...
```

### 4.2 Algorithm & Guarantees
1. **Target Identification**: Resolves `target_id` to its starting symbol and file location. If target is a `BusinessRule`, resolves to its enclosing method/class first.
2. **Graph Traversal (BFS)**:
   - Tracks `visited_nodes: set[str]` to detect cycles. If a cycle is detected, marks `has_cycle = True` on path without infinite loop.
   - Limits search depth to `max_depth` (default 3, max 5).
3. **Direct vs. Transitive Grouping**:
   - `depth == 1`: Classified as `DIRECT_DEPENDENCY`, `CALL_CHAIN`, `INHERITANCE_IMPACT`, or `IMPLEMENTATION_IMPACT`.
   - `depth > 1`: Classified as `TRANSITIVE_DEPENDENCY`.
4. **Business Rule Linking**:
   - Fetches all `BusinessRule` records associated with any entity or method in the impacted path.
5. **Source Traceability**: Every hop records `source_symbol`, `target_symbol`, `relationship_type`, `relative_file_path`, `line_number`, and `evidence_reason`.

---

## 5. AI Gateway Integration & Safety

- Route: `POST /api/v1/impact/explain`.
- Context sent to `AIGateway`:
  ```json
  {
    "target_name": "TransferService.processTransfer()",
    "direct_impacts": ["AccountRepository", "FraudService"],
    "transitive_impacts text": ["Account", "AccountStatus"],
    "affected_rules": ["High-value transfer threshold", "Insufficient balance validation"],
    "path": "TransferService.processTransfer() -> CALLS -> AccountRepository.save()"
  }
  ```
- Guarantee: AI translates established facts into a 2-3 sentence business narrative. If AI fails, deterministic facts and line evidence remain 100% accessible.

---

## 6. Business Logic & Impact REST API Specifications

- `GET /api/v1/analysis/{analysis_id}/impact`: Perform impact analysis for a target (`target_type`, `target_id`, `max_depth`, `include_rules`).
- `POST /api/v1/impact/explain`: Request AI Gateway explanation for an established impact path result.

---

## 7. Frontend UI Architecture (`frontend/src/features/impact/`)

- `ImpactPage.tsx`: Dedicated Impact Analysis workspace.
- `ImpactTargetSelector.tsx`: Dropdown/Search picker for selecting Class, Method, Field, or Business Rule as change target.
- `ImpactSummaryCards.tsx`: Summary metric cards (Direct Targets, Transitive Targets, Business Rules Affected, State Changes).
- `ImpactPathViewer.tsx`: Categorized impact view (`DIRECT IMPACT`, `BUSINESS LOGIC IMPACT`, `TRANSITIVE IMPACT`) with collapsible path chains and `[View Evidence]` buttons.
- `ImpactGraph.tsx`: Impact-focused SVG graph renderer highlighting target node in distinct color and active dependency edges.

---

## 8. Proposed Files to Create / Modify

### Backend
- `[NEW]` [impact_analyzer.py](file:///d:/LegacyX/backend/app/analysis_engine/impact_analyzer.py): Impact engine.
- `[NEW]` [impact.py](file:///d:/LegacyX/backend/app/schemas/impact.py): Pydantic response schemas.
- `[NEW]` [impact.py](file:///d:/LegacyX/backend/app/api/impact.py): FastAPI API endpoints.
- `[MODIFY]` [router.py](file:///d:/LegacyX/backend/app/api/router.py): Include `impact.router`.

### Frontend
- `[NEW]` [ImpactPage.tsx](file:///d:/LegacyX/frontend/src/features/impact/ImpactPage.tsx): Main Impact Analysis view.
- `[NEW]` [ImpactTargetSelector.tsx](file:///d:/LegacyX/frontend/src/features/impact/ImpactTargetSelector.tsx): Target selector.
- `[NEW]` [ImpactPathViewer.tsx](file:///d:/LegacyX/frontend/src/features/impact/ImpactPathViewer.tsx): Path breakdown component.
- `[NEW]` [ImpactGraph.tsx](file:///d:/LegacyX/frontend/src/features/impact/ImpactGraph.tsx): Impact-focused SVG visualizer.
- `[MODIFY]` [api.ts](file:///d:/LegacyX/frontend/src/services/api.ts): API client methods for impact endpoints.
- `[MODIFY]` [ProjectWorkspacePage.tsx](file:///d:/LegacyX/frontend/src/pages/ProjectWorkspacePage.tsx): Add "Impact Analysis" tab.

### Documentation & Tests
- `[NEW]` [ADR-009-deterministic-impact-analysis.md](file:///d:/LegacyX/docs/decisions/ADR-009-deterministic-impact-analysis.md)
- `[NEW]` [impact-analysis.md](file:///d:/LegacyX/docs/architecture/impact-analysis.md)
- `[NEW]` [test_impact_analyzer.py](file:///d:/LegacyX/backend/tests/test_impact_analyzer.py)
- `[NEW]` [test_api_impact.py](file:///d:/LegacyX/backend/tests/test_api_impact.py)

---

## 9. Verification Plan & Acceptance Criteria

### Automated Verification
1. `python -m pytest tests/ -v`: 100% test pass rate across all unit and integration tests (including cycle detection & depth limit tests).
2. `npm run build`: Clean production build with 0 TypeScript/Vite errors.

### Manual Demo Flow Verification
1. Open `LegacyBank` project in LEGACYX workspace.
2. Navigate to **Impact Analysis** tab.
3. Select `TransferService.processTransfer()` as change target.
4. Verify Direct Impacts: `TransferController`, `AccountRepository`, `FraudService`.
5. Verify Business Rule Impacts: `High-value transfer threshold`, `Insufficient balance validation`, `Transfer fee calculation`.
6. Verify Transitive Impacts: `Account`, `AccountStatus`.
7. Click **View Evidence** on `AccountRepository` and confirm line-level call site evidence (`TransferService.java:38`).
8. Click **Explain Impact with AI** and verify separate AI summary rendering.

---

*Phase 5 Implementation Plan — LEGACYX Engineering Team*
