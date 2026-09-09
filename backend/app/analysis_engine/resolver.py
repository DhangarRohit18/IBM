"""
LEGACYX — Conservative Relationship & Call Resolver (Phase 3).

Resolves structural relationships:
- IMPORTS: Import declarations
- EXTENDS: Class inheritance
- IMPLEMENTS: Interface implementation
- DEPENDS_ON: Field declarations, constructor parameters, return types
- CALLS: Method call sites

CONSERVATIVE RESOLUTION PRINCIPLE (AGENTS.md & Phase 3 Contract):
- Accuracy is paramount. False positives are strictly worse than unresolved relationships.
- When a method invocation target cannot be resolved unambiguously to a single entity,
  it MUST be recorded as unresolved (`is_resolved=False`) with preserved line number and call site evidence.
- Never fabricate a relationship or guess a target.
"""

from dataclasses import dataclass, field
from typing import Any

from app.analysis_engine.java_parser import ParsedTypeEntity
from app.models.code_relationship import RelationshipType


@dataclass
class ResolvedRelationship:
    source_entity_name: str
    source_method_name: str | None
    target_entity_name: str
    relationship_type: RelationshipType
    relative_file_path: str
    line_number: int
    source_construct: str
    evidence_reason: str
    is_resolved: bool = True


class RelationshipResolver:
    """Resolves deterministic structural relationships from parsed Java AST entities."""

    def resolve_relationships(
        self, entities: list[ParsedTypeEntity]
    ) -> list[ResolvedRelationship]:
        """Process entities and produce a list of ResolvedRelationship records."""
        relationships: list[ResolvedRelationship] = []

        # Build symbol map of fully qualified names and simple names to entities
        fqn_map: dict[str, ParsedTypeEntity] = {e.fully_qualified_name: e for e in entities}
        simple_name_map: dict[str, list[ParsedTypeEntity]] = {}
        for e in entities:
            simple_name_map.setdefault(e.name, []).append(e)

        for entity in entities:
            # ── 1. IMPORTS Relationships ───────────────────────────────────────
            for imp in entity.imports:
                relationships.append(
                    ResolvedRelationship(
                        source_entity_name=entity.fully_qualified_name,
                        source_method_name=None,
                        target_entity_name=imp,
                        relationship_type=RelationshipType.IMPORTS,
                        relative_file_path=entity.relative_file_path,
                        line_number=entity.line_start,
                        source_construct=f"import {imp};",
                        evidence_reason=f"Explicit import statement in {entity.name}",
                        is_resolved=imp in fqn_map,
                    )
                )

            # ── 2. EXTENDS Relationships ───────────────────────────────────────
            if entity.extends_name:
                target_name = entity.extends_name
                resolved_target = self._resolve_type_name(target_name, entity, fqn_map, simple_name_map)
                relationships.append(
                    ResolvedRelationship(
                        source_entity_name=entity.fully_qualified_name,
                        source_method_name=None,
                        target_entity_name=resolved_target or target_name,
                        relationship_type=RelationshipType.EXTENDS,
                        relative_file_path=entity.relative_file_path,
                        line_number=entity.line_start,
                        source_construct=f"class {entity.name} extends {target_name}",
                        evidence_reason=f"Class inheritance: {entity.name} extends {target_name}",
                        is_resolved=resolved_target is not None,
                    )
                )

            # ── 3. IMPLEMENTS Relationships ────────────────────────────────────
            for impl in entity.implements_names:
                resolved_target = self._resolve_type_name(impl, entity, fqn_map, simple_name_map)
                relationships.append(
                    ResolvedRelationship(
                        source_entity_name=entity.fully_qualified_name,
                        source_method_name=None,
                        target_entity_name=resolved_target or impl,
                        relationship_type=RelationshipType.IMPLEMENTS,
                        relative_file_path=entity.relative_file_path,
                        line_number=entity.line_start,
                        source_construct=f"implements {impl}",
                        evidence_reason=f"Interface implementation: {entity.name} implements {impl}",
                        is_resolved=resolved_target is not None,
                    )
                )

            # ── 4. DEPENDS_ON Relationships (Field Injection / Declaration) ───
            for f in entity.fields:
                fieldType = f.field_type
                if fieldType in ("int", "long", "double", "float", "boolean", "char", "byte", "short", "String"):
                    continue

                resolved_target = self._resolve_type_name(fieldType, entity, fqn_map, simple_name_map)
                relationships.append(
                    ResolvedRelationship(
                        source_entity_name=entity.fully_qualified_name,
                        source_method_name=None,
                        target_entity_name=resolved_target or fieldType,
                        relationship_type=RelationshipType.DEPENDS_ON,
                        relative_file_path=entity.relative_file_path,
                        line_number=f.line_start,
                        source_construct=f"private {fieldType} {f.name};",
                        evidence_reason=f"Field dependency: {entity.name} has member field of type {fieldType}",
                        is_resolved=resolved_target is not None,
                    )
                )

            # ── 5. CALLS Relationships (Method Invocations) ───────────────────
            for m in entity.methods:
                for inv in m.method_invocations:
                    method_name = inv.get("method_name", "")
                    qualifier = inv.get("qualifier") or inv.get("target_expression") or ""
                    line_no = inv.get("line_number", m.line_start)

                    target_entity_name: str | None = None
                    is_resolved = False
                    reason = ""

                    if not qualifier or qualifier == "this":
                        target_entity_name = entity.fully_qualified_name
                        is_resolved = True
                        reason = f"Self/internal method call: {entity.name}.{method_name}()"
                    else:
                        # Try to match qualifier against field names in entity
                        matching_field = next((f for f in entity.fields if f.name == qualifier), None)
                        if matching_field:
                            target_entity_name = self._resolve_type_name(
                                matching_field.field_type, entity, fqn_map, simple_name_map
                            )
                            if target_entity_name:
                                is_resolved = True
                                reason = f"Field method call via member '{qualifier}' of type {matching_field.field_type}"
                            else:
                                target_entity_name = f"{matching_field.field_type}.{method_name}"
                                is_resolved = False
                                reason = f"Unresolved target entity for field '{qualifier}' of type {matching_field.field_type}"
                        else:
                            # Try to match qualifier as a class name
                            target_entity_name = self._resolve_type_name(qualifier, entity, fqn_map, simple_name_map)
                            if target_entity_name:
                                is_resolved = True
                                reason = f"Static or type-qualified method call: {qualifier}.{method_name}()"
                            else:
                                # Conservative resolution: mark unresolved
                                target_entity_name = f"{qualifier}.{method_name}"
                                is_resolved = False
                                reason = f"Ambiguous method call site on variable/qualifier '{qualifier}'"

                    relationships.append(
                        ResolvedRelationship(
                            source_entity_name=entity.fully_qualified_name,
                            source_method_name=m.name,
                            target_entity_name=target_entity_name or f"{qualifier}.{method_name}",
                            relationship_type=RelationshipType.CALLS,
                            relative_file_path=entity.relative_file_path,
                            line_number=line_no,
                            source_construct=f"{qualifier}.{method_name}()" if qualifier else f"{method_name}()",
                            evidence_reason=reason,
                            is_resolved=is_resolved,
                        )
                    )

        return relationships

    def _resolve_type_name(
        self,
        type_name: str,
        current_entity: ParsedTypeEntity,
        fqn_map: dict[str, ParsedTypeEntity],
        simple_name_map: dict[str, list[ParsedTypeEntity]],
    ) -> str | None:
        """Resolve a simple or qualified type name to a fully qualified name."""
        # 1. Direct FQN match
        if type_name in fqn_map:
            return type_name

        # 2. Same package match
        same_pkg_fqn = f"{current_entity.package_name}.{type_name}" if current_entity.package_name else type_name
        if same_pkg_fqn in fqn_map:
            return same_pkg_fqn

        # 3. Match from import statements
        for imp in current_entity.imports:
            if imp.endswith(f".{type_name}"):
                return imp

        # 4. Simple name lookup if unique
        candidates = simple_name_map.get(type_name, [])
        if len(candidates) == 1:
            return candidates[0].fully_qualified_name

        return None
