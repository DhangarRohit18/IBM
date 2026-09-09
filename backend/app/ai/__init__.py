"""
LEGACYX — AI Gateway Package (Phase 4).

All AI provider calls must go through this gateway (AGENTS.md §3.1, ADR-005).
No service, route, or analysis module may call an AI provider directly.
"""

from app.ai.base import AIProvider
from app.ai.gateway import AIGateway, ai_gateway
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.watsonx_provider import WatsonxProvider

__all__ = [
    "AIProvider",
    "AIGateway",
    "ai_gateway",
    "MockAIProvider",
    "WatsonxProvider",
]
