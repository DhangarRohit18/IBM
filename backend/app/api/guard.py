"""
LEGACYX — LegacyX Guard API Router.

Provides developer-facing IDE extension endpoints for:
- 01 Understand: Business decision discovery & method risk analysis
- 02 Capture: Behavioral baseline freezing from method execution
- 03 Change Impact: Blast radius evaluation across services, APIs, and scenarios
- 04 Prove: Dual-harness replay & silent drift detection
- Mutation Challenge: Controlled drift injection into modernization candidates
- Ask LegacyX: Grounded AI reasoning using deterministic AST & replay evidence
"""

from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/guard", tags=["LegacyX Guard (IDE)"])

# State holding mutated state for live demonstration
_MUTATION_STATE = {
    "is_mutated": False,
    "source_file": "FeeCalculation.java",
    "line": 45,
    "active_rounding": "HALF_UP",
}


class AnalyzeMethodRequest(BaseModel):
    file_path: str = Field(default="FeeCalculation.java", description="Relative path of file in IDE")
    method_name: str = Field(default="calculateTransferFee", description="Selected Java method name")


class VerifyChangeRequest(BaseModel):
    file_path: str = Field(default="FeeCalculation.java", description="Relative path of modified file")
    method_name: str = Field(default="calculateTransferFee", description="Target method name")
    override_mutation: Optional[bool] = Field(default=None, description="Force mutated state for live verification")


class AskLegacyXRequest(BaseModel):
    question: str = Field(..., description="Developer question about method, risk, or drift")
    method_name: str = Field(default="calculateTransferFee")
    file_path: str = Field(default="FeeCalculation.java")


class InjectDriftRequest(BaseModel):
    enabled: bool = Field(..., description="Whether to inject controlled drift into modern runtime")


# ── 01 — Understand ──────────────────────────────────────────────────────────

@router.post("/analyze-method", summary="01 Understand: Analyze Business Decisions in Method")
async def analyze_method(req: AnalyzeMethodRequest) -> dict[str, Any]:
    return {
        "file_path": req.file_path,
        "method_name": req.method_name,
        "business_decisions_found": 3,
        "business_decisions": [
            {
                "id": "DEC-01",
                "title": "Transfer Fee Calculation",
                "rule": "amount > ₹50,000 ? 0.50% (High-Value Tariff) : 0.25% (Standard)",
                "covered_scenarios": 7,
                "risk_level": "HIGH",
                "line_range": "38-55",
                "description": "Calculates tier-based service fees with BigDecimal precision.",
            },
            {
                "id": "DEC-02",
                "title": "High-Risk Compliance Boundary",
                "rule": "amount > ₹50,000 AND risk_score > 70 -> Compliance Hold",
                "covered_scenarios": 5,
                "risk_level": "CRITICAL",
                "line_range": "57-68",
                "description": "Enforces AML velocity ceilings and fraud mitigation flags.",
            },
            {
                "id": "DEC-03",
                "title": "VIP Tier Exemption Policy",
                "rule": "customer.tier == 'VIP' -> 50% discount on calculated fee",
                "covered_scenarios": 3,
                "risk_level": "MEDIUM",
                "line_range": "70-82",
                "description": "Waives fractional surcharges for accredited institutional accounts.",
            },
        ],
        "dependencies": [
            "com.legacybank.service.CustomerService",
            "com.legacybank.service.AccountService",
            "com.legacybank.policy.FeePolicy",
        ],
        "affected_apis": [
            "POST /api/v1/transfers",
            "GET /api/v1/fees/estimate",
        ],
        "risk_level": "HIGH",
        "guidance": "Method controls financial debit invariants. Any modernization requires behavioral replay verification.",
    }


# ── 02 — Capture ─────────────────────────────────────────────────────────────

@router.post("/create-baseline", summary="02 Capture: Create Behavioral Baseline from Legacy Behavior")
async def create_baseline(req: AnalyzeMethodRequest) -> dict[str, Any]:
    scenarios = [
        {"id": "SCEN-01", "name": "Normal transfer", "input": "₹25,000 / Risk 15", "legacy_output": "₹62.50", "status": "FROZEN"},
        {"id": "SCEN-02", "name": "₹49,999 boundary", "input": "₹49,999 / Risk 20", "legacy_output": "₹124.99", "status": "FROZEN"},
        {"id": "SCEN-03", "name": "₹50,000 boundary", "input": "₹50,000 / Risk 42", "legacy_output": "₹250.00", "status": "FROZEN"},
        {"id": "SCEN-04", "name": "₹50,001 boundary", "input": "₹50,001 / Risk 42", "legacy_output": "₹250.01", "status": "FROZEN"},
        {"id": "SCEN-05", "name": "Premium customer", "input": "₹50,000 / VIP", "legacy_output": "₹125.00", "status": "FROZEN"},
        {"id": "SCEN-06", "name": "High-risk customer", "input": "₹60,000 / Risk 75", "legacy_output": "COMPLIANCE_HOLD", "status": "FROZEN"},
        {"id": "SCEN-07", "name": "Decimal rounding", "input": "₹285.50 / Risk 10", "legacy_output": "₹1.43", "status": "FROZEN"},
    ]
    return {
        "status": "BASE_FROZEN",
        "method_name": req.method_name,
        "scenarios_captured": len(scenarios),
        "fingerprint": "sha256:4f9a0c2188b1ec45d3e098a12903fe45b8",
        "scenarios": scenarios,
        "message": f"Successfully captured and frozen {len(scenarios)} canonical execution paths into immutable baseline.",
    }


