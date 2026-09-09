# LEGACYX — Phase 4 Implementation Plan
## Business Logic Recovery & Explainable Rule Extraction

**Phase Name**: Phase 4: Business Logic Recovery  
**Status**: PROPOSED FOR REVIEW  
**Target Completion**: Hackathon Phase 4 Sprint  
**Architectural Contract**: Enforced by [`AGENTS.md`](../AGENTS.md) and [`ADR-005`](decisions/ADR-005-ai-gateway-abstraction.md)

---

## 1. Executive Summary & Objective

Phase 4 progresses LEGACYX from structural understanding (**"HOW is this legacy system structured?"**) to business recovery (**"WHAT business decisions, validations, calculations, actions, and state transitions are encoded inside this legacy system?"**).

### Core Architectural Principle
**AI MUST NEVER be the source of truth for a business rule.**

1. **Deterministic Static Analysis** establishes all facts, conditions, thresholds, actions, calculations, state transitions, and source evidence.
2. **AI Gateway Abstraction** (`backend/app/ai/`) provides optional explanations, summaries, and translations of technical logic into readable business language.
3. **Source Evidence** preserves line numbers, relative file paths, AST constructs, and extraction reasons for every extracted rule.
4. **No Numeric Score Inventing**: Confidence percentages (e.g. `94% accuracy`) are strictly prohibited.
5. **Separation of Facts & Explanations**: AI explanations are stored separately from deterministic facts. AI failures or timeouts never invalidate extracted rules.

---

## 2. System Architecture & Scope Boundaries

### 2.1 Extraction & Explanation Pipeline

```
           Phase 3 Structural Entities & ASTs (javalang 0.13.0)
                                   │
                                   ▼
                 ┌───────────────────────────────────┐
                 │    BusinessRuleExtractor          │ ── Deterministic AST Pattern Matcher
                 └───────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       Conditional & Threshold           Validation & Calculation
       Rules (if/switch bounds)          (guards, formulas, state changes)
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                 ┌───────────────────────────────────┐
                 │  BusinessRule Persistence Model   │ ── PostgreSQL DB (Facts + Evidence)
                 └───────────────────────────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
        FastAPI Business Rules API       Optional AI Explanation
        (/api/v1/analysis/.../rules)     (AI Gateway Abstraction)
                     │                           │
                     └─────────────┬─────────────┘
                                   ▼
                 ┌───────────────────────────────────┐
                 │  Business Logic Recovery Web UI   │ ── Workspace, Inspector & Graph
                 └───────────────────────────────────┘
```

### 2.2 Strict Scope Boundaries

#### IMPLEMENT:
- Deterministic business rule candidate extraction
- Controlled rule taxonomy (`VALIDATION`, `CONDITIONAL`, `THRESHOLD`, `CALCULATION`, `ACTION`, `STATE_TRANSITION`)
- Condition, action, threshold, formula, and state transition detection
- Line-level source construct evidence preservation
- Rule review state machine (`EXTRACTED` → `EXPLAINED` → `REVIEWED` / `REJECTED`)
- Centralized AI Gateway abstraction (`backend/app/ai/`) with `watsonx`, `openai`, and `mock` providers
- Business Logic Recovery REST APIs & interactive Frontend UI workspace
- Lightweight deterministic rule flow visualizer (`BusinessRuleGraph.tsx`)
- Expanded multi-package `LegacyBank` fixture
- Comprehensive test suite & documentation

#### DO NOT IMPLEMENT:
- Modernization recommendations or strategy generation
- Migration planning
- Code transformation or generated replacement code
- Behavioral validation or containerized sandbox execution
- Generic AI chatbot or unrestricted natural-language code queries
- Phase 5 functionality

---

## 3. Database Schema & ORM Models

### 3.1 `business_rules` Table (`BusinessRule`)

