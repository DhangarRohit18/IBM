# ADR-002 — Java/Spring as the Initial Supported Ecosystem

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

LEGACYX's analysis engine must parse source code, extract an AST, identify annotations, resolve dependencies, detect framework patterns, and extract database interactions. This requires language-specific and framework-specific knowledge.

Two approaches are possible:

**Option A — Multi-language from the start:**  
Support Java, Python, .NET, Node.js, etc. from Phase 3 onwards.

**Option B — Single ecosystem, done deeply:**  
Choose one language and framework ecosystem and implement a complete, demonstrable workflow.

---

## Decision

LEGACYX implements **Java / Spring Boot** as the first and only supported ecosystem during Phases 1–12.

---

## Rationale

### 1. Legacy Java/Spring is the Largest Target Market

Java is the dominant language in enterprise legacy systems. Spring Boot (and older Spring MVC) applications are the primary candidates for modernization in large organizations. This maximizes relevance.

### 2. Depth Over Breadth for a Hackathon Demonstration

A shallow multi-language implementation would demonstrate nothing convincingly. A deep Java/Spring implementation can demonstrate the full LEGACYX workflow: ingest → analyze → understand → decide → change → verify. Depth is more impressive and more trustworthy than breadth.

### 3. Java Has Strong AST Tooling

Java has mature, well-documented AST parsing libraries (e.g., javalang, JavaParser) that make deterministic analysis tractable in Phase 3. Spring's annotation-based architecture makes REST endpoint detection and dependency injection detection straightforward.

### 4. LegacyBank is a Realistic Target

The LegacyBank demonstration repository is designed specifically for Java/Spring, covering realistic characteristics. This gives Phase 12 (Demo Hardening) a credible end-to-end story.

### 5. Architecture Supports Future Extension

The analysis engine is designed with a `base_parser.py` abstraction that can support additional languages. Supporting Python or .NET is a future decision, not a current constraint.

---

## Consequences

- All analysis engine work in Phase 3 is Java-specific.
- LegacyBank is built with Java 11 / Spring Boot 2.x / Maven.
- Python, .NET, Node.js are out of scope for Phases 1–12.
- The `parser/` module must define a language-agnostic base interface to allow future extension.
