# ADR-008 — Business Logic Recovery via Deterministic Static Extraction & AI Explanation

**Status:** Accepted  
**Date:** Phase 4  
**Deciders:** Project Lead  

---

## Context

LEGACYX requires extracting business rules (validations, thresholds, calculations, actions, state transitions) encoded inside legacy applications.

Two approaches were evaluated:

**Option A — AI-First Rule Extraction:**  
Send raw source files to an LLM/AI provider and ask it to list the business rules.

**Option B — Deterministic Static Extraction + AI Gateway Explanation (Chosen):**  
Use static AST pattern analysis to extract all facts (conditions, thresholds, formulas, state mutations, file locations, line numbers). Store deterministic facts as the authoritative source of truth. Use the central AI Gateway ONLY to produce supplementary human-readable explanations.

---

## Decision

LEGACYX adopts **Option B — Deterministic Static Extraction + AI Gateway Explanation.**

### Key Rules
1. **AI Output is Never a Fact**: Facts (conditions, thresholds, line numbers) must be proven by deterministic AST extraction.
2. **Deduplication & Grouping**: Related facts extracted from the same control flow site are grouped into single business rule candidates to prevent duplication.
3. **Conservative State Inference**: Previous states in state transitions must remain `UNKNOWN` (`None`) unless proven by static evidence.
4. **Symbolic & Literal Threshold Support**: Threshold extraction supports both constant literals (`50000`) and symbolic constant references (`MAX_TRANSFER_LIMIT`).
5. **No Numeric Accuracy/Confidence Scores**: Rules rely on empirical facts and source line evidence, not invented percentage scores.

---

## Consequences

- `backend/app/models/business_rule.py` defines the `BusinessRule` entity storing deterministic facts separately from `ai_explanation`.
- `backend/app/analysis_engine/rule_extractor.py` implements pure AST pattern extraction.
- `backend/app/ai/` provides lightweight `MockProvider` and `WatsonxProvider` options behind `AIGateway`.
- If an AI call fails, the rule candidate remains valid with its deterministic facts.
