"""
LEGACYX — AI Provider Base Abstract Class (Phase 4).

Defines the capabilities interface for AI Gateway providers (AGENTS.md §3.1, ADR-005).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AIProvider(ABC):
    """Abstract base class for all AI Gateway provider implementations."""

    @abstractmethod
    async def explain_business_rule(
        self,
        rule_context: dict[str, Any],
    ) -> str:
        """
        Translates structured deterministic rule facts into a clear, human-readable business explanation.
        Must NOT invent new facts, thresholds, conditions, or actions not in rule_context.
        """
        pass

    @abstractmethod
    async def explain_impact(
        self,
        impact_context: dict[str, Any],
    ) -> str:
        """
        Explains established impact paths and affected business rules in plain natural language.
        Must NOT invent relationships, components, or impacts not present in impact_context.
        """
        pass

    @abstractmethod
    async def explain_strategy(
        self,
        strategy_context: dict[str, Any],
    ) -> str:
        """
        Explains an established modernization strategy recommendation and decision trace in plain language.
        Must NOT invent new dependencies, business rules, or alternative strategy recommendations.
        """
        pass

    @abstractmethod
    async def explain_plan(
        self,
        plan_context: dict[str, Any],
    ) -> str:
        """
        Explains an established modernization execution plan, ordered tasks, and preservation rules in plain language.
        Must NOT invent new tasks, reorder tasks, or invent business rules.
        """
        pass

    @abstractmethod
    async def generate_code_proposal(
        self,
        transformation_context: dict[str, Any],
    ) -> str:
        """
        Generates candidate code proposals for an established transformation specification.
        Must NOT invent business rules, dependencies, or alter target file paths/types.
        """
        pass

    @abstractmethod
    async def explain_validation_evidence(
        self,
        validation_context: dict[str, Any],
    ) -> str:
        """
        Explains established empirical validation evidence (build, test, behavioral equivalence match/mismatch).
        Must NOT claim verification without evidence or invent fake test results.
        """
        pass