# ── 03 — Change Impact (Blast Radius) ────────────────────────────────────────

@router.post("/change-impact", summary="03 Change: Evaluate Change Impact & Blast Radius")
async def change_impact(req: AnalyzeMethodRequest) -> dict[str, Any]:
    return {
        "changed_method": req.method_name,
        "changed_file": req.file_path,
        "blast_radius": {
            "business_decisions_affected": 3,
            "behavioral_scenarios_affected": 7,
            "downstream_services_affected": [
                "TransferService",
                "AccountService",
                "AuditLedgerService",
            ],
            "public_apis_affected": [
                "POST /api/v1/transfers",
                "GET /api/v1/fees/estimate",
            ],
        },
        "safety_advisory": "Change directly modifies monetary outcome for high-value transactions. Replay verification mandatory before git commit.",
    }


# ── 04 — Prove (Verify Change & Drift Detection) ─────────────────────────────

@router.post("/verify-change", summary="04 Prove: Execute Dual-Harness Replay & Detect Silent Drift")
async def verify_change(req: VerifyChangeRequest) -> dict[str, Any]:
    # Determine if mutated: if explicitly requested or global mutation state is enabled
    is_mutated = req.override_mutation if req.override_mutation is not None else _MUTATION_STATE["is_mutated"]

    if is_mutated:
        # DRIFT DETECTED: Scenario #04 diverges due to RoundingMode change
        scenario_results = [
            {"id": "SCEN-01", "name": "Normal transfer", "legacy": "₹62.50", "current": "₹62.50", "status": "PRESERVED"},
            {"id": "SCEN-02", "name": "₹49,999 boundary", "legacy": "₹124.99", "current": "₹124.99", "status": "PRESERVED"},
            {"id": "SCEN-03", "name": "₹50,000 boundary", "legacy": "₹250.00", "current": "₹250.00", "status": "PRESERVED"},
            {
                "id": "SCEN-04",
                "name": "Fee Calculation & Rounding Mode",
                "input": "Transfer Amount: ₹50,000 | Customer: CUST-1042 | Risk Score: 42",
                "legacy": "₹250.00",
                "current": "₹249.99",
                "difference": "₹0.01",
                "status": "DRIFT_DETECTED",
                "is_hero": True,
            },
            {"id": "SCEN-05", "name": "Premium customer", "legacy": "₹125.00", "current": "₹125.00", "status": "PRESERVED"},
            {"id": "SCEN-06", "name": "High-risk customer", "legacy": "COMPLIANCE_HOLD", "current": "COMPLIANCE_HOLD", "status": "PRESERVED"},
            {"id": "SCEN-07", "name": "Decimal rounding", "legacy": "₹1.43", "current": "₹1.43", "status": "PRESERVED"},
        ]
        return {
            "status": "BEHAVIORAL_DRIFT_DETECTED",
            "overall_equivalence": False,
            "total_scenarios": 7,
            "equivalent_count": 6,
            "drift_count": 1,
            "hero_drift": {
                "scenario_id": "SCEN-04",
                "transfer_amount": "₹50,000",
                "customer_id": "CUST-1042",
                "risk_score": 42,
                "legacy_runtime": "₹250.00",
                "current_runtime": "₹249.99",
                "difference": "₹0.01",
                "decision_changed": True,
                "root_cause": {
                    "policy_change": "Fee calculation changed",
                    "behavior_change": "Rounding behaviour changed",
                    "source_file": "FeeCalculation.java",
                    "line": 45,
                    "diff": (
                        "- BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_UP);\n"
                        "+ BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_DOWN);"
                    ),
                },
                "impacted": {
                    "services": 3,
                    "scenarios": 7,
                    "apis": 2,
                },
            },
            "scenario_results": scenario_results,
            "wow_quote": "The compiler said this change was valid. LegacyX said the business decision wasn't.",
        }
    else:
        # ALL SCENARIOS EQUIVALENT
        scenario_results = [
            {"id": "SCEN-01", "name": "Normal transfer", "legacy": "₹62.50", "current": "₹62.50", "status": "PRESERVED"},
            {"id": "SCEN-02", "name": "₹49,999 boundary", "legacy": "₹124.99", "current": "₹124.99", "status": "PRESERVED"},
            {"id": "SCEN-03", "name": "₹50,000 boundary", "legacy": "₹250.00", "current": "₹250.00", "status": "PRESERVED"},
            {"id": "SCEN-04", "name": "Fee Calculation & Rounding Mode", "legacy": "₹250.00", "current": "₹250.00", "status": "PRESERVED"},
            {"id": "SCEN-05", "name": "Premium customer", "legacy": "₹125.00", "current": "₹125.00", "status": "PRESERVED"},
            {"id": "SCEN-06", "name": "High-risk customer", "legacy": "COMPLIANCE_HOLD", "current": "COMPLIANCE_HOLD", "status": "PRESERVED"},
            {"id": "SCEN-07", "name": "Decimal rounding", "legacy": "₹1.43", "current": "₹1.43", "status": "PRESERVED"},
        ]
        return {
            "status": "BEHAVIORALLY_EQUIVALENT",
            "overall_equivalence": True,
            "total_scenarios": 7,
            "equivalent_count": 7,
            "drift_count": 0,
            "hero_drift": None,
            "scenario_results": scenario_results,
            "wow_quote": "100% Behavioral Equivalence Verified. Zero silent drift detected.",
        }


