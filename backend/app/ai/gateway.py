"""
LEGACYX — Central AI Gateway Abstraction (Phase 4).

All AI provider calls must go through this gateway (AGENTS.md §3.1, ADR-005).
No route or service module may import AI SDKs directly.
Enforces:
1. Secret and credential redaction (AGENTS.md §7.1).
2. Strict isolation: AI output is supplementary explanation only (ADR-008).
3. Failure isolation: AI timeout/error leaves deterministic facts valid.
"""

import os
import re
from typing import Any

from app.ai.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.watsonx_provider import WatsonxProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIGateway:
    """Central AI Gateway Singleton."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        if provider:
            self._provider = provider
        else:
            provider_type = os.getenv("AI_PROVIDER", "mock").lower()
            if provider_type == "watsonx":
                self._provider = WatsonxProvider()
            else:
                self._provider = MockAIProvider()

    def get_provider(self) -> AIProvider:
        return self._provider

    async def generate_rule_explanation(self, rule_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI explanation for structured deterministic rule context.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, explanation_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(rule_context)
        try:
            logger.info("ai_gateway.explaining_rule", rule_type=sanitized_context.get("rule_type"))
            explanation = await self._provider.explain_business_rule(sanitized_context)
            return True, explanation
        except Exception as exc:
            logger.error("ai_gateway.explanation_failed", error=str(exc))
            return False, f"AI Explanation unavailable: {str(exc)}"

    async def generate_impact_explanation(self, impact_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI explanation for established deterministic impact analysis facts.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, explanation_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(impact_context)
        try:
            logger.info("ai_gateway.explaining_impact", target=sanitized_context.get("target_name"))
            explanation = await self._provider.explain_impact(sanitized_context)
            return True, explanation
        except Exception as exc:
            logger.error("ai_gateway.impact_explanation_failed", error=str(exc))
            return False, f"AI Impact Explanation unavailable: {str(exc)}"

    async def generate_strategy_explanation(self, strategy_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI explanation for established deterministic modernization strategy facts.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, explanation_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(strategy_context)
        try:
            logger.info("ai_gateway.explaining_strategy", target=sanitized_context.get("target_name"))
            explanation = await self._provider.explain_strategy(sanitized_context)
            return True, explanation
        except Exception as exc:
            logger.error("ai_gateway.strategy_explanation_failed", error=str(exc))
            return False, f"AI Strategy Explanation unavailable: {str(exc)}"

    async def generate_plan_explanation(self, plan_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI explanation for established deterministic modernization plan facts.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, explanation_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(plan_context)
        try:
            logger.info("ai_gateway.explaining_plan", entity=sanitized_context.get("entity_name"))
            explanation = await self._provider.explain_plan(sanitized_context)
            return True, explanation
        except Exception as exc:
            logger.error("ai_gateway.plan_explanation_failed", error=str(exc))
            return False, f"AI Plan Explanation unavailable: {str(exc)}"

    async def generate_code_proposal(self, transformation_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI candidate code proposal for established transformation context.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, code_proposal_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(transformation_context)
        try:
            logger.info("ai_gateway.proposing_code", target=sanitized_context.get("entity_name"))
            proposal = await self._provider.generate_code_proposal(sanitized_context)
            return True, proposal
        except Exception as exc:
            logger.error("ai_gateway.code_proposal_failed", error=str(exc))
            return False, f"AI Code Proposal unavailable: {str(exc)}"

    async def generate_validation_explanation(self, validation_context: dict[str, Any]) -> tuple[bool, str]:
        """
        Requests an AI explanation for established empirical validation evidence facts.
        Redacts sensitive tokens/secrets before calling provider.
        Returns (success: bool, explanation_or_error: str).
        """
        sanitized_context = self._redact_secrets_from_context(validation_context)
        try:
            logger.info("ai_gateway.explaining_validation", overall_status=sanitized_context.get("overall_status"))
            explanation = await self._provider.explain_validation_evidence(sanitized_context)
            return True, explanation
        except Exception as exc:
            logger.error("ai_gateway.validation_explanation_failed", error=str(exc))
            return False, f"AI Validation Explanation unavailable: {str(exc)}"



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
