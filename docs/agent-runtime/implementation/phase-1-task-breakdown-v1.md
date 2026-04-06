# Phase 1 Task Breakdown v1

## Purpose

This document turns the kickoff slice into an implementation backlog.

It is intentionally concrete:
- grouped by package/module,
- ordered by dependency,
- scoped to the first development milestone,
- written so it can be copied into issues or PR plans with minimal translation.

Use this together with:
- `implementation-kickoff-v1.md`
- `interfaces-v1.md`
- `repo-structure-v1.md`

## Working Rule

Do not start tasks from a later block until the current block is green.

Phase 1 is optimized for:
- fast local bring-up,
- durable core semantics,
- narrow but real end-to-end behavior.

It is not optimized for completeness.

## Block A — Repository Bootstrap

### A1. Create Python project skeleton

Target:
- `services/runtime/`
- `packages/contracts/`
- `packages/persistence/`
- `packages/runtime-core/`
- `tests/`

Definition of done:
- import graph works
- one root toolchain is chosen
- local dev command can run tests and app bootstrap

### A2. Choose and wire base tooling

Pick and commit:
- package manager
- formatter
- linter
- test runner
- Alembic config

Definition of done:
- one documented bootstrap command exists
- one documented test command exists
- one documented migration command exists

### A3. Add runtime config model

Implement a config object for:
- SQLite path
- bootstrap bearer token
- webhook signing secret(s)
- default assignee agent id
- environment mode (`local-dev`, later `prod`)

Definition of done:
- app starts from config, not hardcoded constants scattered across modules

## Block B — Contracts

### B1. HTTP DTOs

Implement DTOs for:
- `POST /requests`
- `GET /requests/{request_id}`
- error body

Definition of done:
- request/response validation matches `contracts/http-api-v1.md`

### B2. Event DTOs

Implement:
- event envelope
- actor payload
- aggregate key helper

Definition of done:
- can serialize/deserialize canonical event envelope with `schema_version`, `occurred_at`, `dedup_key`

### B3. Handoff DTOs

Implement:
- handoff payload
- accept payload
- reject payload
- complete payload

Definition of done:
- validation matches `contracts/internal-a2a-v1.md`

### B4. Webhook DTOs

Implement:
- publication callback payload
- signed header extraction model

Definition of done:
- model distinguishes webhook `event_id` from `publish_dedup_key`

### B5. Internal command DTOs

Implement the kickoff command set:
- `AcceptRequestCommand`
- `CreateTaskCommand`
- `DispatchHandoffCommand`
- `AcceptHandoffCommand`
- `RejectHandoffCommand`
- `CompleteTaskCommand`
- `RecordPublicationAttemptCommand`
- `RecordPublicationResultCommand`
- `ScheduleJobCommand`
- `CancelJobCommand`

Definition of done:
- runtime-core services accept internal DTOs only

## Block C — Persistence

### C1. Alembic baseline

Create the baseline migration for:
- `command_log`
- `requests`
- `tasks`
- `handoffs`
- `publications`
- `event_log`
- `event_outbox`
- `jobs`
- projection tables from `state-projections-v1.md`

Definition of done:
- empty DB can be created from scratch
- migration can be reapplied on a clean local environment

### C2. ORM models / table mappings

Implement persistence models for all baseline tables.

Definition of done:
- field names match the docs
- enums/vocabularies are centralized

### C3. Repositories

Implement:
- `CommandLogRepository`
- `RequestRepository`
- `TaskRepository`
- `HandoffRepository`
- `PublicationRepository`
- `EventLogRepository`
- `OutboxRepository`
- `JobRepository`

Definition of done:
- repositories are CRUD/query only
- no orchestration logic leaks into persistence

### C4. Transaction helper

Implement one transaction/unit-of-work helper for:
- request write + event append
- event append + outbox row creation
- webhook state update + event append

Definition of done:
- core write paths are atomic

## Block D — Event Engine

### D1. Event append service

