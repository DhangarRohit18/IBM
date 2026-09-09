"""
LEGACYX — Mock AI Provider (Phase 4).

Deterministic mock implementation for testing and offline development.
Generates structured explanations strictly based on provided rule context facts.
"""

from typing import Any

from app.ai.base import AIProvider


class MockAIProvider(AIProvider):
    """Offline mock AI provider emitting predictable business explanations."""

    async def explain_business_rule(
        self,
        rule_context: dict[str, Any],
    ) -> str:
        rule_type = rule_context.get("rule_type", "BUSINESS_RULE")
        title = rule_context.get("title", "")
        cond = rule_context.get("condition_expression") or rule_context.get("calculation_formula") or ""
        act = rule_context.get("action_expression") or rule_context.get("outcome_expression") or ""
        thresh = rule_context.get("threshold_value")
        op = rule_context.get("threshold_operator")

        if rule_type == "THRESHOLD" and thresh:
            return (
                f"Business Logic Summary: The application evaluates whether '{cond}' holds. "
                f"When the value exceeds or matches the configured limit of {thresh} (operator {op or 'comparison'}), "
                f"the system triggers action '{act or 'approval routing'}'."
            )
        elif rule_type == "VALIDATION":
            return (
                f"Business Validation Safeguard: Enforces business precondition '{cond}'. "
                f"If this condition fails, the execution is immediately halted with outcome '{act or 'rejection/exception'}', "
                f"preventing unauthorized or invalid operations."
            )
        elif rule_type == "CALCULATION":
            return (
                f"Business Formula Derivation: Calculates financial or operational output according to formula '{cond}'. "
                f"This derivation establishes the resulting value used in downstream transactions."
            )
        elif rule_type == "STATE_TRANSITION":
            new_st = rule_context.get("new_state", "UPDATED")
            prev_st = rule_context.get("previous_state") or "UNKNOWN"
            return (
                f"Business Lifecycle State Transition: Updates entity state from {prev_st} to {new_st} "
                f"upon satisfying control flow evaluation '{cond or 'transaction completion'}'."
            )
        else:
            return (
                f"Business Decision Rule: Evaluates conditional logic '{cond}'. "
                f"Upon evaluation, the system executes action '{act or 'further processing'}'."
            )

    async def explain_impact(
        self,
        impact_context: dict[str, Any],
    ) -> str:
        target_name = impact_context.get("target_name", "Target Component")
        direction = impact_context.get("direction", "forward")
        direct_comps = impact_context.get("direct_components", [])
        transitive_comps = impact_context.get("transitive_components", [])
        direct_rules = impact_context.get("direct_rules", [])

        if not direct_comps and not transitive_comps and not direct_rules:
            return f"Impact Assessment for '{target_name}': No static dependencies or business rules are affected within depth={impact_context.get('max_depth', 3)}."

        dir_desc = "depend on" if direction == "reverse" else "are depended upon by"
        explanation = (
            f"Impact Narrative for '{target_name}': Modifying this component will directly affect "
            f"{len(direct_comps)} component(s) that {dir_desc} it ({', '.join(c.get('name', '') for c in direct_comps[:3])}). "
            f"Additionally, {len(direct_rules)} business rule(s) contained within or linked to these components will require regression verification."
        )
        if transitive_comps:
            explanation += f" Indirect ripple effects extend to {len(transitive_comps)} downstream component(s)."
        return explanation

    async def explain_strategy(
        self,
        strategy_context: dict[str, Any],
    ) -> str:
        target_name = strategy_context.get("target_name", "Target Component")
        rec_strat = strategy_context.get("recommended_strategy", "MODULARIZE")
        why = strategy_context.get("why_recommended", "")
        rule_count = len(strategy_context.get("rules_to_preserve", []))
        resp_count = len(strategy_context.get("observed_responsibilities", []))

        return (
            f"Modernization Strategy Rationale for '{target_name}': The recommended strategy is '{rec_strat}'. "
            f"Static analysis discovered {resp_count} distinct AST responsibility signals and {rule_count} business rules that must be preserved. "
            f"{why}"
        )

    async def explain_plan(
        self,
        plan_context: dict[str, Any],
    ) -> str:
        entity_name = plan_context.get("entity_name", "Target Component")
        strat_type = plan_context.get("strategy_type", "MODULARIZE")
        task_count = len(plan_context.get("tasks", []))
        rule_count = len(plan_context.get("rules_to_preserve", []))
        checkpoint_count = len(plan_context.get("verification_checkpoints", []))

        return (
            f"Modernization Plan Narrative for '{entity_name}': Executes an evidence-backed {strat_type} plan comprising "
            f"{task_count} topologically ordered execution tasks. The plan guarantees 100% invariant preservation for {rule_count} "
            f"business rules while attaching {checkpoint_count} deterministic verification checkpoints."
        )

    async def generate_code_proposal(
        self,
        transformation_context: dict[str, Any],
    ) -> str:
        entity_name = transformation_context.get("entity_name", "Target")
        task_title = transformation_context.get("title", "Transformation Step")
        category = transformation_context.get("artifact_category", "EXTRACTED_CLASS")
        rule_count = len(transformation_context.get("rules_to_preserve", []))

        return (
            f"// AI Candidate Transformation Proposal\n"
            f"// Target Entity: {entity_name}\n"
            f"// Task: {task_title}\n"
            f"// Category: {category}\n"
            f"// Grounded Preserved Rules: {rule_count}\n"
            f"// Note: Candidate proposal strictly derived from static evidence specifications.\n"
        )

    async def explain_validation_evidence(
        self,
        validation_context: dict[str, Any],
    ) -> str:
        build_st = validation_context.get("build_status", "UNKNOWN")
        test_st = validation_context.get("test_status", "UNKNOWN")
        beh_st = validation_context.get("behavioral_status", "UNKNOWN")
        overall_st = validation_context.get("overall_status", "UNKNOWN")
        passed = validation_context.get("passed_scenarios", 0)
        total = validation_context.get("total_scenarios", 0)
        failed_brs = validation_context.get("failed_business_rules", [])

        if overall_st == "VERIFIED":
            return (
                f"Empirical Validation Explanation: The modernization artifact successfully achieved "
                f"Build Status '{build_st}', Unit Test Status '{test_st}', and Behavioral Equivalence '{beh_st}'. "
                f"All {total} authoritative business rule scenarios passed without mismatch."
            )
        elif overall_st == "FAILED":
            fail_msg = f" Failing business rules: {', '.join(failed_brs)}." if failed_brs else ""
            return (
                f"Empirical Validation Mismatch Explanation: Validation failed with overall status '{overall_st}'. "
                f"Build: '{build_st}', Test: '{test_st}', Behavioral Equivalence: '{beh_st}'. "
                f"Scenario outcomes: {passed}/{total} passed.{fail_msg}"
            )
        else:
            return (
                f"Empirical Validation Diagnostics: Execution run completed with overall status '{overall_st}'. "
                f"Build Status: '{build_st}', Test Status: '{test_st}', Behavioral Equivalence: '{beh_st}'."
            )



