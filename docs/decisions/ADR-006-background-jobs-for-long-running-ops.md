# ADR-006 — Long-Running Operations Use Background Jobs

**Status:** Accepted  
**Date:** Phase 0  
**Deciders:** Project Lead

---

## Context

Several LEGACYX operations are inherently long-running:
- Repository analysis (parsing 50k+ LOC Java project, building dependency graphs)
- Migration plan generation (AI-assisted, involves multiple AI calls)
- Code transformation (AI call per component)
- Behavioral validation (building and executing two systems)

Two approaches:

**Option A — Synchronous API responses:**  
The API request blocks until the operation completes and returns the result directly. Frontend waits for the HTTP response.

**Option B — Background job queue with progress events:**  
The API request enqueues a job and returns immediately with a job ID. The job executes in a worker process. Progress events are emitted via WebSocket. The frontend polls or subscribes to events.

---

## Decision

LEGACYX uses **Option B — Background job queue with progress events** for all long-running operations.

The job queue is implemented using **Redis** as the broker. Workers consume from Redis queues.

---

## Rationale

### 1. HTTP Request Timeouts

A repository analysis job for a 50k LOC codebase may take minutes. HTTP requests cannot reliably remain open for minutes. Load balancers, proxies, and browsers impose timeouts that make synchronous long-running HTTP requests unreliable.

### 2. Horizontal Scalability

Background workers are independently scalable. Adding analysis capacity means adding worker instances, not scaling API server instances. This is a clean separation of concerns.

### 3. Resilience

If the API server restarts, a synchronous operation fails immediately. A background job in Redis is durable (with appropriate configuration) and can be retried or resumed by a different worker.

### 4. Real-Time Progress Is Required

The product requires real-time progress during analysis, migration, and validation. This is not a nice-to-have — it is a defined feature. Real-time progress requires an asynchronous architecture with event emission from workers and WebSocket delivery to the frontend. This is not achievable with synchronous API responses.

### 5. Idempotency and Restartability

Background jobs can be designed to be idempotent: if a job fails partway through, it can be restarted without duplicating work already completed. Synchronous operations do not offer this property.

---

## Consequences

- Every long-running operation (analysis, migration generation, transformation, validation) must be implemented as a background job.
- FastAPI routes that trigger long-running operations return `202 Accepted` with a job ID and a status URL.
- Workers are defined in `backend/app/workers/`.
- Redis is a required infrastructure component from Phase 1.
- A WebSocket endpoint must be implemented for progress events (Phase 11).
- Job results are persisted to PostgreSQL by the worker, not the API layer.
- Workers must emit structured progress events throughout their execution lifecycle.
- Failed jobs must be restartable. Workers must be idempotent where possible.
