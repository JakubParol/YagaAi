# Coding Kickoff Plan — What To Add Before Implementation

## Context
This plan was prepared after reviewing all Markdown documentation currently in the repository (`README.md`, full `docs/agent-runtime/**`, and current `docs/superpowers/**`).

The architecture and runtime rules are described in depth, but we still need a few implementation-facing artifacts to reduce ambiguity before coding starts.

## What Is Already Solid
- System vision, boundaries, roles, and runtime principles are documented.
- Event, status, handoff, and policy references exist.
- High-level deployment/runtime shape and preferred tech stack are defined.
- There is already an event-storming alignment design + implementation plan.

## What We Still Need To Write (Minimum Coding Readiness)

### 1) API Contract Pack (v1)
**Why:** we describe behavior conceptually, but coding needs exact request/response schemas and error models.

Create:
- `docs/agent-runtime/contracts/http-api-v1.md`
  - Endpoints, methods, payload schemas, validation rules
  - Error taxonomy + HTTP status mapping
  - Idempotency rules (especially for ingress)
- `docs/agent-runtime/contracts/internal-a2a-v1.md`
  - Naomi↔Alex / Naomi↔Amos handoff payloads
  - Ack/accept/complete examples
- `docs/agent-runtime/contracts/webhook-callback-v1.md`
  - Callback payloads, signatures, retry semantics

### 2) Data Model Spec (DB-first)
**Why:** docs mention entities and state, but implementation needs exact tables/indices and migration strategy.

Create:
- `docs/agent-runtime/data/sql-schema-v1.md`
  - Full table list and columns (types, nullability, defaults)
  - PK/FK/index constraints
  - Uniqueness rules (`request_id`, `correlation_id`, dedupe keys)
- `docs/agent-runtime/data/state-projections-v1.md`
  - How request/task/publication projections are materialized
  - Writer responsibility and conflict resolution rules

### 3) Event Bus Contract + Topic Map
**Why:** canonical events exist, but not yet a wire-level publish/subscribe contract.

Create:
- `docs/agent-runtime/contracts/event-bus-v1.md`
  - Topic naming convention
  - Event envelope schema (`event_id`, `occurred_at`, actor, causation/correlation)
  - Delivery guarantees and retry/dead-letter policy
- `docs/agent-runtime/reference/event-topic-map.md`
  - Mapping: canonical event → topic → producer → consumers

### 4) Implementation Skeleton Spec
**Why:** high-level architecture exists; we need folder-level code blueprint to start parallel coding.

Create:
- `docs/agent-runtime/implementation/repo-structure-v1.md`
  - Proposed package/module structure
  - Responsibility boundaries per module
- `docs/agent-runtime/implementation/interfaces-v1.md`
  - Service interfaces (ingress, orchestrator, memory, publication)
  - DTO definitions and mapping boundaries

### 5) Test Strategy & Quality Gates
**Why:** without explicit quality gates, coding diverges quickly.

Create:
- `docs/agent-runtime/testing/test-strategy-v1.md`
  - Unit/integration/e2e scope
  - Contract test matrix for APIs, A2A, events
  - Failure-recovery scenario matrix (timeouts, retries, duplicate delivery)
- `docs/agent-runtime/testing/definition-of-done-v1.md`
  - Required checks per PR
  - Minimum coverage targets and critical-path checks

### 6) Security & Compliance Baseline
**Why:** current docs mention governance, but implementation needs concrete security defaults.

Create:
- `docs/agent-runtime/security/security-baseline-v1.md`
  - AuthN/AuthZ model (service-to-service + operator)
  - Secret management rules
  - Data retention/redaction policy for prompts/memory/audit logs
  - PII handling and audit requirements

### 7) Operational Runbooks
**Why:** observability is described; on-call execution needs practical procedures.

Create:
- `docs/agent-runtime/operations/runbook-ingress-failures.md`
- `docs/agent-runtime/operations/runbook-handoff-failures.md`
- `docs/agent-runtime/operations/runbook-publication-failures.md`
- `docs/agent-runtime/operations/runbook-data-repair.md`

Each should include: detection signals, triage steps, safe retries, rollback/manual repair, and post-incident audit steps.

## Recommended Order (So We Can Start Coding Fast)
1. **API Contract Pack**
2. **Data Model Spec**
3. **Event Bus Contract + Topic Map**
4. **Implementation Skeleton Spec**
5. Start coding a thin vertical slice (ingress → task create → event publish → callback)
6. Parallelize **Test Strategy**, **Security Baseline**, and **Runbooks**

## Thin Vertical Slice Definition (Sprint 0)
Before full implementation, define one end-to-end slice with real persistence:
- Receive normalized request
- Persist request + initial task
- Emit lifecycle events
- Simulate one A2A handoff
- Persist completion and publication projection
- Return/publish final user-visible result

This slice validates core assumptions before scaling modules.

## Exit Criteria: “Ready To Code”
We can start full coding when all conditions below are true:
- v1 API, A2A, callback, and event-bus contracts are frozen.
- SQL schema v1 and migration baseline are approved.
- Module boundaries are documented and assigned.
- Definition of Done is accepted and automated in CI.
- Security baseline and minimal runbooks are merged.
