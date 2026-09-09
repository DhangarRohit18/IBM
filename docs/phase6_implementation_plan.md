# LEGACYX — Phase 6 Implementation Plan
## Modernization Strategy Engine & Decision Tracing

---

## Executive Summary

Phase 6 transitions LEGACYX from understanding **HOW** a system is structured (Phase 3 System X-Ray), **WHAT** business decisions it encodes (Phase 4 Business Logic Recovery), and **WHAT** ripple effects a change will cause (Phase 5 Impact Analysis), to answering:

> **"Given what we have learned about this legacy system, what modernization approach is appropriate, and why?"**

All strategy recommendations are **100% evidence-backed** and derived strictly from observable architectural facts, AST responsibility signals, Phase 4 business rules, and Phase 5 impact paths.

**Strict Anti-Pattern Rule:** LEGACYX will NOT operate as a generic AI coding assistant or fabricate artificial numerical scores (e.g. *No "Modernization Score: 94%"* or *No "Confidence: 89%"*). All evaluations rely on observable metrics and deterministic decision tracing. AI is strictly confined to explaining established strategy rationale via the central AI Gateway.

---

## 1. Architectural Strategy & Technical Taxonomy

### 1.1 Controlled Strategy Taxonomy
LEGACYX adopts a controlled, evidence-backed strategy taxonomy:

| Strategy | Description | Candidate Conditions |
|---|---|---|
| `MODULARIZE` | Decompose component internally into smaller packages/classes within existing deployment boundary. | High internal responsibility count (>=4), moderate dependencies, single deployment unit preference. |
| `EXTRACT_SERVICE` | Extract component into a standalone microservice or domain service. | Clear business boundary, multiple business rules (>=3), external callers, manageable external coupling. |
| `STRANGLER` | Replace component incrementally via proxy/gateway while legacy runs in parallel. | High impact surface (transitive dependents > 5), stateful business rules, high risk of big-bang replacement. |
| `REFACTOR_IN_PLACE` | Clean up internal code smells and structure without architectural boundary changes. | Low responsibility count (<=2), low external coupling, single domain focus. |
| `ADAPTER` | Bridge legacy interfaces/protocols to modern service interfaces. | Protocol/interface mismatch between legacy consumers and modernized services. |
| `ANTI_CORRUPTION_LAYER` | Isolate modern services from legacy database schema or domain model leaks. | High database table coupling, legacy data model leaks. |
| `RETAIN_AND_WRAP` | Keep original legacy component intact and expose via clean facade. | Complex stateful logic, low change frequency, or extraction risk outweighs benefits. |
| `NO_MODERNIZATION_NEEDED` | Component is well-formed, single-responsibility model or utility. | Simple DTO, Enum, or Utility with 0 business rules and single responsibility. |

### 1.2 The Full Reasoning Pipeline

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
│   Identifies Input Validation, Persistence, Calculations,   │
│   State Mutations, Service Coordination, Notifications      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            DETERMINISTIC STRATEGY SELECTOR ENGINE           │
│   1. Evaluate Rule Matrix over Observed Facts               │
│   2. Build Explicit Decision Trace (Fact -> Implication)    │
│   3. Identify Business Rules to Preserve                     │
│   4. Map Known Impact Surface                               │
│   5. Generate Recommended + Alternative Strategies          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI GATEWAY NARRATIVE                    │
│   Translates established decision trace into plain text     │
│   (Strictly reasoning over verified facts only)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design & Implementation Increments

### Increment 1: Architecture Decision Record & Documentation
- Create `docs/decisions/ADR-010-evidence-backed-modernization-strategy.md` defining the strategy selection rules, decision trace structure, and strict AI boundary.
- Create `docs/architecture/modernization-strategy.md` detailing the end-to-end modernization pipeline.

### Increment 2: Deterministic Responsibility Analyzer Engine
- Implement `ResponsibilityAnalyzer` in `backend/app/analysis_engine/responsibility_analyzer.py`.
- Analyzes method implementations and AST constructs to observe signals:
  - `INPUT_VALIDATION`: null checks, precondition assertions, `@Valid` annotations.
  - `BUSINESS_RULE_ENFORCEMENT`: conditional evaluations, threshold checks.
  - `CALCULATION_DERIVATION`: arithmetic formulas, fee derivations.
  - `SERVICE_COORDINATION`: invocations of external domain services/repositories.
  - `PERSISTENCE_MUTATION`: repository `save`, `update`, `delete` calls.
  - `STATE_TRANSITION`: explicit status field assignments.
  - `EXTERNAL_NOTIFICATION`: event publishing, email/log dispatches.
- Each observed responsibility includes exact relative file path, line numbers, method signature, and evidence snippet.

