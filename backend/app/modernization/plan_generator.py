"""
LEGACYX — Deterministic Modernization Plan Generator Engine (Phase 7).

Consumes:
- CodeEntity (Phase 3 System X-Ray candidate component)
- ModernizationStrategy (Phase 6 strategy recommendation / override state)
- AST Responsibilities (Phase 6 responsibility signals)
- BusinessRules (Phase 4 extracted rules & traces)
- Impact Summary & Direct Dependents (Phase 5 impact surface)

Produces:
- ModernizationPlan payload with topologically ordered ModernizationTask objects
- Explicit evidence traceability (file paths, line numbers, rules, impact callers)
- Preservation Rules Catalog
- Verification Checkpoints Catalog
- Topological DAG sequence ordering (Acyclic execution)
"""

import uuid
from typing import Any, List, Dict
from app.models.modernization_plan import TaskType


class ModernizationPlanGenerator:
    """Generates evidence-backed modernization execution plans deterministically."""

    def generate_plan(
        self,
        entity_name: str,
        entity_type: str,
        component_type: str,
        relative_file_path: str,
        strategy_type: str,
        responsibilities: List[Dict[str, Any]],
        business_rules: List[Dict[str, Any]],
        impact_summary: Dict[str, Any],
        direct_dependents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Main entrypoint. Evaluates static analysis facts and builds a deterministic plan.
        """
        # 1. Compile Rules to Preserve
        rules_to_preserve = [
            {
                "rule_id": r.get("id"),
                "title": r.get("title"),
                "rule_type": r.get("rule_type"),
                "relative_file_path": r.get("relative_file_path", relative_file_path),
                "line_start": r.get("line_start"),
                "line_end": r.get("line_end"),
                "condition_expression": r.get("condition_expression"),
                "calculation_formula": r.get("calculation_formula"),
            }
            for r in business_rules
        ]

        # 2. Extract Evidence Tasks
        raw_tasks: List[Dict[str, Any]] = []

        # A. Group Business Rules by Type for Specific Isolation Tasks
        validation_rules = [r for r in business_rules if r.get("rule_type") == "VALIDATION"]
        threshold_rules = [r for r in business_rules if r.get("rule_type") in ["THRESHOLD", "CONDITIONAL"]]
        calculation_rules = [r for r in business_rules if r.get("rule_type") == "CALCULATION"]
        state_rules = [r for r in business_rules if r.get("rule_type") == "STATE_TRANSITION"]
        action_rules = [r for r in business_rules if r.get("rule_type") == "ACTION"]

        # Track task UUIDs for dependency chaining
        isolation_task_ids: List[str] = []

        # (i) Validation Rule Isolation Task
        if validation_rules:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.SEPARATE_BUSINESS_RULE.value,
                "title": f"Separate Precondition & Validation Rules from {entity_name}",
                "description": f"Isolate {len(validation_rules)} validation rules into dedicated precondition validator helper.",
                "target_component": f"{entity_name}Validator",
                "target_file_path": relative_file_path,
                "rule_ids": [r["id"] for r in validation_rules if r.get("id")],
                "evidence_references": [
                    {
                        "file_path": r.get("relative_file_path", relative_file_path),
                        "line_start": r.get("line_start"),
                        "line_end": r.get("line_end"),
                        "expression": r.get("condition_expression"),
                    }
                    for r in validation_rules
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "RULE_PRESERVATION",
                    "description": "Verify precondition validation checks throw identical legacy exception types.",
                },
            })

        # (ii) Threshold & Control Rule Isolation Task
        if threshold_rules:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.SEPARATE_BUSINESS_RULE.value,
                "title": f"Isolate Threshold & Policy Decision Rules from {entity_name}",
                "description": f"Isolate {len(threshold_rules)} policy decision rules (e.g. threshold limits, conditional guards) into a dedicated policy module.",
                "target_component": f"{entity_name}Policy",
                "target_file_path": relative_file_path,
                "rule_ids": [r["id"] for r in threshold_rules if r.get("id")],
                "evidence_references": [
                    {
                        "file_path": r.get("relative_file_path", relative_file_path),
                        "line_start": r.get("line_start"),
                        "line_end": r.get("line_end"),
                        "expression": r.get("condition_expression"),
                    }
                    for r in threshold_rules
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "THRESHOLD_BOUNDARIES",
                    "description": "Verify threshold boundary condition expressions remain exact.",
                },
            })

        # (iii) Calculation Derivation Task
        if calculation_rules:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.EXTRACT_CALCULATION.value,
                "title": f"Extract Financial & Calculation Formulas from {entity_name}",
                "description": f"Extract {len(calculation_rules)} monetary and formula calculation rules into pure mathematical calculation functions.",
                "target_component": f"{entity_name}Calculator",
                "target_file_path": relative_file_path,
                "rule_ids": [r["id"] for r in calculation_rules if r.get("id")],
                "evidence_references": [
                    {
                        "file_path": r.get("relative_file_path", relative_file_path),
                        "line_start": r.get("line_start"),
                        "line_end": r.get("line_end"),
                        "formula": r.get("calculation_formula"),
                    }
                    for r in calculation_rules
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "CALCULATION_ACCURACY",
                    "description": "Verify financial formula calculation output matches legacy precision.",
                },
            })

        # (iv) State Transition Isolation Task
        if state_rules:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.ISOLATE_STATE_TRANSITION.value,
                "title": f"Isolate Domain Lifecycle State Transitions in {entity_name}",
                "description": f"Isolate {len(state_rules)} lifecycle state transitions into an explicit state machine or state transition handler.",
                "target_component": f"{entity_name}StateMachine",
                "target_file_path": relative_file_path,
                "rule_ids": [r["id"] for r in state_rules if r.get("id")],
                "evidence_references": [
                    {
                        "file_path": r.get("relative_file_path", relative_file_path),
                        "line_start": r.get("line_start"),
                        "line_end": r.get("line_end"),
                        "expression": r.get("condition_expression"),
                    }
                    for r in state_rules
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "STATE_INVARIANT",
                    "description": "Verify domain entity state transitions progress correctly.",
                },
            })

        # B. Group AST Responsibilities for Component Isolation Tasks
        persistence_resps = [resp for resp in responsibilities if resp.get("category") == "PERSISTENCE_MUTATION"]
        notification_resps = [resp for resp in responsibilities if resp.get("category") == "EXTERNAL_NOTIFICATION"]
        coordination_resps = [resp for resp in responsibilities if resp.get("category") == "SERVICE_COORDINATION"]

        if persistence_resps:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.ISOLATE_PERSISTENCE.value,
                "title": f"Isolate Database Persistence Mutations in {entity_name}",
                "description": f"Decouple {len(persistence_resps)} persistence mutation calls into dedicated repository adapter.",
                "target_component": f"{entity_name}RepositoryAdapter",
                "target_file_path": relative_file_path,
                "rule_ids": [],
                "evidence_references": [
                    {
                        "file_path": relative_file_path,
                        "line_number": resp.get("line_number"),
                        "category": resp.get("category"),
                        "snippet": resp.get("source_snippet"),
                    }
                    for resp in persistence_resps
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "PERSISTENCE_CONTRACT",
                    "description": "Verify database schema mutations remain transactionally safe.",
                },
            })

        if notification_resps:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.ISOLATE_EXTERNAL_NOTIFICATION.value,
                "title": f"Isolate External Event & Notification Dispatch in {entity_name}",
                "description": f"Decouple {len(notification_resps)} external notification and event dispatching statements into event publisher.",
                "target_component": f"{entity_name}EventPublisher",
                "target_file_path": relative_file_path,
                "rule_ids": [],
                "evidence_references": [
                    {
                        "file_path": relative_file_path,
                        "line_number": resp.get("line_number"),
                        "category": resp.get("category"),
                        "snippet": resp.get("source_snippet"),
                    }
                    for resp in notification_resps
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "EVENT_CONTRACT",
                    "description": "Verify external domain notifications dispatch without altering execution flow.",
                },
            })

        # C. Default Responsibility Isolation Task if no specific rules/resps matched
        if not raw_tasks:
            t_id = str(uuid.uuid4())
            isolation_task_ids.append(t_id)
            raw_tasks.append({
                "temp_id": t_id,
                "task_type": TaskType.EXTRACT_RESPONSIBILITY.value,
                "title": f"Refactor Localized Methods in {entity_name}",
                "description": f"Clean up method internal structures for component '{entity_name}'.",
                "target_component": entity_name,
                "target_file_path": relative_file_path,
                "rule_ids": [],
                "evidence_references": [
                    {
                        "file_path": relative_file_path,
                        "line_number": resp.get("line_number"),
                        "category": resp.get("category"),
                        "snippet": resp.get("source_snippet"),
                    }
                    for resp in responsibilities[:5]
                ],
                "depends_on_temp_ids": [],
                "verification_checkpoint": {
                    "checkpoint_type": "CODE_CLEANUP",
                    "description": "Verify code refactoring preserves existing unit tests.",
                },
            })

        # D. Interface Definition Task (Depends on Isolation Tasks)
        interface_task_id = str(uuid.uuid4())
        raw_tasks.append({
            "temp_id": interface_task_id,
            "task_type": TaskType.DEFINE_INTERFACE.value,
            "title": f"Define Target Domain Contract Interface for {entity_name}",
            "description": f"Define clean domain service interface decoupling extracted responsibilities for strategy {strategy_type}.",
            "target_component": f"I{entity_name}",
            "target_file_path": relative_file_path,
            "rule_ids": [r["id"] for r in business_rules if r.get("id")],
            "evidence_references": [
                {"file_path": relative_file_path, "type": "INTERFACE_CONTRACT", "entity_name": entity_name}
            ],
            "depends_on_temp_ids": list(isolation_task_ids),
            "verification_checkpoint": {
                "checkpoint_type": "INTERFACE_CONTRACT",
                "description": "Verify new domain interface covers all required operations.",
            },
        })

        # E. Pattern / Facade Task (Depends on Interface Task)
        pattern_task_id = str(uuid.uuid4())
        pattern_type = TaskType.INTRODUCE_FACADE.value if strategy_type in ["MODULARIZE", "STRANGLER", "RETAIN_AND_WRAP"] else TaskType.INTRODUCE_ADAPTER.value
        raw_tasks.append({
            "temp_id": pattern_task_id,
            "task_type": pattern_type,
            "title": f"Introduce Modernization Gateway / Facade for {entity_name}",
            "description": f"Wrap legacy component '{entity_name}' with a facade to maintain backward compatibility under strategy {strategy_type}.",
            "target_component": f"{entity_name}Facade",
            "target_file_path": relative_file_path,
            "rule_ids": [],
            "evidence_references": [
                {"file_path": relative_file_path, "type": "FACADE_WRAPPER", "strategy": strategy_type}
            ],
            "depends_on_temp_ids": [interface_task_id],
            "verification_checkpoint": {
                "checkpoint_type": "FACADE_COMPATIBILITY",
                "description": "Verify facade delegates calls to new domain modules seamlessly.",
            },
        })

        # F. Caller Migration Tasks for Direct Dependents (Depends on Facade Task)
        caller_task_ids: List[str] = []
        if direct_dependents:
            for dep in direct_dependents[:5]:
                dep_name = dep.get("name") or "CallerComponent"
                dep_path = dep.get("relative_file_path") or relative_file_path
                c_id = str(uuid.uuid4())
                caller_task_ids.append(c_id)
                raw_tasks.append({
                    "temp_id": c_id,
                    "task_type": TaskType.MIGRATE_CALLER.value,
                    "title": f"Update Direct Dependent '{dep_name}' Call Site",
                    "description": f"Update call site in '{dep_name}' to consume the modern interface/facade instead of direct legacy coupling.",
                    "target_component": dep_name,
                    "target_file_path": dep_path,
                    "rule_ids": [],
                    "evidence_references": [
                        {"file_path": dep_path, "type": "DIRECT_DEPENDENT", "caller_name": dep_name}
                    ],
                    "depends_on_temp_ids": [pattern_task_id],
                    "verification_checkpoint": {
                        "checkpoint_type": "CALLER_COMPATIBILITY",
                        "description": f"Verify caller {dep_name} operates correctly with modern facade.",
                    },
                })
        else:
            # Fallback if no direct dependents found
            c_id = str(uuid.uuid4())
            caller_task_ids.append(c_id)
            raw_tasks.append({
                "temp_id": c_id,
                "task_type": TaskType.MIGRATE_CALLER.value,
                "title": f"Verify Standalone Caller Contracts for {entity_name}",
                "description": f"Verify external callers can invoke component '{entity_name}' via modern facade interface.",
                "target_component": entity_name,
                "target_file_path": relative_file_path,
                "rule_ids": [],
                "evidence_references": [{"file_path": relative_file_path, "type": "SELF_CALLER"}],
                "depends_on_temp_ids": [pattern_task_id],
                "verification_checkpoint": {
                    "checkpoint_type": "CALLER_COMPATIBILITY",
                    "description": "Verify facade invocation contracts.",
                },
            })

        # G. Business Behavior Preservation Task (Depends on Caller Tasks)
        behavior_task_id = str(uuid.uuid4())
        raw_tasks.append({
            "temp_id": behavior_task_id,
            "task_type": TaskType.PRESERVE_BEHAVIOR.value,
            "title": f"Enforce Invariant Business Rules Preservation for {entity_name}",
            "description": f"Validate that all {len(business_rules)} extracted business rules remain enforced without behavioral drift.",
            "target_component": entity_name,
            "target_file_path": relative_file_path,
            "rule_ids": [r["id"] for r in business_rules if r.get("id")],
            "evidence_references": [
                {"rule_count": len(business_rules), "rules": [r.get("title") for r in business_rules]}
            ],
            "depends_on_temp_ids": list(caller_task_ids),
            "verification_checkpoint": {
                "checkpoint_type": "BEHAVIORAL_EQUIVALENCE",
                "description": "Verify 100% rule invariant preservation against legacy behavior.",
            },
        })

        # H. Final Verification Checkpoint Task (Depends on Behavior Preservation Task)
        checkpoint_task_id = str(uuid.uuid4())
        raw_tasks.append({
            "temp_id": checkpoint_task_id,
            "task_type": TaskType.ADD_VERIFICATION_CHECKPOINT.value,
            "title": f"Execute Final Modernization Verification Suite for {entity_name}",
            "description": f"Execute complete verification suite validating rule preservation, caller compatibility, and impact surface safety under strategy {strategy_type}.",
            "target_component": entity_name,
            "target_file_path": relative_file_path,
            "rule_ids": [r["id"] for r in business_rules if r.get("id")],
            "evidence_references": [
                {"strategy": strategy_type, "impact_count": len(direct_dependents), "rule_count": len(business_rules)}
            ],
            "depends_on_temp_ids": [behavior_task_id],
            "verification_checkpoint": {
                "checkpoint_type": "FINAL_AUDIT_PASS",
                "description": "All unit tests, integration contracts, and business rule invariants passed cleanly.",
            },
        })

        # 3. Map Temporary IDs to Final Task Dicts & Topological Sequence Order
        # Replace temp_ids with real UUIDs and build final tasks
        temp_to_final_id: Dict[str, str] = {t["temp_id"]: str(uuid.uuid4()) for t in raw_tasks}

        tasks: List[Dict[str, Any]] = []
        for idx, t in enumerate(raw_tasks, start=1):
            tasks.append({
                "id": temp_to_final_id[t["temp_id"]],
                "sequence_order": idx,
                "title": t["title"],
                "description": t["description"],
                "task_type": t["task_type"],
                "status": "PENDING",
                "target_component": t["target_component"],
                "target_file_path": t["target_file_path"],
                "depends_on_task_ids": [temp_to_final_id[tid] for tid in t["depends_on_temp_ids"] if tid in temp_to_final_id],
                "rule_ids": t["rule_ids"],
                "evidence_references": t["evidence_references"],
                "verification_checkpoint": t["verification_checkpoint"],
            })

        # 4. Generate Verification Checkpoints Catalog for Plan
        verification_checkpoints = [
            {
                "task_order": t["sequence_order"],
                "task_title": t["title"],
                "checkpoint": t["verification_checkpoint"],
            }
            for t in tasks
        ]

        # 5. Build Summary
        summary = (
            f"Deterministic Modernization Execution Plan for '{entity_name}' ({strategy_type}). "
            f"Consists of {len(tasks)} ordered tasks, preserving {len(rules_to_preserve)} business rules across "
            f"{len(direct_dependents)} direct dependent callers with {len(verification_checkpoints)} verification checkpoints."
        )

        return {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "component_type": component_type,
            "relative_file_path": relative_file_path,
            "strategy_type": strategy_type,
            "summary": summary,
            "rules_to_preserve": rules_to_preserve,
            "impact_summary": impact_summary,
            "verification_checkpoints": verification_checkpoints,
            "tasks": tasks,
        }


plan_generator = ModernizationPlanGenerator()
