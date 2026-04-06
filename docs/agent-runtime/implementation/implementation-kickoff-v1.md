# Implementation Kickoff v1

## Purpose

This document translates the architecture set into the **first implementation milestone**.

It answers one practical question:

> What do we need to build first so the runtime exists as a real, testable system rather than only a document set?

This is intentionally narrower than full v1. It targets the minimum slice that proves:
- durable request ingress,
- strategic-owner normalization,
- task + handoff lifecycle,
- callback handling,
- reply publication tracking,
- event durability,
- basic recovery hooks.

Use this as the implementation start point.

## Frozen Kickoff Decisions

The following decisions are fixed for the kickoff slice. Do not reopen them during the first implementation milestone.

- runtime topology: one local process, with API handlers and worker loops running in-process
- ingress surface for the kickoff slice: `POST /api/v1/requests` acts as the ingress adapter surrogate
- request class at kickoff: all `POST /requests` inputs are treated as `durable`
- strategic owner at kickoff: always `james`
- execution assignee at kickoff: configurable default, but ship with `naomi` as the default local assignee
- task creation timing at kickoff: immediate on accepted ingress
- handoff creation timing at kickoff: immediate after task creation
- publication model at kickoff: one final reply intent per request; progress updates are deferred
- auth profile at kickoff: loopback-local runtime with bootstrap bearer auth for non-webhook endpoints; webhook HMAC remains mandatory
- adapter model at kickoff: no real Discord/WhatsApp/web adapters yet; publication webhook simulates adapter callback delivery

- handoff outcome values at kickoff: only `done`, `failed`, and `blocked` are expected in normal completion paths; `partial` and `escalated` are schema-valid but reserved for later workflow slices

These choices are intentionally narrow. They reduce ambiguity so the first code can start.

## Scope of the First Milestone

Build the **core-slice runtime bring-up** first.

Included:
- local FastAPI app
- SQLite persistence with Alembic baseline
- command log, event log, outbox, jobs, requests, tasks, handoffs, publications
- `POST /api/v1/requests`
- `GET /api/v1/requests/{request_id}`
- `POST /api/v1/webhooks/publication-status`
- event append + ordered stream reads
- request projection + publication projection
- handoff accept / complete / reject service path
- publication-state updates from signed webhook callback
- bounded retry/watchdog table shape and command stubs

Explicitly deferred from the first milestone:
- full Mission Control workflow engine
- UI
- CLI
- memory retrieval and vectorization
- real Discord / WhatsApp adapters
- advanced diagnostics and operator dashboards
- remote auth hardening beyond what is needed for local bring-up

## Non-Negotiable Slice Boundaries

Do not collapse these concerns in the first implementation:
- request routing/publication state vs task/workflow state
- task completion vs callback success vs reply publication success
- strategic ownership vs execution ownership
- handoff transport ack vs handoff acceptance vs task completion
- internal event identity vs external webhook delivery identity

If the first slice cheats on these boundaries, later work will be slower and riskier.

## First Deliverable

At the end of the first milestone, the team should be able to run this local sequence:

1. `POST /api/v1/requests` creates a durable request record.
2. Runtime creates the initial task / handoff context.
3. Assignee accepts the handoff through the internal service path.
4. Assignee completes the work and emits callback/event updates.
5. Runtime marks request as awaiting publication.
6. Publication callback webhook marks the publish intent as `published` or `failed`.
7. `GET /api/v1/requests/{request_id}` shows the joined operator-facing state.

If this path does not work end to end, do not move to UI, vectorization, or richer workflow automation.

## Recommended Build Order

## Minimum Internal Command Set

Implement these internal commands first and do not invent a parallel set during coding:

- `AcceptRequestCommand`
- `CreateTaskCommand`
- `DispatchHandoffCommand`
- `AcceptHandoffCommand`
- `RejectHandoffCommand`
- `CompleteHandoffCommand`
- `RecordPublicationAttemptCommand`
- `RecordPublicationResultCommand`
- `ScheduleJobCommand`
- `CancelJobCommand`

These are internal DTOs/services, not public HTTP routes.
They are the minimum language needed for the kickoff slice.

### Step 1 — Create repository skeleton

Create the target minimum layout from `repo-structure-v1.md`:

```text
/services/runtime
/packages/runtime-core
/packages/persistence
/packages/contracts
/tests
```

Do not create `apps/web`, `apps/cli`, or `packages/mission-control` until the core slice compiles and runs.
Do not split the kickoff slice into separate `api` and `worker` apps.

### Step 2 — Define contract models first

Implement shared Pydantic models for:
- HTTP request/response DTOs
- event envelope
- internal handoff DTOs
- webhook callback DTOs
- internal command/event DTOs

These models should live under `packages/contracts`.

The contract layer should be written before repositories and handlers so persistence cannot invent its own schema accidentally.

### Step 3 — Create Alembic baseline and persistence layer

Implement the initial schema from:
- `data/sql-schema-v1.md`
- `data/state-projections-v1.md`

Minimum repositories:
- `RequestRepository`
- `TaskRepository`
- `HandoffRepository`
- `PublicationRepository`
- `CommandLogRepository`
- `EventLogRepository`
- `OutboxRepository`
- `JobRepository`

