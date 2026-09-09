# ADR-005 — AI Providers Abstracted Behind an AI Gateway

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

LEGACYX requires AI capabilities at multiple points: explaining business rules, recommending strategies, generating migration plans, transforming code, generating tests, and explaining validation failures.

Two implementation approaches:

**Option A — Direct provider calls:**  
Call the AI provider (IBM watsonx, OpenAI, etc.) directly from service classes or routes, with provider-specific code scattered across the codebase.

**Option B — AI gateway abstraction:**  
Define a provider-agnostic `AIProvider` abstract interface with capability methods. Implement each provider behind this interface. Route all AI calls through a central `AIGateway`. No provider-specific code outside `backend/app/ai/providers/`.

---

## Decision

LEGACYX uses **Option B — AI Gateway abstraction.**

---

## Rationale

### 1. IBM watsonx is the Hackathon Target, But Must Not Be Hardcoded

IBM Bob (watsonx) is the intended AI integration for the hackathon. However, if the provider is hardcoded throughout the codebase:
- Switching providers (for testing, fallback, or future business decisions) requires changes across many files.
- Testing individual services requires mocking a specific provider SDK.
- The coupling to a commercial AI API makes the codebase fragile.

### 2. Provider-Specific Code Has a Specific Risk Profile

AI provider calls:
- Make network requests to external services (latency, outages)
- May transmit sensitive source code (must be controlled)
- Have rate limits and cost implications
- Return non-deterministic outputs

All of these risks must be managed in one place, not scattered across dozens of service files.

### 3. The Gateway Can Enforce Safety Rules Centrally

The AI gateway is the correct place to enforce:
- Secret redaction before source fragments are sent to the provider
- Prompt template versioning
- Response storage alongside the analysis results that prompted them
- AI output labelling (ensuring responses are stored as `ai_generated: true`)
- Rate limiting, retries, and circuit breaking

### 4. Capability Orientation, Not Model Orientation

The abstraction defines capabilities (`explain_business_rule`, `recommend_strategy`, `transform_code`) rather than model calls. This means the gateway can route different capabilities to different models or providers if that is ever useful — without touching downstream service code.

---

## Consequences

- `backend/app/ai/base.py` must define the `AIProvider` abstract base class with all required capability methods.
- `backend/app/ai/gateway.py` must be the only import point for AI functionality in service code.
- `backend/app/ai/providers/` may contain multiple implementations. Only one per capability is active at runtime, determined by configuration.
- No service, route, or analysis module may import directly from a provider SDK.
- For testing, a `MockAIProvider` implementation must be available for unit tests that do not require real AI responses.