### Increment 3: Deterministic Strategy Selector Engine
- Implement `StrategySelector` in `backend/app/analysis_engine/strategy_selector.py`.
- Evaluates candidate components using deterministic rule conditions:
  - Compiles **Decision Trace**:
    `Observed Facts` → `Architectural Implications` → `Strategy Consideration` → `Recommended Strategy`.
  - Compiles **Preservation Rules**: Links all Phase 4 `BusinessRule` records that must be preserved.
  - Compiles **Impact Context**: Integrates Phase 5 direct and transitive impact surface.
  - Generates **Alternative Strategy** when viable (e.g., Recommended `MODULARIZE` vs Alternative `STRANGLER`).
  - Supports `RETAIN_AND_WRAP` and `NO_MODERNIZATION_NEEDED` outcomes when evidence does not justify active refactoring.

### Increment 4: Database Models & Schemas
- Create `ModernizationStrategy` ORM model in `backend/app/models/modernization_strategy.py`.
  - Fields: `id`, `analysis_id`, `repository_id`, `entity_id`, `recommended_strategy`, `alternative_strategy`, `decision_trace` (JSON), `observed_responsibilities` (JSON), `rules_to_preserve` (JSON), `impact_summary` (JSON), `qualitative_comparison` (JSON), `status` (`PROPOSED`, `REVIEWED`, `OVERRIDDEN`), `user_override_strategy`, `user_override_notes`, `ai_explanation`, `ai_explanation_status`.
- Create Pydantic schemas in `backend/app/schemas/modernization.py`.

### Increment 5: FastAPI Router & AI Gateway Extension
- Implement API routes in `backend/app/api/modernization.py`:
  - `POST /api/v1/analysis/{analysis_id}/modernization/evaluate`: Triggers deterministic strategy evaluation across all analysis entities.
  - `GET /api/v1/analysis/{analysis_id}/modernization/strategies`: Lists all evaluated component strategies with filters.
  - `GET /api/v1/modernization/strategies/{id}`: Detailed inspection of a component's strategy card, decision trace, and preservation rules.
  - `POST /api/v1/modernization/strategies/{id}/explain`: Requests AI Gateway narrative for established strategy facts.
  - `POST /api/v1/modernization/strategies/{id}/override`: Records human review or override with audited rationale.
- Register `modernization.router` in `backend/app/api/router.py`.
- Extend `AIGateway` (`backend/app/ai/gateway.py`) with `recommend_strategy_narrative` capability.

### Increment 6: Frontend Modernization Workspace
- Add Phase 6 types and client API methods in `frontend/src/services/api.ts`.
- Build components in `frontend/src/features/modernization/`:
  - `ModernizationCandidateSelector.tsx`: Component filter and strategy overview header.
  - `ObservedResponsibilitiesCard.tsx`: Observed responsibilities list with evidence links.
  - `BusinessRulesPreservationCard.tsx`: List of business rules that must be preserved.
  - `ImpactSurfaceCard.tsx`: Known direct & transitive impact surface.
  - `StrategyRecommendationCard.tsx`: Recommended strategy badge, decision trace, and why preferable rationale.
  - `StrategyAlternativeCard.tsx`: Alternative strategy comparison card.
  - `HumanOverrideModal.tsx`: Audit form for accepting or overriding strategy recommendations.
  - `ModernizationPage.tsx`: Full Phase 6 workspace view.
- Register **Modernization Strategy** tab in `ProjectWorkspacePage.tsx`.

### Increment 7: Test Suite & Verification
- Unit tests for `ResponsibilityAnalyzer`: `backend/tests/test_responsibility_analyzer.py`.
- Unit tests for `StrategySelector`: `backend/tests/test_strategy_selector.py`.
- Integration tests for API routes: `backend/tests/test_api_modernization.py`.
- Negative test: Verify system emits `NO_MODERNIZATION_NEEDED` or `RETAIN_AND_WRAP` when evidence does not support refactoring (prevents fake AI recommendations).
- LegacyBank Demo test: Verify `TransferService` produces the complete reasoning chain:
  `Structure -> Responsibilities -> Business Rules -> Impact -> MODULARIZE (Recommended) -> STRANGLER (Alternative) -> Preservation Rules`.
- Execute full test suite (`pytest`) and frontend build (`npm run build`).
- Produce `docs/phase6_verification_report.md`.

---

## 3. Strict Scope & Rule Boundaries

### Must NOT Be Implemented (Scope Fence)
- NO Migration Plans or Task Generation (Phase 7)
- NO Code Transformation or Target Code Generation (Phase 8)
- NO Behavioral Validation or Sandbox Execution (Phase 9)
- NO Numerical/Percentage Confidence Scores (No "94% score")
- NO Unrestricted AI Chat or Invented Architecture Facts

---

## 4. Verification Plan

### Automated Tests
- `python -m pytest tests/ -v`: Must achieve 100% clean test pass.
- `npm run build` in `frontend`: Must pass with 0 TypeScript/Vite errors.

### LegacyBank End-to-End Verification
Verify `TransferService` strategy outputs:
- **Observed Responsibilities**: Validation, Fee Calculation, Fraud Coordination, Persistence Mutation, State Transition.
- **Rules to Preserve**: High-value approval, balance check, fee calculation, state update.
- **Impact Surface**: `TransferController` (Direct), `NotificationService` (Transitive).
- **Recommended Strategy**: `MODULARIZE` with explicit Decision Trace.
- **Alternative Strategy**: `STRANGLER` with qualitative comparison.