# ── Mutation Challenge ───────────────────────────────────────────────────────

@router.post("/inject-drift", summary="Mutation Challenge: Inject Controlled Drift for Live Demo")
async def inject_drift(req: InjectDriftRequest) -> dict[str, Any]:
    global _MUTATION_STATE
    _MUTATION_STATE["is_mutated"] = req.enabled
    _MUTATION_STATE["active_rounding"] = "HALF_DOWN" if req.enabled else "HALF_UP"
    return {
        "status": "MUTATION_CONFIGURED",
        "is_mutated": _MUTATION_STATE["is_mutated"],
        "active_rounding": _MUTATION_STATE["active_rounding"],
        "target_file": "FeeCalculation.java",
        "target_line": 45,
        "source_diff": (
            "- BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_UP);\n"
            "+ BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_DOWN);"
        ) if req.enabled else "No active mutation. Original RoundingMode.HALF_UP restored.",
        "message": (
            "Controlled drift INJECTED: RoundingMode altered to HALF_DOWN. Run 'Verify Change' in LegacyX Guard to catch the drift!"
            if req.enabled
            else "Controlled drift REMOVED: RoundingMode restored to HALF_UP. Run 'Verify Change' to observe 100% equivalence."
        ),
    }


# ── Ask LegacyX AI Reasoning ─────────────────────────────────────────────────

@router.post("/ask", summary="Ask LegacyX: Grounded AI Explanation using Deterministic Evidence")
async def ask_legacyx(req: AskLegacyXRequest) -> dict[str, Any]:
    q_lower = req.question.lower()
    if "risk" in q_lower or "why" in q_lower:
        explanation = (
            "This method (calculateTransferFee) is classified as HIGH RISK because it directly governs monetary debits "
            "across 3 downstream services (AccountService, TransferService, AuditLedgerService) and 2 public REST endpoints. "
            "It establishes the high-value transaction boundary at ₹50,000. Under boundary condition Scenario #04, altering "
            "the rounding strategy from RoundingMode.HALF_UP to RoundingMode.HALF_DOWN produces an unprescribed ₹0.01 deficit."
        )
    elif "drift" in q_lower or "scenario" in q_lower or "04" in q_lower:
        explanation = (
            "Scenario #04 failed with a ₹0.01 discrepancy (Legacy: ₹250.00 vs Current: ₹249.99). "
            "Deterministic AST analysis traced the root cause directly to FeeCalculation.java:45, where BigDecimal rounding mode "
            "was altered from RoundingMode.HALF_UP to RoundingMode.HALF_DOWN. To preserve the business decision, revert to HALF_UP."
        )
    else:
        explanation = (
            f"LegacyX Guard AST Analysis for {req.method_name} in {req.file_path}: Controls 3 business decisions, "
            f"covers 7 canonical boundary scenarios, and connects to 3 downstream banking services. "
            f"All changes must be replayed against the frozen behavioral baseline (SHA-256: 4f9a...88b1)."
        )

    return {
        "question": req.question,
        "method_name": req.method_name,
        "file_path": req.file_path,
        "explanation": explanation,
        "evidence_used": {
            "ast_nodes": ["calculateTransferFee", "amount", "BigDecimal.setScale"],
            "dependencies": ["CustomerService", "AccountService", "FeePolicy"],
            "frozen_baseline_hash": "4f9a0c2188b1ec45d3e098a12903fe45b8",
            "active_rounding": _MUTATION_STATE["active_rounding"],
        },
    }
