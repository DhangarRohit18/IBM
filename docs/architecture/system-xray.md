# LEGACYX — Architecture: System X-Ray / Deterministic Analysis (Phase 3)

## 1. Executive Summary

System X-Ray is the Phase 3 deterministic static analysis engine of LEGACYX. It transforms extracted Java repositories into a queryable, evidence-backed structural representation without relying on AI inference or floating-point confidence scores.

---

## 2. Architecture & Layer Discipline

```
Ingested Repository (Phase 2 Artifact)
         │
         ▼
 ┌───────────────────────────────┐
 │   JavaASTParser (javalang)    │ ── Extraction of Types, Methods, Fields, Annotations, Call Sites
 └───────────────────────────────┘
         │
         ▼
 ┌───────────────────────────────┐
 │  ComponentClassifier          │ ── Fact-based rules: Controller, Service, Repository, Entity, Config
 └───────────────────────────────┘
         │
         ▼
 ┌───────────────────────────────┐
 │  RelationshipResolver         │ ── Conservative resolution: IMPORTS, EXTENDS, IMPLEMENTS, DEPENDS_ON, CALLS
 └───────────────────────────────┘
         │
         ▼
 ┌───────────────────────────────┐
 │  ArchitectureGraphBuilder     │ ── Deterministic Graph Nodes & Directed Edges
 └───────────────────────────────┘
         │
         ▼
 PostgreSQL Persistence Layer & FastAPI Endpoints & System X-Ray UI
```

---

## 3. Mandatory Requirements & Architectural Guarantees

### 3.1 Parser Selection & Limitations (`javalang 0.13.0`)
- **Parser**: `javalang` 0.13.0 (pure Python, zero native binary dependencies).
- **Supported Features**: Java 7/8 syntax (classes, interfaces, enums, annotations, method declarations, field declarations, constructors, method invocations, imports, packages).
- **Limitations**: Java 9+ features (records, sealed classes, pattern matching, var keyword, text blocks) are parsed gracefully with error boundaries. Syntactically invalid files generate diagnostic parse errors rather than halting pipeline execution.

### 3.2 Evidence-Backed Component Classification
- Every component classification emits a list of deterministic facts stored in `classification_evidence`.
- **Constraint**: Floating-point confidence percentages (e.g. `95%`) are **STRICTLY PROHIBITED**. Classifications are backed exclusively by empirical static evidence (e.g., `"Annotated with @RestController"`, `"Implements JpaRepository interface"`).

### 3.3 Conservative Call Site Resolution
- **Rule**: False positive relationships are strictly worse than unresolved relationships.
- When a method call site cannot be resolved unambiguously to a single entity, the relationship is recorded with `is_resolved=False` and preserved line-level call site evidence (`source_construct`, `evidence_reason`, `line_number`).

### 3.4 First-Class Source Evidence
Every extracted entity, method, field, and relationship preserves:
1. `relative_file_path`
2. `line_number` (or `line_start` - `line_end`)
3. `source_construct`
4. `evidence_reason`

---

## 4. Database Schema (Phase 3 System X-Ray)

- `analysis_runs`: Execution audit logs and status (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).
- `code_packages`: Java package declarations and file counts.
- `code_entities`: Top-level classes, interfaces, enums with `classification_evidence` string arrays.
- `code_methods`: Method & constructor signatures, parameter types, return types, line boundaries.
- `code_fields`: Field declarations, field types, annotations, line boundaries.
- `code_relationships`: Directed structural edges (`IMPORTS`, `EXTENDS`, `IMPLEMENTS`, `DEPENDS_ON`, `CALLS`).

---

## 5. Phase Scope Boundaries

Phase 3 contains **ABSOLUTELY NO**:
- AI / LLM calls / IBM watsonx integration
- Business-rule extraction
- Modernization recommendations or migration planning
- Code transformation
- Behavioral validation or sandbox execution

---

*Phase 3 Architecture Specification — LEGACYX*