| Column Name | Type | Constraints / Details |
|---|---|---|
| `id` | `VARCHAR(36)` | Primary Key (UUID) |
| `analysis_id` | `VARCHAR(36)` | Foreign Key -> `analysis_runs.id` (ON DELETE CASCADE) |
| `repository_id` | `VARCHAR(36)` | Foreign Key -> `repositories.id` (ON DELETE CASCADE) |
| `entity_id` | `VARCHAR(36)` | Foreign Key -> `code_entities.id` (Nullable) |
| `method_id` | `VARCHAR(36)` | Foreign Key -> `code_methods.id` (Nullable) |
| `rule_type` | `VARCHAR(32)` | Enum: `VALIDATION`, `CONDITIONAL`, `THRESHOLD`, `CALCULATION`, `ACTION`, `STATE_TRANSITION` |
| `title` | `VARCHAR(255)` | Deterministic title (e.g. `Threshold check: amount > 50000`) |
| `status` | `VARCHAR(32)` | Enum: `EXTRACTED`, `EXPLAINED`, `REVIEWED`, `REJECTED` |
| `condition_expression` | `TEXT` | Deterministic condition string (e.g. `amount > 50000`) |
| `action_expression` | `TEXT` | Deterministic action string (e.g. `requireManagerApproval()`) |
| `outcome_expression` | `TEXT` | Deterministic outcome (e.g. `throw InsufficientBalanceException`) |
| `threshold_value` | `VARCHAR(128)` | Parsed constant threshold (e.g. `50000`) |
| `threshold_operator` | `VARCHAR(16)` | Comparison operator (e.g. `>`, `>=`, `<`, `<=`, `==`) |
| `calculation_formula` | `TEXT` | Formula expression (e.g. `amount * 0.02`) |
| `previous_state` | `VARCHAR(128)` | Source state (only if deterministically known) |
| `new_state` | `VARCHAR(128)` | Target state (e.g. `APPROVED`, `BLOCKED`) |
| `relative_file_path` | `VARCHAR(512)` | Relative file path |
| `line_start` | `INTEGER` | Line start |
| `line_end` | `INTEGER` | Line end |
| `source_construct` | `VARCHAR(128)` | Construct (e.g. `if_statement`, `assignment`, `throw_statement`) |
| `extraction_reason` | `TEXT` | Evidence reason |
| `ai_explanation` | `TEXT` | AI generated summary (Nullable) |
| `ai_explanation_status` | `VARCHAR(32)` | Enum: `NOT_REQUESTED`, `PENDING`, `COMPLETED`, `FAILED` |
| `reviewed_by` | `VARCHAR(128)` | Reviewer identifier (Nullable) |
| `reviewed_at` | `TIMESTAMP` | Timestamp of review (Nullable) |
| `review_notes` | `TEXT` | Engineer notes (Nullable) |
| `created_at` | `TIMESTAMP` | Creation timestamp |
| `updated_at` | `TIMESTAMP` | Update timestamp |

---

## 4. Controlled Rule Taxonomy

1. **`VALIDATION`**: Guard checks that reject invalid inputs or state (e.g., `balance < amount`, `account.isBlocked()`).
2. **`CONDITIONAL`**: General conditional branching logic (`if` / `switch` statements).
3. **`THRESHOLD`**: Comparison of a variable against a fixed literal numeric/string boundary (`amount > 50000`).
4. **`CALCULATION`**: Mathematical formula calculations or fee derivations (`fee = amount * 0.02`).
5. **`ACTION`**: Secondary side-effect operations invoked conditionally (`sendNotification()`, `requireManagerApproval()`).
6. **`STATE_TRANSITION`**: Explicit state mutation calls (`account.setStatus(BLOCKED)`).

---

## 5. Deterministic Rule Extraction Engine

### 5.1 Extractor Implementation (`rule_extractor.py`)

The extractor inspects method ASTs produced by `JavaASTParser`:

```python
class BusinessRuleExtractor:
    def extract_rules(
        self,
        analysis_id: str,
        repository_id: str,
        entity: CodeEntity,
        method: CodeMethod,
        ast_node: javalang.ast.Node,
        file_content_lines: list[str],
    ) -> list[BusinessRule]:
        ...
```

### 5.2 Extraction Patterns

