# LEGACYX Architecture — Build, Unit Test & Behavioral Equivalence Validation (Phase 9)

## 1. Executive Overview

Phase 9 (**Build, Unit Test & Behavioral Equivalence Validation**) provides empirical, verifiable execution evidence for modernized code artifacts produced in Phase 8.

```
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 8 — APPROVED MODERNIZATION ARTIFACTS                            │
│  storage/modernized/{project_id}/{plan_id}/                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 9 — VALIDATION PIPELINE                                         │
│                                                                        │
│  ┌──────────────────────┐   ┌───────────────────────────────────────┐  │
│  │ Build Environment    │───│ Step 1: JDK / javac Compilation       │  │
│  │ Detection Guard      │   │ (PASS / FAIL / UNAVAILABLE)           │  │
│  └──────────────────────┘   └───────────────────┬───────────────────┘  │
│                                                 │                      │
│                                                 ▼                      │
│                             ┌───────────────────────────────────────┐  │
│                             │ Step 2: Unit Test Execution           │  │
│                             │ (Captured exit code, stdout/stderr)   │  │
│                             └───────────────────┬───────────────────┘  │
│                                                 │                      │
│                                                 ▼                      │
│                             ┌───────────────────────────────────────┐  │
│                             │ Step 3: Behavioral Test Scenarios     │  │
│                             │ (Legacy vs Modernized Output Compare) │  │
│                             │ (MATCH / MISMATCH / UNABLE)           │  │
│                             └───────────────────┬───────────────────┘  │
│                                                 │                      │
│                                                 ▼                      │
│                             ┌───────────────────────────────────────┐  │
│                             │ Audited Validation Record & Evidence  │  │
│                             │ Human Review & AI Narrative           │  │
│                             └───────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Validation Stages

### Stage 1: Build & Compilation Validation
- Detects system JDK (`javac`).
- Executes compilation inside an isolated temporary directory.
- Captures `exit_code`, `duration_ms`, `stdout`, `stderr`.
- Statuses: `PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`, `NOT_RUN`.

### Stage 2: Unit Test Execution
- Executes generated test stubs (`*Test.java`) inside isolated workspace.
- Captures total tests, passed count, failed count, skipped count, exit code, and log output.
- Statuses: `PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`, `NOT_RUN`.

### Stage 3: Behavioral Equivalence Scenario Evaluation
- Consumes authoritative Phase 4 `BusinessRule` records.
- Executes legacy logic vs modernized logic across predefined test inputs.
- Compares return values, state transitions, exception types, and calculated formulas.
- Statuses: `MATCH`, `MISMATCH`, `UNABLE_TO_VALIDATE`.

---

## 3. Controlled Status Taxonomy

| Model Field | Allowed Values |
|---|---|
| `ValidationStatus` | `PROPOSED`, `RUNNING`, `COMPLETED`, `FAILED`, `ENVIRONMENT_UNAVAILABLE`, `REVIEWED` |
| `BuildStatus` | `PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`, `NOT_RUN` |
| `TestStatus` | `PASS`, `FAIL`, `ENVIRONMENT_UNAVAILABLE`, `NOT_RUN` |
| `BehaviorStatus` | `PASS`, `FAIL`, `UNABLE_TO_VALIDATE`, `NOT_RUN` |
| `OverallStatus` | `VALIDATED`, `VALIDATION_FAILED`, `VALIDATION_BLOCKED`, `PARTIALLY_VALIDATED` |
| `ComparisonResult` | `MATCH`, `MISMATCH`, `UNABLE_TO_VALIDATE` |

---

## 4. Canonical LegacyBank Validation Scenarios

### Target: `AccountService.processTransfer()`

Derived directly from Phase 4 `BusinessRule` records:

| Scenario Name | Rule ID | Input Condition | Expected Legacy Output | Expected Modernized Output | Comparison |
|---|---|---|---|---|:---:|
| **Transfer Limit Exceeded Guard** | `BR-001` | `amount = 60000` | `approval_required = true`, state `PENDING_APPROVAL` | `approval_required = true`, state `PENDING_APPROVAL` | `MATCH` |
| **Normal Transfer Execution** | `BR-001` | `amount = 1000` | `approval_required = false`, state `COMPLETED` | `approval_required = false`, state `COMPLETED` | `MATCH` |
| **Insufficient Balance Guard** | `BR-002` | `balance < amount` | Throws `InsufficientBalanceException` | Throws `InsufficientBalanceException` | `MATCH` |
| **Fee Calculation Verification** | `BR-003` | `amount = 10000` | `fee = 200.0` | `fee = 200.0` | `MATCH` |
| **Blocked Account Guard** | `BR-004` | `status = BLOCKED` | Throws `AccountBlockedException` | Throws `AccountBlockedException` | `MATCH` |

---

## 5. Security & Isolation Model

- **Subprocess Workspace Isolation**: Temporary directory created per validation run under `storage/temp_validation/{run_id}/`. Cleaned up upon completion.
- **Original Source Immutability**: `storage/extracted/` is strictly read-only.
- **Path Traversal Protection**: Validation runners sanitize all input paths.
