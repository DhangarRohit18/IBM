"""
LEGACYX — Technology Detector (Phase 2).

Performs deterministic, evidence-backed technology detection for:
- Java (*.java files)
- Maven (pom.xml presence)
- Gradle (build.gradle, build.gradle.kts presence)
- Spring Framework / Spring Boot (Spring dependencies/annotations in build & config files)

AI is NEVER used for technology detection (AGENTS.md §2.1 & Phase 2 contract).
Every detected technology MUST include an evidence array.
"""

from dataclasses import dataclass, field
from pathlib import Path

from app.services.ingestion.indexer import IndexedFileItem


@dataclass
class TechnologyEvidence:
    name: str
    evidence: list[str] = field(default_factory=list)


class TechnologyDetector:
    """Detects technologies deterministically using file index items and file contents."""

    def detect_technologies(
        self, target_dir: Path, indexed_items: list[IndexedFileItem]
    ) -> list[TechnologyEvidence]:
        """Examine indexed items and project configuration files to detect technologies."""
        technologies: list[TechnologyEvidence] = []
        target_dir = target_dir.resolve()

        # ── 1. Java Detection ──────────────────────────────────────────────────
        java_files = [item for item in indexed_items if not item.is_directory and item.extension == "java"]
        if java_files:
            sample_file = java_files[0].relative_path
            technologies.append(
                TechnologyEvidence(
                    name="Java",
                    evidence=[
                        f"{len(java_files)} .java files discovered",
                        f"Example: {sample_file}",
                    ],
                )
            )

        # ── 2. Maven Detection ─────────────────────────────────────────────────
        maven_files = [
            item for item in indexed_items if not item.is_directory and item.filename.lower() == "pom.xml"
        ]
        if maven_files:
            technologies.append(
                TechnologyEvidence(
                    name="Maven",
                    evidence=[f"Build descriptor found: {m.relative_path}" for m in maven_files],
                )
            )

        # ── 3. Gradle Detection ────────────────────────────────────────────────
        gradle_files = [
            item
            for item in indexed_items
            if not item.is_directory
            and item.filename.lower() in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")
        ]
        if gradle_files:
            technologies.append(
                TechnologyEvidence(
                    name="Gradle",
                    evidence=[f"Build descriptor found: {g.relative_path}" for g in gradle_files],
                )
            )

        # ── 4. Spring / Spring Boot Detection ──────────────────────────────────
        spring_evidence: list[str] = []

        # Check build files for spring dependencies
        for item in indexed_items:
            if item.is_directory:
                continue

            fname_lower = item.filename.lower()
            if fname_lower in ("pom.xml", "build.gradle", "build.gradle.kts"):
                file_path = target_dir / item.relative_path
                if file_path.exists():
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if "spring-boot" in content or "springframework" in content:
                            spring_evidence.append(
                                f"Spring dependency detected in build file: {item.relative_path}"
                            )
                    except Exception:
                        pass

            # Check configuration files
            if fname_lower in ("application.properties", "application.yml", "application.yaml") or (
                fname_lower.endswith(".xml") and "spring" in fname_lower
            ):
                spring_evidence.append(f"Spring configuration file found: {item.relative_path}")

        # Also check for @SpringBootApplication or @Component in Java files if sample available
        if not spring_evidence and java_files:
            for item in java_files[:10]:  # Sample first 10 Java files
                file_path = target_dir / item.relative_path
                if file_path.exists():
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if "@SpringBootApplication" in content or "import org.springframework" in content:
                            spring_evidence.append(
                                f"Spring annotations/imports found in source: {item.relative_path}"
                            )
                            break
                    except Exception:
                        pass

        if spring_evidence:
            technologies.append(
                TechnologyEvidence(name="Spring", evidence=spring_evidence)
            )

        return technologies
