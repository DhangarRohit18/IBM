# ADR-007 — Java AST Parser Selection for System X-Ray

**Status:** Accepted  
**Date:** Phase 3  
**Deciders:** Project Lead, Lead Architect  

---

## Context

Phase 3 requires a deterministic static analysis engine to extract structural entities (packages, classes, interfaces, enums, methods, fields, constructors, annotations) and relationships (imports, inheritance, interface implementation, dependencies, method calls) from Java source code repositories.

Per AGENTS.md §2.1 and Phase 3 requirements:
- Static analysis is the sole source of truth for repository facts.
- Regex-based parsing is forbidden due to unreliability on complex syntax.
- Hand-written Java parsers are forbidden to avoid duplicate/fragile parser maintenance.
- A real AST (Abstract Syntax Tree) parser must be used.

---

## Parser Evaluation

| Criteria | `javalang` 0.13.0 | `tree-sitter-java` | Heavy JVM Binding (e.g. JavaParser via JPype) |
|---|---|---|---|
| **Runtime Dependency** | Pure Python (Zero native C/JVM dependencies) | Native C compiled bindings required | Requires Java JRE/JDK runtime installation on host |
| **AST Completeness** | Full Java 8+ AST nodes with exact line/column positions | Concrete Syntax Tree (CST) requiring manual AST mapping | Full Java 17+ AST |
| **Line & Column Evidence** | Built-in `Position(line, column)` on AST nodes | Built-in byte offsets & point objects | Built-in Range objects |
| **Ease of Integration** | Native Python import (`import javalang`) | Requires binary wheel compilation for Windows/Linux | Requires IPC/Subprocess or PyJNI bridge |
| **Error Handling** | Raises `javalang.parser.JavaSyntaxError` on malformed code | Error recovery nodes | Exception throwing |

---

## Decision

LEGACYX selects **`javalang` (v0.13.0)** as the primary Java AST parser engine for Phase 3.

---

## Supported Java Syntax & Capabilities

`javalang 0.13.0` fully parses and extracts:
- Package declarations (`package com.legacybank;`)
- Import statements (`import java.util.List;`, static imports)
- Type declarations: classes, interfaces, enums, abstract classes
- Class modifiers: `public`, `private`, `protected`, `abstract`, `static`, `final`
- Inheritance (`extends ClassName`) and interface implementations (`implements InterfaceName`)
- Field declarations with type signatures and initializers
- Method and constructor declarations with return types, parameter lists, and thrown exceptions
- Annotation decorations (`@RestController`, `@Service`, `@Repository`, `@Override`, `@Autowired`, etc.)
- Method invocations (`object.method()`, `this.method()`, static method calls, constructor calls)
- Exact line and column source positions (`Position(line, column)`)

---

## Syntax Limitations & Fallback Strategy

1. **Modern Java Syntax (Java 14–17+)**: Features such as `record` classes, sealed interfaces, or text blocks (`"""..."""`) may trigger `JavaSyntaxError` in `javalang` 0.13.0.
2. **Graceful Degradation**: When a syntax error occurs on a specific file:
   - The error is logged cleanly (`analysis.file_parse_error`).
   - The file is recorded with an error marker in `AnalysisRun`.
   - Structural entities extracted from all valid files in the repository are preserved.
   - **No fabricated facts or hallucinated entities are produced for failed files.**

---

## Consequences

- `javalang>=0.13.0` is added to `pyproject.toml` and `requirements.txt`.
- Analysis results remain 100% deterministic and reproducible across runs.
- All structural entities and relationships retain line-number evidence derived directly from AST node positions.
