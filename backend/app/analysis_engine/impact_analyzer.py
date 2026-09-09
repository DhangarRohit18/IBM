"""
LEGACYX — Impact Analyzer Engine (Phase 5).

Provides 100% evidence-backed, deterministic impact analysis over Phase 3 structural relationship
graphs and Phase 4 BusinessRule data.

Strict AI Boundary:
This engine establishes all impact nodes, edges, paths, and rule linkages.
AI never invents impact facts.
"""

import enum
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.business_rule import BusinessRule
from app.models.code_entity import CodeEntity
from app.models.code_field import CodeField
from app.models.code_method import CodeMethod
from app.models.code_package import CodePackage
from app.models.code_relationship import CodeRelationship


class ImpactDirection(str, enum.Enum):
    FORWARD = "forward"  # What does this component depend on? (Outgoing dependencies)
    REVERSE = "reverse"  # What components depend on this component? (Incoming callers/dependents)


class ImpactTargetType(str, enum.Enum):
    CLASS = "class"
    METHOD = "method"
    FIELD = "field"
    PACKAGE = "package"
    BUSINESS_RULE = "business_rule"


class ImpactAnalyzer:
    """
    Deterministic Impact Analyzer.
    Traverses Phase 3 structural relationship graph and maps Phase 4 business rules.
    """

    async def analyze(
        self,
        session: AsyncSession,
        analysis_id: str,
        target_type: ImpactTargetType | str,
        target_id: str,
        direction: ImpactDirection | str = ImpactDirection.FORWARD,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        if isinstance(target_type, str):
            target_type = ImpactTargetType(target_type.lower())
        if isinstance(direction, str):
            direction = ImpactDirection(direction.lower())

        max_depth = max(1, min(max_depth, 10))

        # 1. Fetch entities, relationships, and business rules for analysis
        entities_res = await session.execute(
            select(CodeEntity).where(CodeEntity.analysis_id == analysis_id)
        )
        entities = list(entities_res.scalars().all())
        entity_map_by_id = {e.id: e for e in entities}
        entity_map_by_fqn = {e.fully_qualified_name: e for e in entities}
        entity_map_by_name = {e.name: e for e in entities if e.name}

        rels_res = await session.execute(
            select(CodeRelationship).where(CodeRelationship.analysis_id == analysis_id)
        )
        relationships = list(rels_res.scalars().all())

        rules_res = await session.execute(
            select(BusinessRule).where(BusinessRule.analysis_id == analysis_id)
        )
        business_rules = list(rules_res.scalars().all())

        # 2. Resolve target identity
        target_info = await self._resolve_target(
            session=session,
            analysis_id=analysis_id,
            target_type=target_type,
            target_id=target_id,
            entity_map_by_id=entity_map_by_id,
            business_rules=business_rules,
        )

        target_entity_ids: set[str] = set()
        initial_rule_ids: set[str] = set()

        if target_type == ImpactTargetType.CLASS:
            if target_id in entity_map_by_id:
                target_entity_ids.add(target_id)
        elif target_type == ImpactTargetType.METHOD:
            meth_res = await session.execute(
                select(CodeMethod).where(CodeMethod.id == target_id)
            )
            meth = meth_res.scalar_one_or_none()
            if meth and meth.entity_id in entity_map_by_id:
                target_entity_ids.add(meth.entity_id)
        elif target_type == ImpactTargetType.FIELD:
            field_res = await session.execute(
                select(CodeField).where(CodeField.id == target_id)
            )
            field = field_res.scalar_one_or_none()
            if field and field.entity_id in entity_map_by_id:
                target_entity_ids.add(field.entity_id)
        elif target_type == ImpactTargetType.PACKAGE:
            pkg_res = await session.execute(
                select(CodePackage).where(CodePackage.id == target_id)
            )
            pkg = pkg_res.scalar_one_or_none()
            if pkg:
                for e in entities:
                    if e.fully_qualified_name.startswith(pkg.package_name):
                        target_entity_ids.add(e.id)
        elif target_type == ImpactTargetType.BUSINESS_RULE:
            rule_match = next((r for r in business_rules if r.id == target_id), None)
            if rule_match:
                initial_rule_ids.add(rule_match.id)
                if rule_match.entity_id and rule_match.entity_id in entity_map_by_id:
                    target_entity_ids.add(rule_match.entity_id)

        # 3. Perform Graph Traversal (Breadth-First Search)
        visited_nodes: dict[str, int] = {}  # entity_id -> min depth reached
        # Record path parent: node_id -> list of (parent_id, relationship_obj)
        parent_paths: dict[str, list[tuple[str, CodeRelationship]]] = {}

        queue: list[tuple[str, int]] = []
        for start_id in target_entity_ids:
            visited_nodes[start_id] = 0
            queue.append((start_id, 0))

        graph_edges_used: list[dict[str, Any]] = []
        edge_seen_ids: set[str] = set()

        while queue:
            curr_id, curr_depth = queue.pop(0)
            if curr_depth >= max_depth:
                continue

            curr_entity = entity_map_by_id.get(curr_id)
            if not curr_entity:
                continue

            # Find matching relationships
            for rel in relationships:
                next_entity_id: Optional[str] = None

                if direction == ImpactDirection.FORWARD:
                    # Target is outgoing from curr_id
                    if rel.source_entity_id == curr_id:
                        if rel.target_entity_id and rel.target_entity_id in entity_map_by_id:
                            next_entity_id = rel.target_entity_id
                        elif rel.target_entity_name in entity_map_by_fqn:
                            next_entity_id = entity_map_by_fqn[rel.target_entity_name].id
                        elif rel.target_entity_name in entity_map_by_name:
                            next_entity_id = entity_map_by_name[rel.target_entity_name].id
                else:  # REVERSE
                    # Target is incoming to curr_id
                    is_incoming = False
                    if rel.target_entity_id == curr_id:
                        is_incoming = True
                    elif curr_entity.fully_qualified_name and rel.target_entity_name == curr_entity.fully_qualified_name:
                        is_incoming = True
                    elif curr_entity.name and rel.target_entity_name == curr_entity.name:
                        is_incoming = True

                    if is_incoming and rel.source_entity_id in entity_map_by_id:
                        next_entity_id = rel.source_entity_id

                if next_entity_id and next_entity_id != curr_id:
                    next_depth = curr_depth + 1

                    if rel.id not in edge_seen_ids:
                        edge_seen_ids.add(rel.id)
                        graph_edges_used.append({
                            "id": rel.id,
                            "source": rel.source_entity_id,
                            "target": rel.target_entity_id or next_entity_id,
                            "target_name": rel.target_entity_name,
                            "type": rel.relationship_type.value,
                            "line_number": rel.line_number,
                            "relative_file_path": rel.relative_file_path,
                            "source_construct": rel.source_construct,
                            "evidence_reason": rel.evidence_reason,
                            "is_resolved": rel.is_resolved,
                        })

                    if next_entity_id not in parent_paths:
                        parent_paths[next_entity_id] = []
                    parent_paths[next_entity_id].append((curr_id, rel))

                    if next_entity_id not in visited_nodes:
                        visited_nodes[next_entity_id] = next_depth
                        queue.append((next_entity_id, next_depth))

        # 4. Separate Direct vs Transitive Affected Components
        direct_affected_components: list[dict[str, Any]] = []
        transitive_affected_components: list[dict[str, Any]] = []
        node_payloads: list[dict[str, Any]] = []

        for entity_id, depth in visited_nodes.items():
            entity = entity_map_by_id[entity_id]
            is_target = entity_id in target_entity_ids
            is_direct = (depth == 1)

            comp_dict = {
                "id": entity.id,
                "name": entity.name,
                "fully_qualified_name": entity.fully_qualified_name,
                "entity_type": entity.entity_type.value,
                "component_type": entity.component_type.value,
                "relative_file_path": entity.relative_file_path,
                "line_start": entity.line_start,
                "line_end": entity.line_end,
                "depth": depth,
                "is_direct": is_direct,
                "is_target": is_target,
            }

            node_payloads.append(comp_dict)

            if is_target:
                continue

            if is_direct:
                direct_affected_components.append(comp_dict)
            else:
                transitive_affected_components.append(comp_dict)

        # 5. Business Rule Association (Bidirectional)
        direct_affected_rules: list[dict[str, Any]] = []
        transitive_affected_rules: list[dict[str, Any]] = []

        for rule in business_rules:
            rule_dict = {
                "id": rule.id,
                "title": rule.title,
                "rule_type": rule.rule_type if isinstance(rule.rule_type, str) else rule.rule_type.value,
                "status": rule.status if isinstance(rule.status, str) else rule.status.value,
                "relative_file_path": rule.relative_file_path,
                "line_start": rule.line_start,
                "line_end": rule.line_end,
                "entity_id": rule.entity_id,
                "method_id": rule.method_id,
                "condition_expression": rule.condition_expression,
                "action_expression": rule.action_expression,
                "extraction_reason": rule.extraction_reason,
            }

            # Check rule's containing entity in graph traversal
            rule_depth = visited_nodes.get(rule.entity_id) if rule.entity_id else None

            if rule.id in initial_rule_ids:
                rule_dict["is_target"] = True
                rule_dict["depth"] = 0
                direct_affected_rules.append(rule_dict)
            elif rule_depth is not None:
                rule_dict["depth"] = rule_depth
                rule_dict["is_target"] = False
                if rule_depth == 0 or rule_depth == 1:
                    direct_affected_rules.append(rule_dict)
                else:
                    transitive_affected_rules.append(rule_dict)

        # 6. Build Evidenced Impact Paths
        impact_paths: list[dict[str, Any]] = []
        for entity_id, depth in visited_nodes.items():
            if entity_id in target_entity_ids:
                continue
            entity = entity_map_by_id[entity_id]
            # Simple path construct for display
            path_parents = parent_paths.get(entity_id, [])
            for parent_id, rel in path_parents:
                parent_entity = entity_map_by_id.get(parent_id)
                if parent_entity:
                    impact_paths.append({
                        "from_component": parent_entity.name,
                        "from_id": parent_entity.id,
                        "to_component": entity.name,
                        "to_id": entity.id,
                        "relationship_type": rel.relationship_type.value,
                        "depth": depth,
                        "file_path": rel.relative_file_path,
                        "line_number": rel.line_number,
                        "evidence_reason": rel.evidence_reason,
                    })

        # 7. Check "NO EVIDENCED IMPACT" condition
        has_evidenced_impact = bool(
            direct_affected_components or transitive_affected_components or
            direct_affected_rules or transitive_affected_rules
        )
        status_text = "EVIDENCED_IMPACT_FOUND" if has_evidenced_impact else "NO_EVIDENCED_IMPACT"

        return {
            "analysis_id": analysis_id,
            "target": target_info,
            "direction": direction.value,
            "max_depth": max_depth,
            "has_evidenced_impact": has_evidenced_impact,
            "status": status_text,
            "summary": {
                "direct_component_count": len(direct_affected_components),
                "transitive_component_count": len(transitive_affected_components),
                "direct_rule_count": len(direct_affected_rules),
                "transitive_rule_count": len(transitive_affected_rules),
                "total_impacted_nodes": len(visited_nodes),
            },
            "direct_affected_components": direct_affected_components,
            "transitive_affected_components": transitive_affected_components,
            "direct_affected_rules": direct_affected_rules,
            "transitive_affected_rules": transitive_affected_rules,
            "impact_paths": impact_paths,
            "graph": {
                "nodes": node_payloads,
                "edges": graph_edges_used,
            },
        }

    async def _resolve_target(
        self,
        session: AsyncSession,
        analysis_id: str,
        target_type: ImpactTargetType,
        target_id: str,
        entity_map_by_id: dict[str, CodeEntity],
        business_rules: list[BusinessRule],
    ) -> dict[str, Any]:
        info = {
            "id": target_id,
            "type": target_type.value,
            "name": target_id,
            "fully_qualified_name": target_id,
            "file_path": "",
            "description": "",
        }

        if target_type == ImpactTargetType.CLASS:
            entity = entity_map_by_id.get(target_id)
            if entity:
                info["name"] = entity.name
                info["fully_qualified_name"] = entity.fully_qualified_name
                info["file_path"] = entity.relative_file_path
                info["description"] = f"{entity.component_type.value} Class"

        elif target_type == ImpactTargetType.METHOD:
            res = await session.execute(select(CodeMethod).where(CodeMethod.id == target_id))
            meth = res.scalar_one_or_none()
            if meth:
                info["name"] = meth.name
                info["fully_qualified_name"] = f"{meth.signature}"
                info["file_path"] = meth.relative_file_path
                info["description"] = f"Method ({meth.return_type})"

        elif target_type == ImpactTargetType.FIELD:
            res = await session.execute(select(CodeField).where(CodeField.id == target_id))
            field = res.scalar_one_or_none()
            if field:
                info["name"] = field.name
                info["fully_qualified_name"] = f"{field.field_type} {field.name}"
                info["file_path"] = field.relative_file_path
                info["description"] = f"Field of type {field.field_type}"

        elif target_type == ImpactTargetType.PACKAGE:
            res = await session.execute(select(CodePackage).where(CodePackage.id == target_id))
            pkg = res.scalar_one_or_none()
            if pkg:
                info["name"] = pkg.package_name
                info["fully_qualified_name"] = pkg.package_name
                info["description"] = f"Package with {pkg.class_count} classes"

        elif target_type == ImpactTargetType.BUSINESS_RULE:
            rule = next((r for r in business_rules if r.id == target_id), None)
            if rule:
                info["name"] = rule.title
                info["fully_qualified_name"] = rule.title
                info["file_path"] = rule.relative_file_path
                info["description"] = f"Business Rule ({rule.rule_type})"

        return info


impact_analyzer = ImpactAnalyzer()