Important rule:
- repositories return domain/persistence DTOs,
- they do not contain orchestration logic.

### Step 4 — Implement event store and append discipline

Build `EventStoreService` with:
- append with per-aggregate `stream_sequence`
- dedup protection by `dedup_key`
- stream reads by aggregate key
- timeline reads by `correlation_id` / `request_id`

Do not defer this.
The runtime should emit events from day one.

### Step 5 — Implement ingress path

Build `IngressService.accept_request()` to:
- validate `POST /requests`
- enforce `Idempotency-Key`
- create `request_id`
- create `correlation_id`
- write request record
- append `request.received`
- append `request.normalization_attempted`
- append `request.normalization_accepted`
- set `strategic_owner_agent_id = james`
- set `current_owner_agent_id = james`
- create initial request projection row
- create the initial task immediately
- dispatch the initial handoff immediately
- return a non-null `task_ref`

For the kickoff slice, task creation is **not deferred**.

### Step 6 — Implement task + handoff orchestration

Build the minimal `OrchestratorService` and `HandoffService`:
- create task
- dispatch handoff
- accept handoff
- reject handoff
- complete handoff

Required emitted events:
- `task.created`
- `handoff.dispatched`
- `handoff.accepted` or `handoff.rejected`
- `task.accepted`
- `task.started`
- `task.completed`
- `callback.sent`
- `callback.received`

The first implementation may use in-process service calls instead of a real agent runtime, but it must still emit the canonical events.
The kickoff implementation should use a configurable in-process assignee path with `naomi` as the default.

### Step 7 — Implement request/publication projections

Implement projection workers for:
- `request_projection`
- `task_projection`
- `publication_projection`

Minimum operator-facing statuses to support:
- `received`
- `normalized`
- `delegated`
- `awaiting_callback`
- `reply_publish_pending`
- `reply_published`
- `reply_publish_failed`
- `fallback_required`
- `closed`

### Step 8 — Implement publication callback path

Build `POST /api/v1/webhooks/publication-status` with:
- HMAC verification
- delivery-id deduplication by webhook `event_id`
- update of `publications` row
- mirrored update of `requests.reply_publish_status`
- event append for:
  - `reply.publication_attempted`
  - `reply.published`
  - `reply.publication_failed`

Important:
- webhook `event_id` is transport identity,
- `publish_dedup_key` is reply-intent identity.

Do not conflate them.

For the kickoff slice, each request produces exactly one final publish intent.
Intermediate publish intents are deferred until after the first milestone.

### Step 9 — Implement watchdog/job primitives

Do not build full recovery automation yet.
Do build the primitives:
- `jobs` table
- watchdog/job record creation
- cancellation field updates
- one worker loop able to pick queued jobs

The first milestone only needs enough machinery to prove retry/watchdog persistence shape is real.

### Step 10 — Add contract and slice tests before expansion

Before adding Mission Control or UI, add:
- ingress idempotency tests
- handoff acceptance/completion tests
- publication callback signature tests
- duplicate callback delivery tests
- request projection tests
- event ordering/dedup tests
- reconciliation tests for ambiguous publication vs published callback

## Minimal Internal Components

The first slice should implement only these services:
- `IngressService`
- `OrchestratorService`
- `HandoffService`
- `EventStoreService`
- `PublicationService`
- `PolicyEnforcer` stub
- one projection worker loop
- one job worker loop

Everything else can stay stubbed or absent.

## Recommended First API Surface

Required immediately:
- `POST /api/v1/requests`
- `GET /api/v1/requests/{request_id}`
- `POST /api/v1/webhooks/publication-status`

Do not implement the full `full-v1` API set first.

## Recommended Test Matrix for the Kickoff Slice

The kickoff slice is not done until these cases pass:

| Case | Expected result |
|------|-----------------|
| duplicate `POST /requests` same key + same payload | same durable request returned, no duplicate task/handoff |
| duplicate `POST /requests` same key + different payload | `409 CONFLICT` |
| handoff accepted twice | idempotent second accept |
| callback completed twice with same `dedup_key` | idempotent second completion |
| publication webhook replayed with same webhook `event_id` | no duplicate state change |
| publication fails after task completion | request remains open with failed publication state |
| late success after ambiguous publish | state reconciles without duplicate publish intent |

## Exit Criteria for the First Milestone

The first milestone is complete only when all of the following are true:

1. The runtime boots locally with one process and one SQLite database.
2. Alembic can create the baseline schema from scratch.
3. The ingress -> immediate task/handoff -> callback -> publication path works end to end.
4. The request read model can show request lifecycle and publication state cleanly.
5. Duplicate ingress and duplicate publication callbacks are safe.
6. The event log is append-only and queryable by aggregate and correlation.
7. There is at least one worker loop proving projection/job execution against durable tables.

## What To Build Next After This Slice

Only after the first milestone is stable:
- Mission Control domain module
- richer recovery policies
- CLI
- built-in operator UI
- memory and vectorization services
- real adapters
- diagnostics bundle

That order matters. Do not invert it.
