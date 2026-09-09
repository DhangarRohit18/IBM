"""
LEGACYX — Evidence-Backed Component Classifier (Phase 3).

Categorizes Java entities into component roles:
- CONTROLLER
- SERVICE
- REPOSITORY
- MODEL
- CONFIG
- UTILITY
- OTHER

STRICT RULE (AGENTS.md & Phase 3 Contract):
- Every classification MUST be backed by concrete evidence strings.
- Absolutely NO confidence scores, percentages, or AI hallucinations.
"""

from dataclasses import dataclass, field
from app.analysis_engine.java_parser import ParsedTypeEntity
from app.models.code_entity import ComponentType


@dataclass
class ClassificationResult:
    component_type: ComponentType
    evidence: list[str] = field(default_factory=list)


class ComponentClassifier:
    """Classifies Java types into component roles using deterministic static rules."""

    def classify(self, entity: ParsedTypeEntity) -> tuple[ComponentType, list[str]]:
        res = self.classify_entity(entity)
        return res.component_type, res.evidence

    def classify_entity(self, entity: ParsedTypeEntity) -> ClassificationResult:
        """Evaluate entity annotations, interfaces, extends, and naming to classify role."""
        evidence: list[str] = []

        annotation_names = {ann.name for ann in entity.annotations}
        name_lower = entity.name.lower()
        package_lower = entity.package_name.lower()

        # ── 1. Controller ──────────────────────────────────────────────────────
        if "RestController" in annotation_names or "Controller" in annotation_names:
            evidence.append("Annotated with @Controller or @RestController")
            if "RequestMapping" in annotation_names or any(
                a.endswith("Mapping") for a in annotation_names
            ):
                evidence.append("Contains Spring MVC request mapping annotations")
            return ClassificationResult(ComponentType.CONTROLLER, evidence)

        if "controller" in package_lower or name_lower.endswith("controller"):
            evidence.append("Class name or package indicates web controller component")
            return ClassificationResult(ComponentType.CONTROLLER, evidence)

        # ── 2. Service ─────────────────────────────────────────────────────────
        if "Service" in annotation_names:
            evidence.append("Annotated with Spring @Service annotation")
            return ClassificationResult(ComponentType.SERVICE, evidence)

        if "service" in package_lower or name_lower.endswith("service"):
            evidence.append(f"Name '{entity.name}' or package '{entity.package_name}' indicates service layer")
            return ClassificationResult(ComponentType.SERVICE, evidence)

        # ── 3. Repository / DAO ────────────────────────────────────────────────
        if "Repository" in annotation_names:
            evidence.append("Annotated with Spring @Repository annotation")
            return ClassificationResult(ComponentType.REPOSITORY, evidence)

        if entity.extends_name and "JpaRepository" in entity.extends_name:
            evidence.append("Extends JpaRepository interface")
            return ClassificationResult(ComponentType.REPOSITORY, evidence)

        if any("Repository" in impl or "Dao" in impl for impl in entity.implements_names):
            evidence.append(f"Implements persistence interface: {', '.join(entity.implements_names)}")
            return ClassificationResult(ComponentType.REPOSITORY, evidence)

        if "repository" in package_lower or "dao" in package_lower or name_lower.endswith("repository") or name_lower.endswith("dao"):
            evidence.append("Name or package indicates data access component")
            return ClassificationResult(ComponentType.REPOSITORY, evidence)

        # ── 4. Model / Entity / DTO ───────────────────────────────────────────
        if "Entity" in annotation_names or "Table" in annotation_names or "Embeddable" in annotation_names:
            evidence.append("Annotated with JPA @Entity, @Table, or @Embeddable")
            return ClassificationResult(ComponentType.MODEL, evidence)

        if "model" in package_lower or "domain" in package_lower or "dto" in package_lower or name_lower.endswith("dto") or name_lower.endswith("entity"):
            evidence.append("Package or class naming indicates domain model or DTO entity")
            return ClassificationResult(ComponentType.MODEL, evidence)

        # ── 5. Configuration ───────────────────────────────────────────────────
        if "Configuration" in annotation_names or "SpringBootApplication" in annotation_names:
            evidence.append("Annotated with @Configuration or @SpringBootApplication")
            return ClassificationResult(ComponentType.CONFIG, evidence)

        if "config" in package_lower or name_lower.endswith("config") or name_lower.endswith("configuration"):
            evidence.append("Package or name indicates Spring configuration component")
            return ClassificationResult(ComponentType.CONFIG, evidence)

        # ── 6. Utility ─────────────────────────────────────────────────────────
        if "util" in package_lower or name_lower.endswith("util") or name_lower.endswith("utils") or name_lower.endswith("helper"):
            evidence.append("Package or name indicates utility/helper component")
            return ClassificationResult(ComponentType.UTILITY, evidence)

        # Default fallback
        evidence.append("No specific framework annotations or stereotype naming matched")
        return ClassificationResult(ComponentType.OTHER, evidence)