- **Conditional & Threshold Rules**: Matches `IfStatement` nodes. Evaluates `BinaryOperation` expressions for comparison operators (`>`, `>=`, `<`, `<=`, `==`, `!=`). Extracts threshold literal values and variable names.
- **Validation Rules**: Matches `IfStatement` blocks containing `ThrowStatement` or rejection return calls (`return false`, `return REJECTED`).
- **Calculation Rules**: Matches `Assignment` nodes containing mathematical operators (`*`, `/`, `+`, `-`).
- **Action Invocations**: Identifies helper method calls invoked inside conditional bodies.
- **State Transition Detection**: Matches setter invocations matching `setStatus(...)`, `setState(...)` or state field assignments. Unresolved/ambiguous previous states remain `None`.

---

## 6. AI Gateway Abstraction & Safety Architecture

### 6.1 Provider Interface (`backend/app/ai/`)

- `base.py`: Defines `AIProvider` base class with `async def explain_business_rule(self, rule_context: dict) -> str`.
- `gateway.py`: `AIGateway` singleton routing requests, redacting secrets, caching responses, and maintaining circuit breaking.
- `providers/mock_provider.py`: Offline deterministic mock provider for unit tests and local dev.
- `providers/watsonx_provider.py`: IBM watsonx integration using configured API keys.
- `providers/openai_provider.py`: Fallback OpenAI integration.

### 6.2 AI Prompt Safety Boundaries
The AI prompt receives ONLY structured extracted facts:
```json
{
  "rule_type": "THRESHOLD",
  "condition": "amount > 50000",
  "action": "requireManagerApproval()",
  "file": "TransferService.java",
  "lines": "67-69"
}
```
The AI is instructed ONLY to translate the given technical condition into concise business prose. It is strictly forbidden from inferring missing facts or inventing external rules.

If the AI call fails or times out, `ai_explanation_status` is set to `FAILED`, while the rule itself remains fully valid in `EXTRACTED` status.

---

## 7. Business Logic Recovery API Specifications

- `POST /api/v1/analysis/{analysis_id}/business-rules/extract`: Trigger deterministic rule extraction run.
- `GET /api/v1/analysis/{analysis_id}/business-rules`: List business rules (filterable by `rule_type`, `status`, `class_id`, `q`, paginated).
- `GET /api/v1/analysis/{analysis_id}/business-rules/{rule_id}`: Retrieve detailed rule inspection view.
- `POST /api/v1/business-rules/{rule_id}/explain`: Trigger AI Gateway explanation for a specific rule.
- `POST /api/v1/business-rules/{rule_id}/review`: Update status (`REVIEWED` or `REJECTED`) with optional review notes.

---

## 8. Frontend UI Architecture (`frontend/src/features/business_rules/`)

- `BusinessRulesPage.tsx`: Main workspace view featuring metric summary cards, category pills, search bar, rule list table, and split-pane detail drawer.
- `RuleListTable.tsx`: Interactive data table with rule type badges, status pills, and line evidence summaries.
- `RuleDetailDrawer.tsx`: Inspector pane showing:
  - Deterministic facts (Condition, Action, Threshold, Formula, States).
  - AI Explanation block with `[Explain with AI]` action button and status indicator.
  - Line evidence block with file path, line numbers, construct, and `[View Source]` button linking to `SourceEvidenceViewer`.
  - Review controls (`[Mark Reviewed]`, `[Reject]`, notes field).
- `BusinessRuleGraph.tsx`: Lightweight deterministic rule flow visualizer showing `Condition → Decision → Action → State Transition`.

---

## 9. Expanded `LegacyBank` Fixture Specification

Update `backend/tests/fixtures/legacy_bank/` Java source files to demonstrate 6 canonical business rules:
1. **High-Value Transfer Threshold**: `if (amount > 50000) requireManagerApproval();`
2. **Insufficient Balance Rejection**: `if (balance < amount) throw new InsufficientBalanceException("Insufficient funds");`
3. **Transfer Fee Calculation**: `double fee = amount * 0.02;`
4. **Blocked Account Guard**: `if (account.getStatus() == AccountStatus.BLOCKED) throw new IllegalStateException("Account blocked");`
5. **State Transition**: `transaction.setStatus(TransactionStatus.APPROVED);`
6. **Notification Action**: `if (success) notificationService.sendTransferNotification(user, amount);`

---

## 10. Implementation Plan & Proposed File Changes