Implement `EventStoreService.append()` with:
- per-stream sequence allocation
- `dedup_key` enforcement
- append-only semantics

Definition of done:
- duplicate append with same `dedup_key` is safe

### D2. Event read service

Implement reads by:
- aggregate stream
- `correlation_id`
- optional `request_id` filter via payload or join helper

Definition of done:
- request timeline can be queried without transcript access

### D3. Outbox writer

When appending an event that must be dispatched, write:
- event row
- outbox row

Definition of done:
- no dispatched side effect exists without a durable event row

## Block E — Core Runtime Services

### E1. `IngressService`

Implement accepted ingress path:
- validate headers/body
- classify request as `durable`
- create `request_id`
- create `correlation_id`
- persist request
- emit normalization events

Definition of done:
- service returns durable request identity
- duplicate ingress is idempotent

### E2. `OrchestratorService`

Implement:
- immediate task creation
- immediate handoff dispatch
- strategic owner = `james`
- default execution assignee = config default (`naomi`)

Definition of done:
- accepted request always produces a task + handoff in the kickoff slice

### E3. `HandoffService`

Implement:
- accept
- reject
- complete

Definition of done:
- handoff lifecycle updates task state correctly
- task completion records callback path correctly

### E4. `PublicationService`

Implement:
- create/update final publish intent
- transition request/publication state
- record delivery callback outcomes

Definition of done:
- request `reply_publish_status` mirrors the authoritative publication outcome

## Block F — API Layer

### F1. `POST /api/v1/requests`

Definition of done:
- requires `Idempotency-Key`
- uses bootstrap bearer token in local dev
- returns non-null `task_ref`

### F2. `GET /api/v1/requests/{request_id}`

Definition of done:
- returns operator-facing read model
- includes request lifecycle status + publication status

### F3. `POST /api/v1/webhooks/publication-status`

Definition of done:
- verifies HMAC
- deduplicates by webhook delivery `event_id`
- updates request/publication state atomically

## Block G — Background Workers

### G1. Request projection worker

Materialize:
- request lifecycle status
- strategic/current owner fields
- reply target summary
- publication summary

Definition of done:
- `GET /requests/{id}` can read from a projection instead of ad hoc joins

### G2. Task projection worker

Materialize:
- current task owner
- task state
- last stream sequence

Definition of done:
- handoff/task lifecycle is visible without replaying every event each time

### G3. Publication projection worker

Materialize:
- publish intent status
- attempt counts
- last delivery event id

Definition of done:
- publication state is visible independently of request/task state

### G4. Job worker

Implement one simple loop that can:
- poll queued jobs
- mark running/completed/failed
- no-op unsupported job types safely

Definition of done:
- watchdog/retry persistence shape is executable, not only modeled

## Block H — Tests

### H1. Contract tests

Cover:
- HTTP validation
- handoff payload validation
- webhook signature handling

### H2. Persistence tests

Cover:
- migration bootstrap
- repository round-trips
- event sequence ordering
- `dedup_key` uniqueness behavior

### H3. Service tests

Cover:
- ingress idempotency
- immediate task + handoff creation
- handoff accept/reject/complete transitions
- publication result recording

### H4. End-to-end slice tests

Cover:
- request -> task -> handoff -> callback -> publication success
- request -> task -> handoff -> callback -> publication failure
- duplicate ingress replay
- duplicate webhook replay

Phase 1 is not complete without at least one real E2E path.

## Suggested PR Sequence

Recommended PR order:

1. repo bootstrap + tooling
2. contracts package
3. Alembic baseline + persistence models
4. repositories + transaction helper
5. event store + outbox
6. runtime-core services
7. API routes
8. projection/job workers
9. tests + hardening

Do not bundle all of Phase 1 into one PR.

## Exit Gate

Phase 1 can be called kickoff-complete when:
- local app boots,
- migration works,
- one end-to-end happy path passes,
- one end-to-end publication-failure path passes,
- duplicate ingress is safe,
- duplicate webhook replay is safe,
- docs and code still match.
