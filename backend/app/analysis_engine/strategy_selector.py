"""
LEGACYX — Deterministic Modernization Strategy Selector Engine (Phase 6).

Consumes:
- System X-Ray (Phase 3 entities & classification)
- Business Logic Recovery (Phase 4 rules to preserve)
- Impact Analysis (Phase 5 direct & transitive impact surface)
- AST Responsibilities (Phase 6 responsibility signals)

Produces:
- Recommended Strategy & Alternative Strategy
- Decision Trace (Fact -> Implication -> Consideration -> Strategy)
- Preserved Business Rules List
- Impact Surface Summary
- Qualitative Comparative Dimensions (Zero Fake Scores)
- Insufficient Evidence Handling
"""

import enum
from typing import Any


class ModernizationStrategyType(str, enum.Enum):
    MODULARIZE = "MODULARIZE"
    EXTRACT_SERVICE = "EXTRACT_SERVICE"
    STRANGLER = "STRANGLER"
    REFACTOR_IN_PLACE = "REFACTOR_IN_PLACE"
    ADAPTER = "ADAPTER"
    ANTI_CORRUPTION_LAYER = "ANTI_CORRUPTION_LAYER"
    RETAIN_AND_WRAP = "RETAIN_AND_WRAP"
    NO_MODERNIZATION_NEEDED = "NO_MODERNIZATION_NEEDED"