### Backend Files
- `[NEW]` [business_rule.py](file:///d:/LegacyX/backend/app/models/business_rule.py): SQLAlchemy ORM model.
- `[NEW]` [004_business_rules.py](file:///d:/LegacyX/backend/alembic/versions/004_business_rules.py): Alembic DB migration.
- `[NEW]` [rule_extractor.py](file:///d:/LegacyX/backend/app/analysis_engine/rule_extractor.py): Deterministic rule extractor.
- `[NEW]` [base.py](file:///d:/LegacyX/backend/app/ai/base.py): AI Provider abstract base class.
- `[NEW]` [gateway.py](file:///d:/LegacyX/backend/app/ai/gateway.py): Central AI Gateway abstraction.
- `[NEW]` [mock_provider.py](file:///d:/LegacyX/backend/app/ai/providers/mock_provider.py): Offline test AI provider.
- `[NEW]` [watsonx_provider.py](file:///d:/LegacyX/backend/app/ai/providers/watsonx_provider.py): IBM watsonx provider interface.
- `[NEW]` [business_rules.py](file:///d:/LegacyX/backend/app/schemas/business_rules.py): Pydantic schemas.
- `[NEW]` [business_rules.py](file:///d:/LegacyX/backend/app/api/business_rules.py): FastAPI API routes.
- `[MODIFY]` [service.py](file:///d:/LegacyX/backend/app/analysis_engine/service.py): Include rule extraction step in `AnalysisService`.

### Frontend Files
- `[NEW]` [BusinessRulesPage.tsx](file:///d:/LegacyX/frontend/src/features/business_rules/BusinessRulesPage.tsx): Main page workspace.
- `[NEW]` [RuleListTable.tsx](file:///d:/LegacyX/frontend/src/features/business_rules/RuleListTable.tsx): Rule data table.
- `[NEW]` [RuleDetailDrawer.tsx](file:///d:/LegacyX/frontend/src/features/business_rules/RuleDetailDrawer.tsx): Inspector drawer.
- `[NEW]` [BusinessRuleGraph.tsx](file:///d:/LegacyX/frontend/src/features/business_rules/BusinessRuleGraph.tsx): Rule flow graph visualizer.
- `[MODIFY]` [api.ts](file:///d:/LegacyX/frontend/src/services/api.ts): API client for business rules.
- `[MODIFY]` [ProjectWorkspacePage.tsx](file:///d:/LegacyX/frontend/src/pages/ProjectWorkspacePage.tsx): Add "Business Logic" tab.

### Documentation & Tests
- `[NEW]` [ADR-008-business-logic-deterministic-extraction.md](file:///d:/LegacyX/docs/decisions/ADR-008-business-logic-deterministic-extraction.md)
- `[NEW]` [business-logic-recovery.md](file:///d:/LegacyX/docs/architecture/business-logic-recovery.md)
- `[NEW]` [test_rule_extractor.py](file:///d:/LegacyX/backend/tests/test_rule_extractor.py)
- `[NEW]` [test_ai_gateway.py](file:///d:/LegacyX/backend/tests/test_ai_gateway.py)
- `[NEW]` [test_api_business_rules.py](file:///d:/LegacyX/backend/tests/test_api_business_rules.py)

---

## 11. Verification Plan & Acceptance Criteria

### Automated Verification
1. `python -m pytest tests/ -v`: Verify 100% test pass rate across all backend unit & API tests.
2. `npm run build`: Verify 0 TypeScript/Vite compilation errors on frontend.
3. `alembic upgrade head`: Verify DB migration execution.

### Manual Demo Flow Verification
1. Ingest `LegacyBank` repository artifact.
2. Run System X-Ray static analysis.
3. Navigate to **Business Logic Recovery** workspace tab.
4. Verify extraction of High-Value Transfer threshold (`amount > 50000`), Insufficient Balance validation, Fee calculation (`amount * 0.02`), Blocked Account guard, State transition, and Notification action.
5. Click **View Source** on High-Value Transfer rule and confirm exact line highlight in `SourceEvidenceViewer`.
6. Click **Explain with AI** and verify separate AI explanation rendering.
7. Mark rule as **REVIEWED** and verify state transition.

---

*Phase 4 Implementation Plan — LEGACYX Engineering Team*
