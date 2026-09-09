"""
LEGACYX — Java Source AST Parser (Phase 3).

Uses javalang (0.13.0) to parse Java source files into AST structures and extract:
- Package declarations
- Type declarations (Class, Interface, Enum)
- Inheritance (extends) & interface implementations (implements)
- Annotations decorated on types, methods, fields
- Field declarations with type signatures and line boundaries
- Method & constructor declarations with signatures and line boundaries
- Method invocation call sites with exact line numbers
- Imports list

Gracefully handles syntax errors without silent fact fabrication.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import javalang
from javalang.tree import (
    Annotation,
    ClassDeclaration,
    ConstructorDeclaration,
    EnumDeclaration,
    FieldDeclaration,
    Import,
    InterfaceDeclaration,
    MethodDeclaration,
    MethodInvocation,
)

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedAnnotation:
    name: str
    element_pairs: dict[str, str] = field(default_factory=dict)


@dataclass
class ParsedField:
    name: str
    field_type: str
    modifiers: list[str]
    annotations: list[ParsedAnnotation]
    line_start: int
    line_end: int


@dataclass
class ParsedMethod:
    name: str
    return_type: str
    parameters: list[dict[str, str]]
    modifiers: list[str]
    annotations: list[ParsedAnnotation]
    is_constructor: bool
    line_start: int
    line_end: int
    method_invocations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ParsedTypeEntity:
    name: str
    entity_type: str  # CLASS, INTERFACE, ENUM
    package_name: str
    fully_qualified_name: str
    relative_file_path: str
    line_start: int
    line_end: int
    extends_name: str | None
    implements_names: list[str]
    annotations: list[ParsedAnnotation]
    modifiers: list[str]
    fields: list[ParsedField]
    methods: list[ParsedMethod]
    imports: list[str]
    ast_tree: Any = None


class JavaASTParser:
    """Parses Java source files into structured AST entities."""

    def parse_file(self, file_path: Path, relative_file_path: str) -> list[ParsedTypeEntity]:
        """Parse a single Java file and return its type entities."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            tree = javalang.parse.parse(content)
        except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError) as exc:
            logger.warning(
                "analysis.file_parse_error",
                file_path=relative_file_path,
                error=str(exc),
            )
            return []
        except Exception as exc:
            logger.error(
                "analysis.file_parse_unexpected_error",
                file_path=relative_file_path,
                error=str(exc),
            )
            return []

        package_name = tree.package.name if tree.package else ""
        imports = [imp.path for imp in tree.imports] if tree.imports else []
        file_lines = content.splitlines()
        total_lines = len(file_lines)

        entities: list[ParsedTypeEntity] = []

        # Iterate top-level type declarations in compilation unit
        for node in (tree.types or []):
            if not isinstance(node, (ClassDeclaration, InterfaceDeclaration, EnumDeclaration)):
                continue
            line_start = node.position.line if node.position else 1

            # Estimate line end by scanning next sibling position or file end
            line_end = self._estimate_line_end(node, file_lines, line_start, total_lines)

            if isinstance(node, ClassDeclaration):
                entity_type = "CLASS"
                extends_name = node.extends.name if node.extends else None
                implements_names = [impl.name for impl in node.implements] if node.implements else []
            elif isinstance(node, InterfaceDeclaration):
                entity_type = "INTERFACE"
                extends_name = node.extends[0].name if (node.extends and len(node.extends) > 0) else None
                implements_names = []
            else:
                entity_type = "ENUM"
                extends_name = None
                implements_names = [impl.name for impl in node.implements] if node.implements else []

            name = node.name
            fqn = f"{package_name}.{name}" if package_name else name
            modifiers = list(node.modifiers) if node.modifiers else []
            annotations = [self._parse_annotation(ann) for ann in (node.annotations or [])]

            fields = self._extract_fields(node)
            methods = self._extract_methods(node, file_lines)

            entities.append(
                ParsedTypeEntity(
                    name=name,
                    entity_type=entity_type,
                    package_name=package_name,
                    fully_qualified_name=fqn,
                    relative_file_path=relative_file_path,
                    line_start=line_start,
                    line_end=line_end,
                    extends_name=extends_name,
                    implements_names=implements_names,
                    annotations=annotations,
                    modifiers=modifiers,
                    fields=fields,
                    methods=methods,
                    imports=imports,
                    ast_tree=tree,
                )
            )

        return entities

    def _parse_annotation(self, ann: Annotation) -> ParsedAnnotation:
        """Extract annotation name and arguments."""
        pairs: dict[str, str] = {}
        if ann.element:
            if isinstance(ann.element, list):
                pairs["value"] = ", ".join(str(e) for e in ann.element)
            else:
                pairs["value"] = str(ann.element)
        return ParsedAnnotation(name=ann.name, element_pairs=pairs)

    def _extract_fields(self, type_node: Any) -> list[ParsedField]:
        """Extract field declarations from a type node."""
        fields: list[ParsedField] = []
        if not hasattr(type_node, "fields") or not type_node.fields:
            return fields

        for field_decl in type_node.fields:
            line_start = field_decl.position.line if field_decl.position else 1
            field_type = field_decl.type.name if hasattr(field_decl, "type") and hasattr(field_decl.type, "name") else "Object"
            modifiers = list(field_decl.modifiers) if field_decl.modifiers else []
            annotations = [self._parse_annotation(ann) for ann in (field_decl.annotations or [])]

            for declarator in field_decl.declarators:
                fields.append(
                    ParsedField(
                        name=declarator.name,
                        field_type=field_type,
                        modifiers=modifiers,
                        annotations=annotations,
                        line_start=line_start,
                        line_end=line_start,
                    )
                )
        return fields

    def _extract_methods(self, type_node: Any, file_lines: list[str]) -> list[ParsedMethod]:
        """Extract method and constructor declarations from a type node."""
        methods: list[ParsedMethod] = []
        if not hasattr(type_node, "body") or not type_node.body:
            return methods

        for member in type_node.body:
            if not isinstance(member, (MethodDeclaration, ConstructorDeclaration)):
                continue

            is_constructor = isinstance(member, ConstructorDeclaration)
            name = member.name if not is_constructor else type_node.name
            line_start = member.position.line if member.position else 1
            line_end = self._estimate_method_line_end(line_start, file_lines)

            return_type = "void"
            if not is_constructor and hasattr(member, "return_type") and member.return_type:
                return_type = member.return_type.name if hasattr(member.return_type, "name") else "Object"

            modifiers = list(member.modifiers) if member.modifiers else []
            annotations = [self._parse_annotation(ann) for ann in (member.annotations or [])]

            params: list[dict[str, str]] = []
            if member.parameters:
                for param in member.parameters:
                    ptype = param.type.name if hasattr(param.type, "name") else "Object"
                    params.append({"name": param.name, "type": ptype})

            invocations = self._extract_method_invocations(member)

            methods.append(
                ParsedMethod(
                    name=name,
                    return_type=return_type,
                    parameters=params,
                    modifiers=modifiers,
                    annotations=annotations,
                    is_constructor=is_constructor,
                    line_start=line_start,
                    line_end=line_end,
                    method_invocations=invocations,
                )
            )

        return methods

    def _extract_method_invocations(self, method_node: Any) -> list[dict[str, Any]]:
        """Extract method invocation call sites inside a method body."""
        invocations: list[dict[str, Any]] = []
        for path, node in method_node.filter(MethodInvocation):
            line = node.position.line if node.position else method_node.position.line if method_node.position else 1
            qualifier = node.qualifier if hasattr(node, "qualifier") and node.qualifier else ""
            invocations.append(
                {
                    "method_name": node.member,
                    "qualifier": qualifier,
                    "line_number": line,
                    "args_count": len(node.arguments) if node.arguments else 0,
                }
            )
        return invocations

    def _estimate_line_end(
        self, node: Any, file_lines: list[str], start_line: int, total_lines: int
    ) -> int:
        """Estimate closing line of a type declaration by counting matching braces."""
        braces = 0
        found_first_brace = False

        for i in range(start_line - 1, total_lines):
            line = file_lines[i]
            for char in line:
                if char == "{":
                    braces += 1
                    found_first_brace = True
                elif char == "}":
                    braces -= 1
                    if found_first_brace and braces == 0:
                        return i + 1
        return total_lines

    def _estimate_method_line_end(self, start_line: int, file_lines: list[str]) -> int:
        """Estimate closing line of a method by counting braces."""
        total_lines = len(file_lines)
        braces = 0
        found_first_brace = False

        for i in range(start_line - 1, total_lines):
            line = file_lines[i]
            for char in line:
                if char == "{":
                    braces += 1
                    found_first_brace = True
                elif char == "}":
                    braces -= 1
                    if found_first_brace and braces == 0:
                        return i + 1
        return min(start_line + 10, total_lines)
