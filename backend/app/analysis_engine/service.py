"""
LEGACYX — Analysis Service Orchestrator (Phase 3).

Orchestrates the System X-Ray static analysis pipeline:
1. Load extracted repository files
2. Parse Java source files into AST entities via JavaASTParser
3. Classify components with ComponentClassifier (evidence-backed)
4. Resolve structural relationships via RelationshipResolver (conservative)
5. Persist AnalysisRun, CodePackage, CodeEntity, CodeMethod, CodeField, CodeRelationship records
6. Emit structured audit logs
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.analysis_engine.classifier import ComponentClassifier
from app.analysis_engine.java_parser import JavaASTParser, ParsedTypeEntity
from app.analysis_engine.resolver import RelationshipResolver
from app.analysis_engine.rule_extractor import BusinessRuleExtractor
from app.analysis_engine.state_machine import validate_analysis_transition
from app.core.logging import get_logger
from app.core.storage import LocalStorageProvider
from app.models.analysis_run import AnalysisRun, AnalysisRunStatus
from app.models.business_rule import BusinessRule
from app.models.code_entity import CodeEntity, EntityType
from app.models.code_field import CodeField
from app.models.code_method import CodeMethod
from app.models.code_package import CodePackage
from app.models.code_relationship import CodeRelationship, RelationshipType
from app.models.project import Project, ProjectStatus
from app.models.repository import Repository, RepositoryStatus
from app.models.repository_file import RepositoryFile

logger = get_logger(__name__)


class AnalysisService:
    """Orchestrates static analysis execution and persistence."""

    def __init__(self, storage_provider: LocalStorageProvider | None = None) -> None:
        self.storage = storage_provider or LocalStorageProvider()
        self.parser = JavaASTParser()
        self.classifier = ComponentClassifier()
        self.resolver = RelationshipResolver()

    async def create_analysis_run(
        self, session: AsyncSession, repository: Repository
    ) -> AnalysisRun:
        """Initialize an AnalysisRun DB record in PENDING state."""
        run = AnalysisRun(
            repository_id=repository.id,
            status=AnalysisRunStatus.PENDING,
            parser_name="javalang",
            parser_version="0.13.0",
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    async def run_analysis(
        self, session: AsyncSession, repository_id: str, extracted_path: Any = None
    ) -> AnalysisRun:
        """Helper to create run record and execute analysis pipeline in one step."""
        stmt_repo = select(Repository).where(Repository.id == repository_id)
        res = await session.execute(stmt_repo)
        repo = res.scalar_one_or_none()
        if not repo:
            raise ValueError(f"Repository '{repository_id}' not found")

        if extracted_path:
            repo.extracted_path = str(extracted_path)
            session.add(repo)
            await session.commit()

        run = await self.create_analysis_run(session, repo)
        run, _ = await self.run_analysis_pipeline(session, repo.id, run.id)
        return run

    async def run_analysis_pipeline(
        self, session: AsyncSession, repository_id: str, analysis_run_id: str
    ) -> tuple[AnalysisRun, list[CodeEntity]]:
        """Run the complete deterministic static analysis pipeline."""
        stmt_repo = select(Repository).where(Repository.id == repository_id)
        res_repo = await session.execute(stmt_repo)
        repository = res_repo.scalar_one_or_none()
        if not repository:
            raise ValueError(f"Repository '{repository_id}' not found")

        stmt_run = select(AnalysisRun).where(AnalysisRun.id == analysis_run_id)
        res_run = await session.execute(stmt_run)
        analysis_run = res_run.scalar_one_or_none()
        if not analysis_run:
            raise ValueError(f"AnalysisRun '{analysis_run_id}' not found")

        # Update Project status to ANALYZING
        stmt_proj = select(Project).where(Project.id == repository.project_id)
        res_proj = await session.execute(stmt_proj)
        project = res_proj.scalar_one_or_none()

        try:
            # ── 1. Transition: RUNNING ─────────────────────────────────────────
            validate_analysis_transition(analysis_run.status, AnalysisRunStatus.RUNNING)
            analysis_run.status = AnalysisRunStatus.RUNNING
            if project:
                project.status = ProjectStatus.ANALYZING
            await session.commit()

            logger.info("analysis.started", repository_id=repository_id, run_id=analysis_run_id)

            extracted_dir = Path(repository.extracted_path) if repository.extracted_path else self.storage.get_extracted_path(repository.id)

            # ── 2. Discover Java source files ──────────────────────────────────
            stmt_files = select(RepositoryFile).where(
                RepositoryFile.repository_id == repository_id,
                RepositoryFile.extension == "java",
                RepositoryFile.is_directory == False,
            )
            res_files = await session.execute(stmt_files)
            java_files = res_files.scalars().all()

            all_parsed_entities: list[ParsedTypeEntity] = []
            files_analyzed = 0

            if java_files:
                for repo_file in java_files:
                    file_path = extracted_dir / repo_file.relative_path
                    if file_path.exists():
                        parsed_list = self.parser.parse_file(file_path, repo_file.relative_path)
                        all_parsed_entities.extend(parsed_list)
                        files_analyzed += 1
            elif extracted_dir.exists():
                for p in extracted_dir.rglob("*.java"):
                    if p.is_file():
                        rel = str(p.relative_to(extracted_dir)).replace("\\", "/")
                        parsed_list = self.parser.parse_file(p, rel)
                        all_parsed_entities.extend(parsed_list)
                        files_analyzed += 1

            logger.info(
                "analysis.parsing_completed",
                files_analyzed=files_analyzed,
                entities_discovered=len(all_parsed_entities),
            )

            # ── 3. Resolve Structural Packages ────────────────────────────────
            package_names = {e.package_name for e in all_parsed_entities if e.package_name}
            pkg_db_map: dict[str, CodePackage] = {}

            for pkg_name in package_names:
                pkg_obj = CodePackage(
                    analysis_id=analysis_run.id,
                    repository_id=repository.id,
                    name=pkg_name,
                )
                session.add(pkg_obj)
                pkg_db_map[pkg_name] = pkg_obj

            await session.flush()

            # ── 4. Classify & Create Entities ─────────────────────────────────
            entity_db_map: dict[str, CodeEntity] = {}
            classes_count = 0
            interfaces_count = 0
            enums_count = 0
            methods_count = 0
            fields_count = 0

            for parsed_e in all_parsed_entities:
                classification = self.classifier.classify_entity(parsed_e)
                pkg_obj = pkg_db_map.get(parsed_e.package_name)

                e_type = (
                    EntityType.INTERFACE
                    if parsed_e.entity_type == "INTERFACE"
                    else EntityType.ENUM
                    if parsed_e.entity_type == "ENUM"
                    else EntityType.CLASS
                )

                if e_type == EntityType.CLASS:
                    classes_count += 1
                elif e_type == EntityType.INTERFACE:
                    interfaces_count += 1
                else:
                    enums_count += 1

                entity_obj = CodeEntity(
                    analysis_id=analysis_run.id,
                    repository_id=repository.id,
                    package_id=pkg_obj.id if pkg_obj else None,
                    entity_type=e_type,
                    name=parsed_e.name,
                    fully_qualified_name=parsed_e.fully_qualified_name,
                    relative_file_path=parsed_e.relative_file_path,
                    line_start=parsed_e.line_start,
                    line_end=parsed_e.line_end,
                    extends_name=parsed_e.extends_name,
                    implements_names=parsed_e.implements_names,
                    annotations=[{"name": a.name, "element_pairs": a.element_pairs} for a in parsed_e.annotations],
                    modifiers=parsed_e.modifiers,
                    component_type=classification.component_type,
                    classification_evidence=classification.evidence,
                )
                session.add(entity_obj)
                entity_db_map[parsed_e.fully_qualified_name] = entity_obj

            await session.flush()

            # ── 5. Add Methods & Fields ────────────────────────────────────────
            for parsed_e in all_parsed_entities:
                entity_obj = entity_db_map.get(parsed_e.fully_qualified_name)
                if not entity_obj:
                    continue

                for m in parsed_e.methods:
                    method_obj = CodeMethod(
                        entity_id=entity_obj.id,
                        analysis_id=analysis_run.id,
                        name=m.name,
                        return_type=m.return_type,
                        parameters=m.parameters,
                        modifiers=m.modifiers,
                        annotations=[{"name": a.name, "element_pairs": a.element_pairs} for a in m.annotations],
                        is_constructor=m.is_constructor,
                        line_start=m.line_start,
                        line_end=m.line_end,
                    )
                    session.add(method_obj)
                    methods_count += 1

                for f in parsed_e.fields:
                    field_obj = CodeField(
                        entity_id=entity_obj.id,
                        analysis_id=analysis_run.id,
                        name=f.name,
                        field_type=f.field_type,
                        modifiers=f.modifiers,
                        annotations=[{"name": a.name, "element_pairs": a.element_pairs} for a in f.annotations],
                        line_start=f.line_start,
                        line_end=f.line_end,
                    )
                    session.add(field_obj)
                    fields_count += 1

            await session.flush()

            # ── 6. Resolve Relationships ───────────────────────────────────────
            resolved_rels = self.resolver.resolve_relationships(all_parsed_entities)
            relationships_count = len(resolved_rels)

            for rel in resolved_rels:
                src_entity = entity_db_map.get(rel.source_entity_name)
                tgt_entity = entity_db_map.get(rel.target_entity_name)

                if src_entity:
                    rel_obj = CodeRelationship(
                        analysis_id=analysis_run.id,
                        source_entity_id=src_entity.id,
                        target_entity_id=tgt_entity.id if tgt_entity else None,
                        target_entity_name=rel.target_entity_name,
                        relationship_type=rel.relationship_type,
                        relative_file_path=rel.relative_file_path,
                        line_number=rel.line_number,
                        source_construct=rel.source_construct,
                        evidence_reason=rel.evidence_reason,
                        is_resolved=rel.is_resolved,
                    )
                    session.add(rel_obj)

            # ── 7. Extract Deterministic Business Rules ──────────────────────
            rule_extractor = BusinessRuleExtractor()
            for parsed_e in all_parsed_entities:
                entity_obj = entity_db_map.get(parsed_e.fully_qualified_name)
                if not entity_obj or not parsed_e.ast_tree:
                    continue

                file_path = extracted_dir / parsed_e.relative_file_path
                file_lines: list[str] = []
                if file_path.exists():
                    try:
                        file_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    except Exception:
                        pass

                rule_payloads = rule_extractor.extract_rules_from_ast(
                    analysis_id=analysis_run.id,
                    repository_id=repository.id,
                    entity_id=entity_obj.id,
                    method_id=None,
                    relative_file_path=parsed_e.relative_file_path,
                    ast_tree=parsed_e.ast_tree,
                    file_lines=file_lines,
                )

                for payload in rule_payloads:
                    rule_obj = BusinessRule(**payload)
                    session.add(rule_obj)

            await session.flush()

            # ── 7b. Automatically Synthesize Decision Contracts from Rules ───
            try:
                from app.assurance.contract_engine import contract_engine
                await contract_engine.generate_contracts_from_rules(
                    analysis_id=analysis_run.id,
                    repository_id=repository.id,
                    db=session,
                )
            except Exception as contract_err:
                logger.warning("analysis.contracts_synthesis_warning", error=str(contract_err))

            # ── 8. Transition: COMPLETED ───────────────────────────────────────
            validate_analysis_transition(analysis_run.status, AnalysisRunStatus.COMPLETED)
            analysis_run.status = AnalysisRunStatus.COMPLETED
            analysis_run.files_analyzed = files_analyzed
            analysis_run.packages_count = len(package_names)
            analysis_run.classes_count = classes_count
            analysis_run.interfaces_count = interfaces_count
            analysis_run.enums_count = enums_count
            analysis_run.methods_count = methods_count
            analysis_run.fields_count = fields_count
            analysis_run.relationships_count = relationships_count
            analysis_run.completed_at = datetime.now(timezone.utc)

            if project:
                project.status = ProjectStatus.ANALYZED

            await session.commit()
            await session.refresh(analysis_run)

            logger.info(
                "analysis.completed",
                repository_id=repository_id,
                classes=classes_count,
                interfaces=interfaces_count,
                methods=methods_count,
                relationships=relationships_count,
            )

            return analysis_run, list(entity_db_map.values())

        except Exception as exc:
            await session.rollback()
            analysis_run.status = AnalysisRunStatus.FAILED
            analysis_run.error_code = "ANALYSIS_EXECUTION_ERROR"
            analysis_run.error_message = str(exc)
            if project:
                project.status = ProjectStatus.FAILED
            await session.commit()
            logger.error("analysis.failed", repository_id=repository_id, error=str(exc))
            raise

    async def get_summary(self, session: AsyncSession, analysis_id: str) -> dict[str, Any]:
        """Get high level metrics and breakdown summary for an analysis run."""
        stmt_run = select(AnalysisRun).where(AnalysisRun.id == analysis_id)
        res_run = await session.execute(stmt_run)
        run = res_run.scalar_one_or_none()
        if not run:
            return {}

        stmt_entities = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
        res_entities = await session.execute(stmt_entities)
        entities = res_entities.scalars().all()

        breakdown: dict[str, int] = {}
        for e in entities:
            comp_val = e.component_type.value
            breakdown[comp_val] = breakdown.get(comp_val, 0) + 1

        return {
            "analysis_id": run.id,
            "total_files": run.files_analyzed,
            "total_packages": run.packages_count,
            "total_entities": len(entities),
            "total_classes": run.classes_count + run.interfaces_count + run.enums_count,
            "classes_count": run.classes_count,
            "interfaces_count": run.interfaces_count,
            "component_breakdown": breakdown,
        }

    async def get_graph(self, session: AsyncSession, analysis_id: str) -> dict[str, Any]:
        """Get graph representation of entities and relationships."""
        stmt_entities = select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
        res_entities = await session.execute(stmt_entities)
        entities = res_entities.scalars().all()

        stmt_rels = select(CodeRelationship).where(CodeRelationship.analysis_id == analysis_id)
        res_rels = await session.execute(stmt_rels)
        rels = res_rels.scalars().all()

        from app.analysis_engine.graph_builder import ArchitectureGraphBuilder

        builder = ArchitectureGraphBuilder()
        return builder.build_graph(entities, rels)

    async def search_entities(self, session: AsyncSession, analysis_id: str, query: str) -> dict[str, Any]:
        """Search structural entities by name."""
        stmt_classes = select(CodeEntity).where(
            CodeEntity.analysis_id == analysis_id,
            CodeEntity.name.ilike(f"%{query}%")
        )
        res_classes = await session.execute(stmt_classes)
        classes = res_classes.scalars().all()

        stmt_methods = select(CodeMethod).where(
            CodeMethod.analysis_id == analysis_id,
            CodeMethod.name.ilike(f"%{query}%")
        )
        res_methods = await session.execute(stmt_methods)
        methods = res_methods.scalars().all()

        return {"classes": classes, "methods": methods, "fields": []}
