"""
LEGACYX — Deterministic Business Rule Extractor (Phase 4).

Extracts explainable business rules from Java ASTs without AI inference.
Guarantees:
1. Pure static AST pattern matching (reusing Phase 3 javalang ASTs).
2. Actions promoted only when in business control flow / condition / state context.
3. Thresholds support literals & symbolic constant references.
4. State transitions never invent previous states (remain None/UNKNOWN unless proven).
5. Rule Trace: Condition -> Decision Context -> Action -> State Change.
6. Deterministic deduplication of facts extracted from the same control flow site.
7. Zero confidence score percentages.
"""

from typing import Any, Optional
import javalang
from javalang.tree import (
    Assignment,
    BinaryOperation,
    ClassDeclaration,
    IfStatement,
    Literal,
    LocalVariableDeclaration,
    MemberReference,
    MethodDeclaration,
    MethodInvocation,
    ReturnStatement,
    SwitchStatement,
    ThrowStatement,
)

from app.models.business_rule import BusinessRule, RuleStatus, RuleType


class BusinessRuleExtractor:
    """
    Deterministic AST Extractor for Java Business Rules.
    Operates on javalang AST nodes.
    """

    def extract_rules_from_ast(
        self,
        analysis_id: str,
        repository_id: str,
        entity_id: Optional[str],
        method_id: Optional[str],
        relative_file_path: str,
        ast_tree: javalang.tree.CompilationUnit,
        file_lines: list[str],
    ) -> list[dict[str, Any]]:
        """
        Walks AST tree and extracts candidate business rules.
        Returns a list of dictionary kwarg payloads for BusinessRule model creation.
        """
        raw_candidates: list[dict[str, Any]] = []

        if not ast_tree or not hasattr(ast_tree, "types"):
            return []

        # 1. Validation & Threshold & Conditional Rules from IfStatements
        for path, node in ast_tree.filter(IfStatement):
            line_no = getattr(node.position, "line", 1)
            rules = self._extract_if_statement_rules(
                analysis_id=analysis_id,
                repository_id=repository_id,
                entity_id=entity_id,
                method_id=method_id,
                relative_file_path=relative_file_path,
                if_node=node,
                line_no=line_no,
                file_lines=file_lines,
            )
            raw_candidates.extend(rules)

        # 2. Calculation Rules from Assignments
        for path, node in ast_tree.filter(Assignment):
            line_no = getattr(node.position, "line", 1)
            rule = self._extract_assignment_rule(
                analysis_id=analysis_id,
                repository_id=repository_id,
                entity_id=entity_id,
                method_id=method_id,
                relative_file_path=relative_file_path,
                target_var=self._reconstruct_expression(node.expressionl),
                value_node=node.value,
                line_no=line_no,
                file_lines=file_lines,
            )
            if rule:
                raw_candidates.append(rule)

        # 3. Calculation Rules from LocalVariableDeclarations (e.g. double fee = amount * 0.02)
        for path, node in ast_tree.filter(LocalVariableDeclaration):
            line_no = getattr(node.position, "line", 1)
            for decl in node.declarators or []:
                if decl.initializer and isinstance(decl.initializer, BinaryOperation):
                    rule = self._extract_assignment_rule(
                        analysis_id=analysis_id,
                        repository_id=repository_id,
                        entity_id=entity_id,
                        method_id=method_id,
                        relative_file_path=relative_file_path,
                        target_var=decl.name,
                        value_node=decl.initializer,
                        line_no=line_no,
                        file_lines=file_lines,
                    )
                    if rule:
                        raw_candidates.append(rule)

        # 4. State Transitions from standalone MethodInvocations (e.g. setStatus(COMPLETED))
        for path, node in ast_tree.filter(MethodInvocation):
            line_no = getattr(node.position, "line", 1)
            m_name = node.member
            if m_name.startswith("set") and len(node.arguments) > 0 and ("status" in m_name.lower() or "state" in m_name.lower()):
                val_arg = self._reconstruct_expression(node.arguments[0])
                rule_trace = [
                    {"step_type": "DECISION_CONTEXT", "label": "Direct State Transition", "details": f"Line {line_no}", "line_number": line_no},
                    {"step_type": "STATE_CHANGE", "label": f"Transition state: UNKNOWN -> {val_arg}", "details": f"New: {val_arg}", "line_number": line_no},
                ]
                raw_candidates.append({
                    "analysis_id": analysis_id,
                    "repository_id": repository_id,
                    "entity_id": entity_id,
                    "method_id": method_id,
                    "rule_type": RuleType.STATE_TRANSITION,
                    "title": f"State Transition: -> {val_arg}",
                    "status": RuleStatus.EXTRACTED,
                    "previous_state": None,
                    "new_state": val_arg,
                    "rule_trace": rule_trace,
                    "relative_file_path": relative_file_path,
                    "line_start": line_no,
                    "line_end": line_no,
                    "source_construct": "method_invocation",
                    "extraction_reason": f"State transition setter call ({m_name}) at line {line_no}",
                })

        # Deduplicate & group candidates
        return self._deduplicate_candidates(raw_candidates)

    def _extract_if_statement_rules(
        self,
        analysis_id: str,
        repository_id: str,
        entity_id: Optional[str],
        method_id: Optional[str],
        relative_file_path: str,
        if_node: IfStatement,
        line_no: int,
        file_lines: list[str],
    ) -> list[dict[str, Any]]:
        rules: list[dict[str, Any]] = []

        cond_expr = self._reconstruct_expression(if_node.condition)
        source_line = self._get_source_line(file_lines, line_no)

        # Check for Validation Rule (if condition throws exception or returns rejection)
        outcome = None
        has_throw = False

        if if_node.then_statement:
            for path, sub in javalang.ast.Node.filter(if_node.then_statement, ThrowStatement):
                has_throw = True
                outcome = "Reject: throws exception"
                break
            if not has_throw:
                for path, sub in javalang.ast.Node.filter(if_node.then_statement, ReturnStatement):
                    ret_expr = self._reconstruct_expression(sub.expression) if sub.expression else "void"
                    if "false" in ret_expr.lower() or "reject" in ret_expr.lower() or "error" in ret_expr.lower():
                        outcome = f"Reject: returns {ret_expr}"
                        break

        # Action & State Change extraction inside then_statement
        promoted_action = None
        state_change_new = None
        state_change_prev = None

        if if_node.then_statement:
            for path, sub_node in javalang.ast.Node.filter(if_node.then_statement, MethodInvocation):
                m_name = sub_node.member
                if m_name.startswith("set") and len(sub_node.arguments) > 0 and ("status" in m_name.lower() or "state" in m_name.lower()):
                    val_arg = self._reconstruct_expression(sub_node.arguments[0])
                    state_change_new = val_arg
                elif not m_name.startswith("get") and not m_name.startswith("is") and m_name != "save":
                    promoted_action = f"{m_name}()"

            for path, sub_node in javalang.ast.Node.filter(if_node.then_statement, Assignment):
                target = self._reconstruct_expression(sub_node.expressionl)
                val = self._reconstruct_expression(sub_node.value)
                if "status" in target.lower() or "state" in target.lower():
                    state_change_new = val

        # Check for previous state in condition (e.g. if (status == PENDING))
        if state_change_new and isinstance(if_node.condition, BinaryOperation):
            if if_node.condition.operator in ("==", "!="):
                left = self._reconstruct_expression(if_node.condition.operandl)
                right = self._reconstruct_expression(if_node.condition.operandr)
                if "status" in left.lower() or "state" in left.lower():
                    state_change_prev = right
                elif "status" in right.lower() or "state" in right.lower():
                    state_change_prev = left

        # Check for Threshold (comparison operator with numeric/constant literal or symbolic reference)
        threshold_val = None
        threshold_op = None
        if isinstance(if_node.condition, BinaryOperation):
            op = if_node.condition.operator
            if op in (">", ">=", "<", "<=", "==", "!="):
                left_str = self._reconstruct_expression(if_node.condition.operandl)
                right_str = self._reconstruct_expression(if_node.condition.operandr)

                if self._is_literal_or_symbolic(if_node.condition.operandr):
                    threshold_val = right_str
                    threshold_op = op
                elif self._is_literal_or_symbolic(if_node.condition.operandl):
                    threshold_val = left_str
                    threshold_op = op

        # Determine Rule Type
        if has_throw or outcome:
            rule_type = RuleType.VALIDATION
            title = f"Validation Rule: {cond_expr}"
        elif threshold_val:
            rule_type = RuleType.THRESHOLD
            title = f"Threshold Check: {cond_expr}"
        elif state_change_new:
            rule_type = RuleType.STATE_TRANSITION
            title = f"State Transition: -> {state_change_new}"
        elif promoted_action:
            rule_type = RuleType.ACTION
            title = f"Conditional Action: {promoted_action}"
        else:
            rule_type = RuleType.CONDITIONAL
            title = f"Conditional Rule: {cond_expr}"

        # Construct Rule Trace
        rule_trace = [
            {"step_type": "CONDITION", "label": f"If ({cond_expr})", "details": cond_expr, "line_number": line_no},
            {"step_type": "DECISION_CONTEXT", "label": "Control Flow Evaluation", "details": f"Line {line_no}: {source_line[:80]}", "line_number": line_no},
        ]
        if promoted_action:
            rule_trace.append({"step_type": "ACTION", "label": f"Execute {promoted_action}", "details": promoted_action, "line_number": line_no})
        if outcome:
            rule_trace.append({"step_type": "ACTION", "label": outcome, "details": outcome, "line_number": line_no})
        if state_change_new:
            prev_desc = state_change_prev if state_change_prev else "UNKNOWN"
            rule_trace.append({
                "step_type": "STATE_CHANGE",
                "label": f"Transition state: {prev_desc} -> {state_change_new}",
                "details": f"Previous: {prev_desc}, New: {state_change_new}",
                "line_number": line_no,
            })

        rules.append({
            "analysis_id": analysis_id,
            "repository_id": repository_id,
            "entity_id": entity_id,
            "method_id": method_id,
            "rule_type": rule_type,
            "title": title,
            "status": RuleStatus.EXTRACTED,
            "condition_expression": cond_expr,
            "action_expression": promoted_action,
            "outcome_expression": outcome,
            "threshold_value": threshold_val,
            "threshold_operator": threshold_op,
            "previous_state": state_change_prev,  # None if unknown (rendered as UNKNOWN)
            "new_state": state_change_new,
            "rule_trace": rule_trace,
            "relative_file_path": relative_file_path,
            "line_start": line_no,
            "line_end": line_no + 3,
            "source_construct": "if_statement",
            "extraction_reason": f"Deterministic control flow pattern at line {line_no}",
        })

        return rules

    def _extract_assignment_rule(
        self,
        analysis_id: str,
        repository_id: str,
        entity_id: Optional[str],
        method_id: Optional[str],
        relative_file_path: str,
        target_var: str,
        value_node: Any,
        line_no: int,
        file_lines: list[str],
    ) -> Optional[dict[str, Any]]:
        if not isinstance(value_node, BinaryOperation):
            return None

        op = value_node.operator
        if op not in ("*", "/", "+", "-"):
            return None

        formula_expr = self._reconstruct_expression(value_node)
        source_line = self._get_source_line(file_lines, line_no)

        rule_trace = [
            {"step_type": "DECISION_CONTEXT", "label": "Calculation Formula Evaluation", "details": f"Assigning {target_var}", "line_number": line_no},
            {"step_type": "ACTION", "label": f"Compute {target_var} = {formula_expr}", "details": formula_expr, "line_number": line_no},
        ]

        return {
            "analysis_id": analysis_id,
            "repository_id": repository_id,
            "entity_id": entity_id,
            "method_id": method_id,
            "rule_type": RuleType.CALCULATION,
            "title": f"Calculation: {target_var} = {formula_expr}",
            "status": RuleStatus.EXTRACTED,
            "calculation_formula": f"{target_var} = {formula_expr}",
            "action_expression": f"Calculate {target_var}",
            "rule_trace": rule_trace,
            "relative_file_path": relative_file_path,
            "line_start": line_no,
            "line_end": line_no,
            "source_construct": "assignment_expression",
            "extraction_reason": f"Mathematical formula assignment ({op}) at line {line_no}",
        }

    def _reconstruct_expression(self, node: Any) -> str:
        """Helper to reconstruct readable string from javalang AST node."""
        if node is None:
            return ""
        if isinstance(node, str):
            return node
        if isinstance(node, Literal):
            return str(node.value)
        if isinstance(node, MemberReference):
            prefix = f"{node.qualifier}." if node.qualifier else ""
            return f"{prefix}{node.member}"
        if isinstance(node, MethodInvocation):
            args = ", ".join(self._reconstruct_expression(a) for a in node.arguments or [])
            qual = f"{node.qualifier}." if node.qualifier else ""
            return f"{qual}{node.member}({args})"
        if isinstance(node, BinaryOperation):
            left = self._reconstruct_expression(node.operandl)
            right = self._reconstruct_expression(node.operandr)
            return f"{left} {node.operator} {right}"
        if hasattr(node, "name"):
            return str(node.name)
        return str(node)

    def _is_literal_or_symbolic(self, node: Any) -> bool:
        if isinstance(node, Literal):
            return True
        if isinstance(node, MemberReference):
            if node.member.isupper() or (node.qualifier and node.qualifier[0].isupper()):
                return True
        return False

    def _get_source_line(self, file_lines: list[str], line_no: int) -> str:
        if 1 <= line_no <= len(file_lines):
            return file_lines[line_no - 1].strip()
        return ""

    def _deduplicate_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Deduplicates extracted candidates by file, line, rule_type, and condition.
        Prevents displaying duplicate rule candidates from the same control flow site.
        """
        seen: set[tuple[str, int, str, str]] = set()
        deduped: list[dict[str, Any]] = []

        for c in candidates:
            file_path = c.get("relative_file_path", "")
            line = c.get("line_start", 0)
            rule_type = c.get("rule_type", "")
            cond = c.get("condition_expression") or c.get("calculation_formula") or ""

            key = (file_path, line, str(rule_type), cond)
            if key in seen:
                continue

            seen.add(key)
            deduped.append(c)

        return deduped
