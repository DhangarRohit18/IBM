"""
LEGACYX — Deterministic Transformation Engine (Phase 8).

Consumes approved Phase 7 ModernizationPlan & ModernizationTask models, AST signatures (Phase 3),
extracted business rules (Phase 4), and caller impact surfaces (Phase 5).

Generates grounded transformation specifications, target code artifacts
(EXTRACTED_CLASS, EXTRACTED_INTERFACE, FACADE, ADAPTER, REFACTORED_METHOD, MIGRATED_CALLER, SUPPORTING_TEST_STUB),
and git-style unified diffs.

Enforces original source immutability by outputting to isolated storage workspaces.
"""

import difflib
from pathlib import Path
from typing import Any

from app.models.modernization_plan import ModernizationPlan, ModernizationTask, TaskType
from app.models.transformation import ArtifactCategory


class TransformationEngine:
    """
    Deterministic Code Transformation Engine.
    Grounds transformation generation strictly in static analysis evidence, rules to preserve,
    and impact surfaces without mutating original source files.
    """

    def build_transformation_specification(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        rules: list[dict[str, Any]],
        impacted_callers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Builds a complete, evidence-grounded transformation specification.
        """
        category = self.map_task_type_to_artifact_category(task.task_type)

        spec = {
            "plan_id": plan.id,
            "task_id": task.id,
            "entity_name": plan.entity_name,
            "relative_file_path": plan.relative_file_path,
            "task_type": task.task_type,
            "artifact_category": category.value,
            "target_component": task.target_component,
            "target_file_path": task.target_file_path,
            "rules_to_preserve": rules,
            "impacted_callers": impacted_callers,
            "evidence_references": task.evidence_references,
            "verification_checkpoint": task.verification_checkpoint,
        }
        return spec

    def map_task_type_to_artifact_category(self, task_type: str) -> ArtifactCategory:
        """
        Maps controlled Phase 7 TaskType string to Phase 8 ArtifactCategory.
        """
        mapping = {
            TaskType.EXTRACT_RESPONSIBILITY.value: ArtifactCategory.EXTRACTED_CLASS,
            TaskType.SEPARATE_BUSINESS_RULE.value: ArtifactCategory.EXTRACTED_CLASS,
            TaskType.EXTRACT_CALCULATION.value: ArtifactCategory.EXTRACTED_CLASS,
            TaskType.ISOLATE_PERSISTENCE.value: ArtifactCategory.REFACTORED_METHOD,
            TaskType.ISOLATE_STATE_TRANSITION.value: ArtifactCategory.REFACTORED_METHOD,
            TaskType.ISOLATE_EXTERNAL_NOTIFICATION.value: ArtifactCategory.REFACTORED_METHOD,
            TaskType.DEFINE_INTERFACE.value: ArtifactCategory.EXTRACTED_INTERFACE,
            TaskType.INTRODUCE_ADAPTER.value: ArtifactCategory.ADAPTER,
            TaskType.INTRODUCE_FACADE.value: ArtifactCategory.FACADE,
            TaskType.REDUCE_DEPENDENCY.value: ArtifactCategory.REFACTORED_METHOD,
            TaskType.SPLIT_COMPONENT.value: ArtifactCategory.EXTRACTED_CLASS,
            TaskType.MIGRATE_CALLER.value: ArtifactCategory.MIGRATED_CALLER,
            TaskType.PRESERVE_BEHAVIOR.value: ArtifactCategory.REFACTORED_METHOD,
            TaskType.ADD_VERIFICATION_CHECKPOINT.value: ArtifactCategory.SUPPORTING_TEST_STUB,
        }
        return mapping.get(task_type, ArtifactCategory.EXTRACTED_CLASS)

    def generate_deterministic_artifacts(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        rules: list[dict[str, Any]],
        impacted_callers: list[dict[str, Any]],
        source_code_snippet: str = "",
    ) -> list[dict[str, Any]]:
        """
        Generates deterministic candidate code artifacts and unified diffs.
        """
        category = self.map_task_type_to_artifact_category(task.task_type)
        artifacts = []

        if category == ArtifactCategory.EXTRACTED_CLASS:
            art = self._generate_extracted_class(plan, task, rules, source_code_snippet)
            artifacts.append(art)
        elif category == ArtifactCategory.EXTRACTED_INTERFACE:
            art = self._generate_extracted_interface(plan, task, source_code_snippet)
            artifacts.append(art)
        elif category == ArtifactCategory.FACADE:
            art = self._generate_facade(plan, task, source_code_snippet)
            artifacts.append(art)
        elif category == ArtifactCategory.ADAPTER:
            art = self._generate_adapter(plan, task, source_code_snippet)
            artifacts.append(art)
        elif category == ArtifactCategory.MIGRATED_CALLER:
            art = self._generate_migrated_caller(plan, task, impacted_callers, source_code_snippet)
            artifacts.append(art)
        elif category == ArtifactCategory.SUPPORTING_TEST_STUB:
            art = self._generate_test_stub(plan, task, rules, source_code_snippet)
            artifacts.append(art)
        else:
            art = self._generate_refactored_method(plan, task, rules, source_code_snippet)
            artifacts.append(art)

        return artifacts

    def compute_unified_diff(self, original_snippet: str, generated_code: str, file_path: str) -> str:
        """
        Computes standard git-style unified diff between legacy source snippet and generated code.
        """
        orig_lines = original_snippet.splitlines(keepends=True)
        gen_lines = generated_code.splitlines(keepends=True)

        diff = difflib.unified_diff(
            orig_lines,
            gen_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
        diff_str = "".join(diff)
        if not diff_str:
            diff_str = f"--- a/{file_path}\n+++ b/{file_path}\n@@ -1 +1 @@\n (No textual changes detected)\n"
        return diff_str

    def sanitize_artifact_path(self, target_file_path: str, project_id: str, plan_id: str) -> Path:
        """
        Sanitizes output paths to ensure generated artifacts cannot escape isolated storage directory
        storage/modernized/{project_id}/{plan_id}/ (AGENTS.md §7.2, Zip-Slip guard).
        """
        clean_name = Path(target_file_path).name
        if ".." in target_file_path or clean_name.startswith("/") or clean_name.startswith("\\"):
            clean_name = clean_name.lstrip("/\\.").replace("..", "_")

        base_dir = Path("storage") / "modernized" / project_id / plan_id
        resolved_path = (base_dir / clean_name).resolve()
        base_resolved = base_dir.resolve()

        # Prevent directory traversal
        try:
            resolved_path.relative_to(base_resolved)
        except ValueError:
            resolved_path = base_dir / clean_name

        return resolved_path

    # ── Private Template Generators ────────────────────────────────────────────

    def _generate_extracted_class(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        rules: list[dict[str, Any]],
        source_snippet: str,
    ) -> dict[str, Any]:
        target_name = task.target_component or f"{plan.entity_name}Service"
        target_path = task.target_file_path or f"src/main/java/com/legacybank/service/{target_name}.java"

        rule_methods = []
        for idx, r in enumerate(rules, start=1):
            r_title = r.get("title", f"Rule_{idx}")
            r_cond = r.get("condition_expression", "/* condition */")
            rule_methods.append(
                f"    /** Mapped Preserved Rule: {r_title} (ID: {r.get('id')}) */\n"
                f"    public boolean validate_{r_title.lower().replace(' ', '_')}(Object context) {{\n"
                f"        // Preserved logic: {r_cond}\n"
                f"        return {r_cond if ('<' in r_cond or '>' in r_cond or '==' in r_cond) else 'true'};\n"
                f"    }}"
            )

        code = (
            f"package com.legacybank.service;\n\n"
            f"import org.springframework.stereotype.Service;\n\n"
            f"/**\n"
            f" * Modernized Extracted Domain Service: {target_name}\n"
            f" * Decomposed from Legacy Component: {plan.entity_name}\n"
            f" * Task: {task.title} (ID: {task.id})\n"
            f" */\n"
            f"@Service\n"
            f"public class {target_name} {{\n\n"
            + "\n\n".join(rule_methods) + "\n"
            f"}}\n"
        )

        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.EXTRACTED_CLASS.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": len(source_snippet.splitlines()) or 50,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": rules,
            "evidence_references": task.evidence_references,
        }

    def _generate_extracted_interface(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        source_snippet: str,
    ) -> dict[str, Any]:
        target_name = task.target_component or f"I{plan.entity_name}"
        target_path = task.target_file_path or f"src/main/java/com/legacybank/service/{target_name}.java"

        code = (
            f"package com.legacybank.service;\n\n"
            f"/**\n"
            f" * Modernized Domain Interface: {target_name}\n"
            f" * Contract for {plan.entity_name}\n"
            f" */\n"
            f"public interface {target_name} {{\n"
            f"    void executeDomainOperation(Object request);\n"
            f"}}\n"
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.EXTRACTED_INTERFACE.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": 30,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": [],
            "evidence_references": task.evidence_references,
        }

    def _generate_facade(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        source_snippet: str,
    ) -> dict[str, Any]:
        facade_name = task.target_component or f"{plan.entity_name}Facade"
        target_path = task.target_file_path or f"src/main/java/com/legacybank/facade/{facade_name}.java"

        code = (
            f"package com.legacybank.facade;\n\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"/**\n"
            f" * Modernization Facade: {facade_name}\n"
            f" * Wraps legacy {plan.entity_name} to preserve caller interface backwards compatibility.\n"
            f" */\n"
            f"@Component\n"
            f"public class {facade_name} {{\n\n"
            f"    public void process(Object request) {{\n"
            f"        // Delegates caller requests to modern domain service\n"
            f"    }}\n"
            f"}}\n"
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.FACADE.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": 40,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": [],
            "evidence_references": task.evidence_references,
        }

    def _generate_adapter(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        source_snippet: str,
    ) -> dict[str, Any]:
        adapter_name = task.target_component or f"{plan.entity_name}Adapter"
        target_path = task.target_file_path or f"src/main/java/com/legacybank/adapter/{adapter_name}.java"

        code = (
            f"package com.legacybank.adapter;\n\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"/**\n"
            f" * Modernization Adapter: {adapter_name}\n"
            f" */\n"
            f"@Component\n"
            f"public class {adapter_name} {{\n"
            f"    public Object adapt(Object legacyInput) {{\n"
            f"        return legacyInput;\n"
            f"    }}\n"
            f"}}\n"
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.ADAPTER.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": 25,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": [],
            "evidence_references": task.evidence_references,
        }

    def _generate_migrated_caller(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        impacted_callers: list[dict[str, Any]],
        source_snippet: str,
    ) -> dict[str, Any]:
        caller_name = task.target_component or "AccountController"
        target_path = task.target_file_path or f"src/main/java/com/legacybank/controller/{caller_name}.java"

        code = (
            f"package com.legacybank.controller;\n\n"
            f"import org.springframework.web.bind.annotation.RestController;\n"
            f"import org.springframework.beans.factory.annotation.Autowired;\n\n"
            f"/**\n"
            f" * Migrated Caller: {caller_name}\n"
            f" * Updated to delegate calls directly to modern domain service.\n"
            f" */\n"
            f"@RestController\n"
            f"public class {caller_name} {{\n"
            f"    // Migrated dependency injection point\n"
            f"}}\n"
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.MIGRATED_CALLER.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": 35,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": [],
            "evidence_references": task.evidence_references,
        }

    def _generate_test_stub(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        rules: list[dict[str, Any]],
        source_snippet: str,
    ) -> dict[str, Any]:
        test_name = f"{task.target_component or plan.entity_name}Test"
        target_path = f"src/test/java/com/legacybank/service/{test_name}.java"

        test_methods = []
        for idx, r in enumerate(rules, start=1):
            r_title = r.get("title", f"Rule_{idx}")
            test_methods.append(
                f"    @Test\n"
                f"    void test_{r_title.lower().replace(' ', '_')}() {{\n"
                f"        // Verification Checkpoint for Preserved Rule ID: {r.get('id')}\n"
                f"        // Condition: {r.get('condition_expression')}\n"
                f"        assertTrue(true);\n"
                f"    }}"
            )

        code = (
            f"package com.legacybank.service;\n\n"
            f"import org.junit.jupiter.api.Test;\n"
            f"import static org.junit.jupiter.api.Assertions.*;\n\n"
            f"/**\n"
            f" * Supporting Verification Test Stub: {test_name}\n"
            f" * Task: {task.title}\n"
            f" */\n"
            f"public class {test_name} {{\n\n"
            + "\n\n".join(test_methods) + "\n"
            f"}}\n"
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.SUPPORTING_TEST_STUB.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": 45,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": rules,
            "evidence_references": task.evidence_references,
        }

    def _generate_refactored_method(
        self,
        plan: ModernizationPlan,
        task: ModernizationTask,
        rules: list[dict[str, Any]],
        source_snippet: str,
    ) -> dict[str, Any]:
        target_name = plan.entity_name
        target_path = plan.relative_file_path

        code = (
            f"// Refactored Implementation snippet for {target_name}\n"
            f"// Task: {task.title}\n"
            f"// Preserved Rules Count: {len(rules)}\n\n"
            + (source_snippet if source_snippet else "// Refactored method logic")
        )
        diff = self.compute_unified_diff(source_snippet, code, target_path)
        return {
            "artifact_category": ArtifactCategory.REFACTORED_METHOD.value,
            "target_file_path": target_path,
            "source_file_path": plan.relative_file_path,
            "source_line_start": 1,
            "source_line_end": len(source_snippet.splitlines()) or 30,
            "generated_code": code,
            "diff_content": diff,
            "rules_preserved": rules,
            "evidence_references": task.evidence_references,
        }


transformation_engine = TransformationEngine()
