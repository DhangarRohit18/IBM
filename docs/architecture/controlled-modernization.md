# LEGACYX Architecture — Controlled Modernization & Code Transformation (Phase 8)

## 1. Executive Overview

Phase 8 (**Controlled Modernization & Code Transformation**) bridges **Phase 7 Approved Modernization Plans** to **Isolated Target Code Generation**.

```
┌────────────────────────────────┐
│  Phase 6 — Modernization       │
│  Strategy Selection            │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│  Phase 7 — Approved            │
│  Modernization Plan & Tasks    │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────────────┐
│  PHASE 8 — CONTROLLED MODERNIZATION ENGINE                             │
│                                                                        │
│  ┌───────────────────────┐   ┌──────────────────────────────────────┐  │
│  │ AST & Rule Grounding   │   │ Transformation Proposal Generator    │  │
│  │ (Phase 3 + Phase 4/5)  │───│ (Deterministic Engine + AI Gateway) │  │
│  └───────────────────────┘   └──────────────────┬───────────────────┘  │
│                                                 │                      │
│                                                 ▼                      │
│                              ┌──────────────────────────────────────┐  │
│                              │ Isolated Artifact Storage            │  │
│                              │ storage/modernized/{proj}/{plan_id}/ │  │
│                              └──────────────────┬───────────────────┘  │
│                                                 │                      │
│                                                 ▼                      │
│                              ┌──────────────────────────────────────┐  │
│                              │ Audited Human Review & Diff Viewer   │  │
│                              │ PROPOSED → REVIEWED → APPROVED        │  │
│                              └──────────────────┬───────────────────┘  │
└─────────────────────────────────────────────────┼──────────────────────┘
                                                  │
                                                  ▼
                               ┌─────────────────────────────────────┐
                               │  Phase 9 — Build & Behavioral       │
                               │  Equivalence Validation             │
                               └─────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Original Source Immutability**: Legacy repository code files are never mutated. Modernized artifacts are stored under `storage/modernized/{project_id}/{plan_id}/`.
2. **Deterministic Evidence Primacy**: Transformations inherit exact parameter types, AST method signatures, and Phase 4 business rule logic (validation conditions, thresholds, calculation formulas).
3. **AI Proposal Boundary**: AI generates candidate code snippets strictly within prompt templates supplied with deterministic context. AI cannot invent facts, dependencies, or rules.
4. **State Machine Compliance**: `PROPOSED` → `REVIEWED` → `APPROVED` → `APPLIED` (or `REJECTED`).
5. **No Behavioral Equivalence Claims**: Behavioral validation is strictly deferred to Phase 9.

---

## 3. Transformation Taxonomy & Artifact Model

Phase 8 introduces 7 structured artifact categories generated from Phase 7 task types:

| Artifact Category | Origin Task Types | Description / Target File |
|---|---|---|
| `EXTRACTED_CLASS` | `EXTRACT_RESPONSIBILITY`, `SEPARATE_BUSINESS_RULE`, `EXTRACT_CALCULATION`, `SPLIT_COMPONENT` | Standalone domain service (e.g. `TransferDomainService.java`) |
| `EXTRACTED_INTERFACE` | `DEFINE_INTERFACE` | Clean interface specification (e.g. `TransferService.java`) |
| `FACADE` | `INTRODUCE_FACADE` | Backward-compatible wrapper over legacy component (e.g. `AccountServiceFacade.java`) |
| `ADAPTER` | `INTRODUCE_ADAPTER` | Adapter bridging legacy protocol to modern domain service |
| `REFACTORED_METHOD` | `ISOLATE_PERSISTENCE`, `ISOLATE_STATE_TRANSITION`, `PRESERVE_BEHAVIOR` | Cleaned method implementation with isolated dependencies |
| `MIGRATED_CALLER` | `MIGRATE_CALLER` | Updated caller component delegating to modern service (e.g. `AccountController.java`) |
| `SUPPORTING_TEST_STUB` | `ADD_VERIFICATION_CHECKPOINT` | Unit test stub skeleton linking preserved Phase 4 rules |

---

## 4. State Machine & Review Workflow

```
                        ┌──────────────┐
                        │   PROPOSED   │
                        └──────┬───────┘
                               │
                        (Human Architect Review)
                               │
                               ▼
                        ┌──────────────┐
                        │   REVIEWED   │
                        └──────┬───────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
             (Human Approve)       (Human Reject)
                    │                     │
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │   APPROVED   │      │   REJECTED   │
             └──────┬───────┘      └──────────────┘
                    │
            (Apply Artifact)
                    │
                    ▼
             ┌──────────────┐
             │   APPLIED    │
             └──────────────┘
```

---

## 5. Canonical LegacyBank Transformation Example

### Target Component: `AccountService.processTransfer()`

#### Input: Approved Phase 7 Tasks & Evidence
- **Rule BR-001**: `amount > 50000` (Approval Threshold)
- **Rule BR-002**: `balance < amount` (Insufficient Balance)
- **Rule BR-003**: `fee = amount * 0.02` (Fee Calculation)
- **Rule BR-004**: `account.status == BLOCKED` (Account Status Guard)
- **Impact Surface**: `AccountController.java` caller dependency

#### Output Modernized Artifacts:
1. `TransferDomainService.java` (`EXTRACTED_CLASS`):
   Contains isolated balance check, threshold guard, fee calculation, and state transition logic preserving exact Phase 4 rule expressions.
2. `AccountServiceFacade.java` (`FACADE`):
   Wraps legacy `AccountService` and delegates `processTransfer()` calls to `TransferDomainService`.
3. `AccountController.java` (`MIGRATED_CALLER`):
   Updated controller endpoint delegating directly to `AccountServiceFacade` / `TransferDomainService`.

---

## 6. Security, Storage & Isolated Execution

- **Storage Location**: `backend/storage/modernized/{project_id}/{plan_id}/{artifact_id}/`
- **Path Sanitization**: All file paths derived from artifact proposals are sanitized against directory traversal attacks (`..` rejected).
- **Access Control**: Project-scoped authorization checks enforce that artifacts can only be accessed or modified by authorized project owners.
