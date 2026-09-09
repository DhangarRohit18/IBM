"""
LEGACYX — Deterministic Responsibility Analyzer Engine (Phase 6).

Analyzes Java source code and AST representations to observe evidence-backed component responsibilities:
- INPUT_VALIDATION
- BUSINESS_RULE_ENFORCEMENT
- CALCULATION_DERIVATION
- SERVICE_COORDINATION
- PERSISTENCE_MUTATION
- STATE_TRANSITION
- EXTERNAL_NOTIFICATION

Strict AI Boundary:
All responsibility items are established deterministically with source line evidence.
AI never claims semantic responsibilities unsupported by static evidence.
"""

import enum
import re
from typing import Any
import javalang


class ResponsibilityCategory(str, enum.Enum):
    INPUT_VALIDATION = "INPUT_VALIDATION"
    BUSINESS_RULE_ENFORCEMENT = "BUSINESS_RULE_ENFORCEMENT"
    CALCULATION_DERIVATION = "CALCULATION_DERIVATION"
    SERVICE_COORDINATION = "SERVICE_COORDINATION"
    PERSISTENCE_MUTATION = "PERSISTENCE_MUTATION"
    STATE_TRANSITION = "STATE_TRANSITION"
    EXTERNAL_NOTIFICATION = "EXTERNAL_NOTIFICATION"


class ResponsibilityAnalyzer:
    """Analyzes class source lines and AST tree to detect deterministic responsibility signals."""

    def analyze_responsibilities(
        self,
        relative_file_path: str,
        file_lines: list[str],
        ast_tree: Any | None = None,
    ) -> list[dict[str, Any]]:
        responsibilities: list[dict[str, Any]] = []
        seen_keys: set[str] = set()

        if not file_lines:
            return responsibilities

        for line_idx, raw_line in enumerate(file_lines):
            line_no = line_idx + 1
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                continue

            line_lower = line.lower()

            # 1. INPUT_VALIDATION
            if any(k in line_lower for k in ["== null", "!= null", "requirenonnull", "illegalargumentexception", "invalidargument"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.INPUT_VALIDATION,
                    title="Input & Precondition Validation",
                    description="Validates argument invariants or null checks before execution",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed precondition check at line {line_no}",
                    source_snippet=line,
                )

            # 2. BUSINESS_RULE_ENFORCEMENT
            if any(k in line_lower for k in ["isfraudulent", "isblocked", "requiremanagerapproval", "exceeds", "haspermission", "checkrule"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.BUSINESS_RULE_ENFORCEMENT,
                    title="Business Rule Enforcement",
                    description="Evaluates domain control flow, threshold boundaries, or fraud/risk rules",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed business rule check at line {line_no}",
                    source_snippet=line,
                )

            # 3. CALCULATION_DERIVATION
            if any(k in line_lower for k in ["calculatefee", "calculatetotal", "amount *", "fee =", "balance -", "balance +"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.CALCULATION_DERIVATION,
                    title="Calculation & Financial Derivation",
                    description="Computes monetary amounts, fee derivations, or balance adjustments",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed formula or calculation derivation at line {line_no}",
                    source_snippet=line,
                )

            # 4. SERVICE_COORDINATION
            if any(k in line_lower for k in ["fraudservice.", "accountservice.", "paymentservice.", "externalclient."]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.SERVICE_COORDINATION,
                    title="External Service Coordination",
                    description="Coordinates inter-service workflow by invoking secondary domain services",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed cross-service invocation at line {line_no}",
                    source_snippet=line,
                )

            # 5. PERSISTENCE_MUTATION
            if any(k in line_lower for k in ["repository.save", "repository.delete", "repository.update", "entitymanager.persist", "saveandflush"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.PERSISTENCE_MUTATION,
                    title="Database Persistence Mutation",
                    description="Performs database state mutations via repository or entity manager",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed database persistence mutation at line {line_no}",
                    source_snippet=line,
                )

            # 6. STATE_TRANSITION
            if any(k in line_lower for k in ["setstatus(", "setstate(", "status.completed", "status.failed", "status.pending"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.STATE_TRANSITION,
                    title="Entity State Transition",
                    description="Mutates domain entity lifecycle state (e.g. PENDING -> COMPLETED)",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed lifecycle state transition at line {line_no}",
                    source_snippet=line,
                )

            # 7. EXTERNAL_NOTIFICATION
            if any(k in line_lower for k in ["notificationservice.", "eventservice.", "sendemail", "publish", "sendnotification"]):
                self._add_resp(
                    responsibilities,
                    seen_keys,
                    category=ResponsibilityCategory.EXTERNAL_NOTIFICATION,
                    title="External Event & Notification Dispatch",
                    description="Dispatches external notifications, emails, or asynchronous domain events",
                    relative_file_path=relative_file_path,
                    line_number=line_no,
                    evidence_reason=f"Observed notification dispatch at line {line_no}",
                    source_snippet=line,
                )

        return responsibilities

    def _add_resp(
        self,
        resps: list[dict[str, Any]],
        seen: set[str],
        category: ResponsibilityCategory,
        title: str,
        description: str,
        relative_file_path: str,
        line_number: int,
        evidence_reason: str,
        source_snippet: str,
    ) -> None:
        key = f"{category.value}:{line_number}"
        if key in seen:
            return
        seen.add(key)
        resps.append({
            "category": category.value,
            "title": title,
            "description": description,
            "relative_file_path": relative_file_path,
            "line_number": line_number,
            "evidence_reason": evidence_reason,
            "source_snippet": source_snippet[:200],
        })


responsibility_analyzer = ResponsibilityAnalyzer()
