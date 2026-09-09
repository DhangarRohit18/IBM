# ADR-001 — Deterministic Analysis + AI Reasoning Rather Than AI-Only Analysis

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

When analyzing a legacy codebase, two approaches are possible:

**Option A — AI-Only Analysis:**  
Feed the source code directly to a language model and ask it to describe the architecture, dependencies, business rules, and migration strategy.

**Option B — Deterministic Analysis + AI Reasoning:**  
Use static analysis tools to extract verifiable facts from the code (files, classes, methods, imports, dependencies, call relationships, database interactions, API endpoints). Then use AI to reason over those facts (explain architecture, summarize business logic, recommend strategies).

---

## Decision

LEGACYX uses **Option B — Deterministic Analysis + AI Reasoning**.

---

## Rationale

### 1. Language Models Hallucinate on Source Code

AI models can produce plausible but incorrect descriptions of code. A model might:
- Claim a class depends on another class that does not exist.
- Claim a method calls a function that is not present in the codebase.
- Claim a test passed without any execution.
- Describe business logic that is not actually encoded in the source.

In the context of legacy modernization, these errors are dangerous. A migration plan built on incorrect dependency information can break production systems.

### 2. Deterministic Analysis Produces Reproducible, Verifiable Results

Given the same source code, static analysis produces the same results. Results can be:
- Stored with their source (file path, line number).
- Traced back to the analysis run that produced them.
- Verified independently by a human reading the source.
- Compared across runs to detect changes.

This is not possible with AI-only analysis.

### 3. AI Adds Value at the Reasoning Level, Not the Fact Level

AI is genuinely useful for:
- Explaining what a class does in human-readable terms.
- Summarizing a dependency graph.
- Recommending a modernization strategy.
- Generating a migration plan from known facts.
- Explaining why a behavioral test failed.

All of these tasks are higher-level reasoning that benefits from language model capabilities — but they should always be grounded in verified facts.

### 4. Trust and Auditability

In an engineering governance context, every claim must be traceable to evidence. "The AI said so" is not acceptable as source evidence for a migration decision. "The static analyzer found this in file X at line Y" is.

---

## Consequences

- The deterministic analysis engine is the highest-priority component of LEGACYX.
- AI capabilities must always receive analysis results as input, not raw source code alone.
- AI output must always be labelled as AI-generated in the UI and stored separately from deterministic facts.
- The analysis engine and AI gateway must remain logically independent.
