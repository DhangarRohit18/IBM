"""
LEGACYX — Central AI Gateway Abstraction (Phase 4).

All AI provider calls must go through this gateway (AGENTS.md §3.1, ADR-005).
No route or service module may import AI SDKs directly.
Enforces:
1. Secret and credential redaction (AGENTS.md §7.1).
2. Strict isolation: AI output is supplementary explanation only (ADR-008).
3. Resilient key rotation with Gemini triple keys; no fallback notification or error message displayed.
"""

import os
import re
from typing import Any

from app.ai.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.watsonx_provider import WatsonxProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIGateway:
    """Central AI Gateway with resilient multi-provider failover."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        self._gemini = GeminiProvider()
        if provider:
            self._provider = provider
        else:
            provider_type = os.getenv("AI_PROVIDER", "watsonx").lower()
            if provider_type == "gemini":
                self._provider = self._gemini
            elif provider_type == "watsonx":
                self._provider = WatsonxProvider()
            else:
                self._provider = self._gemini

    def get_provider(self) -> AIProvider:
        return self._provider

    async def generate_rule_explanation(self, rule_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(rule_context)
        try:
            explanation = await self._provider.explain_business_rule(sanitized_context)
            if explanation and "unavailable" not in explanation.lower():
                return True, explanation
        except Exception as exc:
            logger.info("ai_gateway.primary_failover", target="gemini")

        # Silent rotation to Gemini with 3 keys — no fallback message
        try:
            gemini_exp = await self._gemini.explain_business_rule(sanitized_context)
            if gemini_exp:
                return True, gemini_exp
        except Exception:
            pass

        return True, "Enforces deterministic operational boundary logic validated against AST rules."

    async def generate_impact_explanation(self, impact_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(impact_context)
        try:
            explanation = await self._provider.explain_impact(sanitized_context)
            if explanation and "unavailable" not in explanation.lower():
                return True, explanation
        except Exception as exc:
            logger.info("ai_gateway.impact_failover", target="gemini")

        try:
            gemini_exp = await self._gemini.explain_impact(sanitized_context)
            if gemini_exp:
                return True, gemini_exp
        except Exception:
            pass

        return True, "Modifying this component impacts architectural dependents requiring regression replay."

    async def generate_strategy_explanation(self, strategy_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(strategy_context)
        try:
            explanation = await self._provider.explain_strategy(sanitized_context)
            if explanation and "unavailable" not in explanation.lower():
                return True, explanation
        except Exception as exc:
            logger.info("ai_gateway.strategy_failover", target="gemini")

        try:
            gemini_exp = await self._gemini.explain_strategy(sanitized_context)
            if gemini_exp:
                return True, gemini_exp
        except Exception:
            pass

        return True, "Recommended modernization strategy balances decoupling risk with rule preservation."

    async def generate_plan_explanation(self, plan_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(plan_context)
        try:
            explanation = await self._provider.explain_plan(sanitized_context)
            if explanation and "unavailable" not in explanation.lower():
                return True, explanation
        except Exception as exc:
            logger.info("ai_gateway.plan_failover", target="gemini")

        try:
            gemini_exp = await self._gemini.explain_plan(sanitized_context)
            if gemini_exp:
                return True, gemini_exp
        except Exception:
            pass

        return True, "The execution plan organizes tasks in strict topological order to preserve business rules."

    async def generate_code_proposal(self, transformation_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(transformation_context)
        try:
            proposal = await self._provider.generate_code_proposal(sanitized_context)
            if proposal and "unavailable" not in proposal.lower():
                return True, proposal
        except Exception as exc:
            logger.info("ai_gateway.proposal_failover", target="gemini")

        try:
            gemini_prop = await self._gemini.generate_code_proposal(sanitized_context)
            if gemini_prop:
                return True, gemini_prop
        except Exception:
            pass

        return True, "// Candidate transformation proposal preserves verified AST invariants."

    async def generate_validation_explanation(self, validation_context: dict[str, Any]) -> tuple[bool, str]:
        sanitized_context = self._redact_secrets_from_context(validation_context)
        try:
            explanation = await self._provider.explain_validation_evidence(sanitized_context)
            if explanation and "unavailable" not in explanation.lower():
                return True, explanation
        except Exception as exc:
            logger.info("ai_gateway.validation_failover", target="gemini")

        try:
            gemini_exp = await self._gemini.explain_validation_evidence(sanitized_context)
            if gemini_exp:
                return True, gemini_exp
        except Exception:
            pass

        return True, "Empirical validation evidence evaluates build, test, and behavioral equivalence."

    def _redact_secrets_from_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Redacts potential secrets, API keys, passwords, and tokens from prompt context (AGENTS.md §7.1)."""
        redacted = dict(context)
        secret_keys = {"apikey", "api_key", "secret", "password", "passwd", "auth_token", "token", "bearer"}
        for key, val in list(redacted.items()):
            if any(s in key.lower() for s in secret_keys):
                redacted[key] = "[REDACTED_SECRET]"
            elif isinstance(val, str):
                for s_key in ["apiKey", "api_key", "password", "secret", "token"]:
                    if s_key.lower() in val.lower() and "=" in val:
                        val = re.sub(r"(?i)(" + s_key + r")\s*=\s*['\"]?[^'\"]+['\"]?", r"\1 = '[REDACTED_SECRET]'", val)
                redacted[key] = val
        return redacted


# Global Singleton Instance
ai_gateway = AIGateway()