class StrategySelector:
    """Evaluates candidate component evidence and computes deterministic modernization strategies."""

    def select_strategy(
        self,
        entity_name: str,
        entity_type: str,
        component_type: str,
        relative_file_path: str,
        responsibilities: list[dict[str, Any]],
        business_rules: list[dict[str, Any]],
        impact_summary: dict[str, Any],
        direct_dependents: list[dict[str, Any]],
        transitive_dependents: list[dict[str, Any]],
    ) -> dict[str, Any]:
        resp_count = len(responsibilities)
        rule_count = len(business_rules)
        direct_dep_count = len(direct_dependents)
        trans_dep_count = len(transitive_dependents)

        rec_strategy = ModernizationStrategyType.RETAIN_AND_WRAP
        alt_strategy: ModernizationStrategyType | None = None
        why_recommended = ""
        why_alternative = ""
        what_not_to_change = ""

        # 1. Evaluate Strategy Selection Rules
        if component_type in ["MODEL", "CONFIG", "UTILITY", "OTHER"] and rule_count == 0 and resp_count <= 1:
            rec_strategy = ModernizationStrategyType.NO_MODERNIZATION_NEEDED
            alt_strategy = None
            why_recommended = (
                f"'{entity_name}' is classified as a {component_type} with single responsibility and zero business rules. "
                "No architectural refactoring or service extraction is required."
            )
            what_not_to_change = "Do not split or alter the clean DTO/Utility structure."

        elif resp_count >= 4 and direct_dep_count <= 3:
            rec_strategy = ModernizationStrategyType.MODULARIZE
            alt_strategy = ModernizationStrategyType.STRANGLER
            why_recommended = (
                f"'{entity_name}' aggregates {resp_count} distinct AST responsibilities (validation, fee calculation, persistence, state mutation). "
                f"Decomposing into modular domain helpers within the current deployment boundary minimizes risk while eliminating internal class bloat."
            )
            why_alternative = (
                "STRANGLER is a viable alternative if you intend to replace the legacy component incrementally via gateway interception."
            )
            what_not_to_change = "Keep external API endpoint contracts and repository schemas unchanged during internal modularization."

        elif resp_count >= 3 and rule_count >= 3 and direct_dep_count > 2 and trans_dep_count <= 5:
            rec_strategy = ModernizationStrategyType.EXTRACT_SERVICE
            alt_strategy = ModernizationStrategyType.MODULARIZE
            why_recommended = (
                f"'{entity_name}' encapsulates a distinct business domain containing {rule_count} business rules and {direct_dep_count} direct consumers. "
                "Extracting into a standalone microservice provides process isolation and independent scalability."
            )
            why_alternative = "MODULARIZE keeps deployment simpler by splitting classes inside the existing monolith process."
            what_not_to_change = "Retain legacy database tables and dual-read endpoints until service migration validation completes."

        elif resp_count >= 3 and trans_dep_count > 5:
            rec_strategy = ModernizationStrategyType.STRANGLER
            alt_strategy = ModernizationStrategyType.RETAIN_AND_WRAP
            why_recommended = (
                f"'{entity_name}' has a broad downstream ripple impact ({trans_dep_count} transitive dependents). "
                "Big-bang replacement presents unacceptable regression risk. Incremental Strangler proxy interception is recommended."
            )
            why_alternative = "RETAIN_AND_WRAP preserves legacy code 100% intact while wrapping it in a new clean facade."
            what_not_to_change = "Do not rewrite underlying legacy execution paths until proxy traffic routing is verified."

        elif resp_count <= 2 and rule_count <= 2 and direct_dep_count <= 2:
            rec_strategy = ModernizationStrategyType.REFACTOR_IN_PLACE
            alt_strategy = ModernizationStrategyType.RETAIN_AND_WRAP
            why_recommended = (
                f"'{entity_name}' has localized responsibility ({resp_count} observed signals) and low external coupling ({direct_dep_count} direct dependents). "
                "Refactoring in place to clean up code smells and expand unit test coverage is optimal."
            )
            why_alternative = "RETAIN_AND_WRAP can be used if zero line edits to legacy code are permitted."
            what_not_to_change = "Do not alter method signatures or throw signatures consumed by callers."

        else:
            # Insufficient evidence / Default safe case
            rec_strategy = ModernizationStrategyType.RETAIN_AND_WRAP
            alt_strategy = ModernizationStrategyType.REFACTOR_IN_PLACE
            why_recommended = (
                f"Static analysis evidence for '{entity_name}' indicates insufficient architectural decoupling benefits. "
                "Preserving the original legacy component intact and wrapping it with a clean interface facade minimizes regression risk."
            )
            why_alternative = "REFACTOR_IN_PLACE can be considered if unit test coverage is comprehensive."
            what_not_to_change = "Do not edit original source code without explicit behavioral test harnesses."

        # 2. Build Decision Trace
        decision_trace = [
            {
                "step": 1,
                "label": "Observed Facts",
                "detail": f"Component '{entity_name}' ({component_type}) contains {resp_count} AST responsibility signals, {rule_count} business rules, and {direct_dep_count} direct dependents.",
            },
            {
                "step": 2,
                "label": "Architectural Implication",
                "detail": (
                    f"Component aggregates multiple domain concerns." if resp_count >= 3
                    else "Component exhibits localized responsibility boundary."
                ),
            },
            {
                "step": 3,
                "label": "Impact Considerations",
                "detail": f"Downstream impact surface spans {direct_dep_count} direct and {trans_dep_count} transitive dependent components.",
            },
            {
                "step": 4,
                "label": "Strategy Recommendation",
                "detail": f"Concluded Strategy: {rec_strategy.value}." + (f" Alternative: {alt_strategy.value}." if alt_strategy else ""),
            },
        ]

        # 3. Rules to Preserve List
        rules_to_preserve = [
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "rule_type": r.get("rule_type"),
                "file_path": r.get("relative_file_path"),
                "line_start": r.get("line_start"),
                "condition": r.get("condition_expression"),
            }
            for r in business_rules
        ]

        # 4. Qualitative Comparison (Zero Fake Scores)
        qualitative_comparison = []
        if alt_strategy:
            qualitative_comparison = [
                {
                    "dimension": "Deployment Boundary",
                    "recommended_value": "Keeps existing deployment unit",
                    "alternative_value": "Requires new standalone deployment unit" if alt_strategy == ModernizationStrategyType.EXTRACT_SERVICE else "Monolith proxy routing",
                },
                {
                    "dimension": "Responsibility Coupling",
                    "recommended_value": "Eliminates internal class bloat",
                    "alternative_value": "Provides process memory isolation",
                },
                {
                    "dimension": "Business Rule Risk",
                    "recommended_value": "Preserves rules under existing test harnesses",
                    "alternative_value": "Requires dual-run validation before cutover",
                },
                {
                    "dimension": "Coexistence Overhead",
                    "recommended_value": "Zero coexistence overhead",
                    "alternative_value": "Requires strangler proxy & traffic router",
                },
            ]

        return {
            "target_name": entity_name,
            "target_type": entity_type,
            "component_type": component_type,
            "relative_file_path": relative_file_path,
            "recommended_strategy": rec_strategy.value,
            "alternative_strategy": alt_strategy.value if alt_strategy else None,
            "why_recommended": why_recommended,
            "why_alternative": why_alternative,
            "what_not_to_change": what_not_to_change,
            "decision_trace": decision_trace,
            "observed_responsibilities": responsibilities,
            "rules_to_preserve": rules_to_preserve,
            "impact_summary": {
                "direct_dependent_count": direct_dep_count,
                "transitive_dependent_count": trans_dep_count,
                "direct_dependents": [d.get("name") for d in direct_dependents[:5]],
                "transitive_dependents": [d.get("name") for d in transitive_dependents[:5]],
            },
            "qualitative_comparison": qualitative_comparison,
        }


strategy_selector = StrategySelector()
