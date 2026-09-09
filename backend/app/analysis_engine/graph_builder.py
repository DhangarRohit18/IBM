"""
LEGACYX — Architecture Graph Builder (Phase 3).

Generates a focused, queryable architecture graph representation derived strictly from
deterministic analysis entities and relationships.

Node Types: CLASS, INTERFACE, ENUM
Edge Types: IMPORTS, EXTENDS, IMPLEMENTS, DEPENDS_ON, CALLS
"""

from typing import Any
from app.models.code_entity import CodeEntity
from app.models.code_relationship import CodeRelationship


class ArchitectureGraphBuilder:
    """Builds node and edge structures for visual architecture rendering."""

    def build_graph(
        self,
        entities: list[CodeEntity],
        relationships: list[CodeRelationship],
        package_filter: str | None = None,
        component_filter: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Construct nodes and edges for the System X-Ray architecture graph."""
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        entity_id_set = set()

        for entity in entities:
            # Filter nodes by package or component type if specified
            if package_filter and not entity.fully_qualified_name.startswith(package_filter):
                continue
            if component_filter and entity.component_type.value != component_filter:
                continue

            entity_id_set.add(entity.id)
            nodes.append(
                {
                    "id": entity.id,
                    "name": entity.name,
                    "fully_qualified_name": entity.fully_qualified_name,
                    "entity_type": entity.entity_type.value,
                    "component_type": entity.component_type.value,
                    "relative_file_path": entity.relative_file_path,
                    "line_start": entity.line_start,
                    "line_end": entity.line_end,
                    "classification_evidence": entity.classification_evidence,
                }
            )

        for rel in relationships:
            # Only include edges between visible nodes in filtered set
            if rel.source_entity_id not in entity_id_set:
                continue
            if rel.target_entity_id and rel.target_entity_id not in entity_id_set:
                continue

            edges.append(
                {
                    "id": rel.id,
                    "source": rel.source_entity_id,
                    "target": rel.target_entity_id or rel.target_entity_name,
                    "target_name": rel.target_entity_name,
                    "type": rel.relationship_type.value,
                    "line_number": rel.line_number,
                    "source_construct": rel.source_construct,
                    "evidence_reason": rel.evidence_reason,
                    "is_resolved": rel.is_resolved,
                }
            )

        return {"nodes": nodes, "edges": edges}
