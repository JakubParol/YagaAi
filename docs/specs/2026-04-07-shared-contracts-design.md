# Shared Contracts Design — YAGA-26

**Date:** 2026-04-07
**Work item:** YAGA-26
**Status:** Approved
**Parent epic:** YAGA-23 (Kickoff Foundation: Bootstrap and Contracts)

## Goal

Implement the contracts layer (`yaga_contracts` package) so that persistence
and services cannot invent incompatible schemas. All Pydantic DTOs for HTTP
request/response, event envelopes, handoff payloads, webhook callbacks, and
internal commands live here.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module layout | Flat files under `yaga_contracts/` | Small scope (~15 models), 300-line file limit, no need for subdirectories yet |
| Inheritance strategy | Hybrid — bases for commands and events only | Commands share a genuine envelope (10 fields); events share a genuine envelope (12 fields). HTTP and webhook DTOs are flat. |
| ID types | `str` everywhere | SQL schema uses TEXT for all IDs. Architecture docs use string identifiers (`"james"`, `"hof_01"`, `"req_01"`). Contracts stay permissive — validation tightening happens at the service layer. |
| Event payloads | `dict[str, Any]` on envelope, typed payload models for deserialization | Avoids a 30+ type discriminated union that couples unrelated event domains. Consumers pick the payload model by `event_type`. |
| Pydantic config | `model_config = ConfigDict(frozen=True)` on all models | Contracts are immutable data containers. |
| Handoff vs task completion | Separate contracts | Handoff acceptance (`received → accepted/rejected`) is a routing concern. Task completion returns via `task.completed` / `callback.sent` events — a different contract layer. No `HandoffCompletion` model in contracts. |

## File Layout

```
packages/contracts/yaga_contracts/
├── __init__.py          # Re-exports all public models
├── shared.py            # Enums, value objects (Actor, ReplyTarget)
├── http.py              # HTTP request/response DTOs
├── events.py            # Event envelope base + typed payload models
├── handoffs.py          # Handoff dispatch + acceptance response DTOs
├── webhooks.py          # Webhook callback DTO + header constants
└── commands.py          # Command base + 10 concrete command types
```

## Module Specifications

### shared.py — Enums and Value Objects

**Enums:**

| Enum | Values | Source |
|------|--------|--------|
| `TaskStatus` | `CREATED`, `ACCEPTED`, `IN_PROGRESS`, `REVIEW`, `VERIFY`, `DONE`, `BLOCKED`, `ESCALATED`, `CANCELLED` | `reference/canonical-statuses.md` |
| `HandoffStatus` | `RECEIVED`, `ACCEPTED`, `REJECTED` | `contracts/internal-a2a-v1.md` (status enum: received\|accepted\|rejected) |
| `RequestStatus` | `RECEIVED`, `NORMALIZED`, `DELEGATED`, `AWAITING_CALLBACK`, `REPLY_PENDING`, `REPLY_PUBLISHED`, `REPLY_FAILED`, `FALLBACK_REQUIRED`, `CLOSED` | `contracts/http-api-v1.md` (operator-facing projection labels) |
| `PublishStatus` | `PENDING`, `ATTEMPTED`, `PUBLISHED`, `FAILED`, `UNKNOWN`, `FALLBACK_REQUIRED`, `ABANDONED` | `data/sql-schema-v1.md` (reply_publish_status vocabulary) |
| `RequestClass` | `SESSION_BOUND`, `DURABLE` | `03-runtime-and-a2a.md` |
| `ExecutionMode` | `SESSION_BOUND`, `DETACHED` | `reference/handoff-contract.md` |
| `HandoffResolution` | `ACCEPTED`, `REJECTED` | `contracts/internal-a2a-v1.md` |
| `TaskOutcome` | `DONE`, `FAILED`, `BLOCKED` | `implementation/implementation-kickoff-v1.md` (v1 subset) |
| `JobStatus` | `SCHEDULED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED` | `data/sql-schema-v1.md` (jobs.status vocabulary) |
| `CommandStatus` | `ACCEPTED`, `REJECTED`, `PROCESSED` | `data/sql-schema-v1.md` (command_log.status vocabulary) |
| `OutboxStatus` | `PENDING`, `DISPATCHED`, `FAILED` | `data/sql-schema-v1.md` (event_outbox.status vocabulary) |

**Value objects (frozen Pydantic models):**

| Model | Fields | Source |
|-------|--------|--------|
| `Actor` | `type: str`, `id: str` | `data/sql-schema-v1.md` (actor_json: `{"type":"agent"\|"runtime"\|"adapter","id":"<id>"}`) |
| `ReplyTarget` | `channel: str`, `session_key: str`, `adapter_metadata: dict[str, Any] \| None` | `data/sql-schema-v1.md` (reply_target_json: `{"channel":"...","session_key":"...","adapter_metadata":{}}`) |

**Note on Actor.type:** Known values are `"agent"`, `"runtime"`, `"adapter"`.
Actor.id is `str` (not UUID) because agent IDs in the architecture are string
identifiers (e.g., `"james"`, `"naomi"`).

### http.py — HTTP DTOs

**`CreateRequestBody`** — POST /api/v1/requests body:

| Field | Type | Notes |
|-------|------|-------|
| `origin` | `str` | Channel identifier: `"whatsapp"`, `"discord"`, `"web"`, `"cli"` |
| `payload` | `RequestPayload` | Nested object (see below) |
| `reply_target` | `ReplyTarget` | Where to publish the human-visible reply. Required: `requests.reply_target_*` columns are NOT NULL in `sql-schema-v1.md`, and the kickoff slice treats all inputs as durable requests that must have a reply destination. The HTTP example in `http-api-v1.md` always includes it. |

**`RequestPayload`** — nested payload within CreateRequestBody:

| Field | Type | Notes |
|-------|------|-------|
| `text` | `str` | User's input text (required for text inputs in v1) |

Source: `contracts/http-api-v1.md` body example:
`{"origin":"discord","payload":{"text":"Implement feature X"},"reply_target":{...}}`

`Idempotency-Key` is a request header handled by the API layer, not part of
the body DTO. `request_id` and `correlation_id` are NOT accepted from external
callers — the runtime assigns them.

**`CreateRequestResponse`** — 202 Accepted:

| Field | Type | Notes |
|-------|------|-------|
| `status` | `Literal["accepted"]` | Always `"accepted"` |
| `request_id` | `str` | Runtime-assigned request identifier |
| `task_ref` | `str \| None` | Task created for this request; `None` when task creation is deferred to a subsequent workflow step. In the kickoff slice, task creation is immediate on accepted ingress, so `task_ref` is always non-null for successful responses. |

Source: `contracts/http-api-v1.md` response: `{"status":"accepted","request_id":"req_01","task_ref":"task_01"}`

**`RequestReadModel`** — GET /api/v1/requests/{request_id}:

| Field | Type | Notes |
|-------|------|-------|
| `request_id` | `str` | |
| `correlation_id` | `str` | |
| `status` | `RequestStatus` | Operator-facing projection label |
| `reply_publish_status` | `PublishStatus` | Publication state |
| `origin` | `str` | Channel identifier |
| `strategic_owner_agent_id` | `str \| None` | e.g., `"james"` |
| `reply_target` | `ReplyTarget \| None` | Current reply destination |
| `created_at` | `datetime` | |
| `updated_at` | `datetime` | |

Source: `contracts/http-api-v1.md` GET /requests/{request_id} response example.
Fields match the HTTP contract exactly. Additional projection fields
(`origin_session_key`, `request_class`, `current_owner_agent_id`,
`reply_target_version`, `last_stream_sequence`) are internal to the
`request_projection` table and are NOT exposed through the HTTP read model.

**`ErrorDetail`** — inner error object:

| Field | Type | Notes |
|-------|------|-------|
| `code` | `str` | Machine-readable error code (e.g., `"VALIDATION_ERROR"`, `"CONFLICT"`) |
| `message` | `str` | Human-readable description |
| `details` | `list[Any]` | Additional structured detail; empty list when not applicable |

**`ErrorResponse`** — error envelope (nested wrapper):

| Field | Type | Notes |
|-------|------|-------|
| `error` | `ErrorDetail` | Nested error object |

Source: `contracts/http-api-v1.md` error body:
`{"error":{"code":"VALIDATION_ERROR","message":"origin is required","details":[]}}`

### events.py — Event Envelope and Payloads

**Base class — `EventEnvelope`:**

| Field | Type | Notes |
|-------|------|-------|
| `event_id` | `str` | Unique per emission, changes on retry |
| `dedup_key` | `str` | Stable across retries (e.g., `"msg_hof_01_dispatch_1"`) |
| `event_type` | `str` | e.g., `"request.received"`, `"task.created"` |
| `aggregate_type` | `str` | e.g., `"request"`, `"task"`, `"handoff"` |
| `aggregate_id` | `str` | |
| `correlation_id` | `str` | Required on all events |
| `causation_id` | `str \| None` | `None` on root events |
| `actor` | `Actor` | |
| `occurred_at` | `datetime` | |
| `schema_version` | `str` | Default `"v1"` per event-bus-v1.md example (TEXT in SQL schema) |
| `stream_sequence` | `int` | Required per event-bus-v1.md. BIGINT in SQL. Assigned by the event store at persist time — producers must NOT set this field; the event store assigns the next monotonic value for the aggregate stream. In the Pydantic model, this field has no default and must be set before serialization (i.e., the event store constructs the final envelope). |
| `payload` | `dict[str, Any]` | Typed payload deserialized by consumers based on `event_type` |

Source: `reference/canonical-events.md` envelope fields +
`data/sql-schema-v1.md` event_log table.

**Note on dedup_key:** The architecture docs show string-pattern dedup keys
(e.g., `"msg_hof_01_dispatch_1"` in `contracts/internal-a2a-v1.md`), not
UUIDs. Using `str` to match the wire format.

**Typed payload models:**

| Model | Key fields |
|-------|------------|
| `RequestReceivedPayload` | `request_id: str`, `origin: str`, `origin_session_key: str \| None`, `idempotency_key: str`, `request_class: RequestClass`, `reply_target: ReplyTarget \| None` |
| `RequestNormalizationPayload` | `request_id: str`, `strategic_owner_agent_id: str`, `default_assignee_agent_id: str` |
| `TaskLifecyclePayload` | `task_id: str`, `request_id: str \| None`, `owner_agent_id: str`, `status: TaskStatus`, `outcome: TaskOutcome \| None` |
| `HandoffLifecyclePayload` | `handoff_id: str`, `task_id: str`, `from_agent: str`, `to_agent: str`, `status: HandoffStatus`, `reason: str \| None` |
| `CallbackPayload` | `task_id: str`, `callback_target: str`, `outcome: TaskOutcome`, `source_agent_id: str`, `target_agent_id: str`, `result_summary: str \| None` |
| `PublicationPayload` | `request_id: str`, `publish_dedup_key: str`, `status: PublishStatus`, `channel: str \| None`, `session_key: str \| None` |
| `WatchdogPayload` | `job_id: str`, `job_type: str`, `subject_type: str`, `subject_id: str` |
| `CommandRejectedPayload` | `command_type: str`, `reason: str` |

All ID fields in payloads are `str` to match the SQL TEXT column types.

### handoffs.py — Handoff DTOs

Handoff acceptance is a **routing concern** (who owns this work). Task/execution
completion is a separate contract that flows through `task.completed` and
`callback.sent` events. This file covers handoff transport only.

Source: `contracts/internal-a2a-v1.md` — "handoff acceptance does NOT carry
execution completion."

**`HandoffDispatch`** — owner → specialist:

| Field | Type | Notes |
|-------|------|-------|
| `handoff_id` | `str` | |
| `request_id` | `str \| None` | Required for user-originated durable work; nullable for agent-internal tasks |
| `from_agent` | `str` | Requester agent identifier |
| `to_agent` | `str` | Target specialist identifier |
| `goal` | `str` | |
| `definition_of_done` | `str` | |
| `callback_target` | `str` | Where to return results operationally |
| `correlation_id` | `str` | Always required |
| `causation_id` | `str \| None` | |
| `dedup_key` | `str` | Stable across safe retries of same handoff intent |

Source: `contracts/internal-a2a-v1.md` handoff payload example. Field names
match the wire format exactly (`from_agent`, `to_agent` — not `from_agent_id`).

Validation rules from the A2A contract:
- `handoff_id`, `from_agent`, `to_agent`, `goal`, `definition_of_done`,
  `callback_target`, `dedup_key` required
- `correlation_id` always required
- `from_agent != to_agent`

**`HandoffAck`** — transport-level acknowledgement:

| Field | Type | Notes |
|-------|------|-------|
| `handoff_id` | `str` | |
| `status` | `HandoffStatus` | Always `RECEIVED` at ack time |
| `received_at` | `datetime` | |

Source: `contracts/internal-a2a-v1.md` ack example:
`{"handoff_id":"hof_01","status":"received","received_at":"..."}`

**`HandoffAcceptance`** — specialist → owner (accept):

| Field | Type | Notes |
|-------|------|-------|
| `handoff_id` | `str` | |
| `status` | `HandoffStatus` | `ACCEPTED` |
| `owner` | `str` | Agent that accepted ownership |
| `accepted_at` | `datetime` | |

Source: `contracts/internal-a2a-v1.md` accept response:
`{"handoff_id":"hof_01","status":"accepted","owner":"alex","accepted_at":"..."}`

**`HandoffRejection`** — specialist → owner (reject):

| Field | Type | Notes |
|-------|------|-------|
| `handoff_id` | `str` | |
| `status` | `HandoffStatus` | `REJECTED` |
| `assignee` | `str` | Agent that rejected |
| `reason` | `str` | Required |
| `rejected_at` | `datetime` | |

Source: `contracts/internal-a2a-v1.md` reject response:
`{"handoff_id":"hof_01","status":"rejected","assignee":"alex","reason":"...","rejected_at":"..."}`

### webhooks.py — Webhook DTOs

**`PublicationStatusWebhook`** — POST /api/v1/webhooks/publication-status body:

| Field | Type | Notes |
|-------|------|-------|
| `event_id` | `str` | Webhook transport delivery ID — distinct from internal event-bus event_id |
| `request_id` | `str` | |
| `publication_id` | `str` | |
| `publish_dedup_key` | `str` | Matches against our publication intent |
| `status` | `PublishStatus` | |
| `channel` | `str` | |
| `session_key` | `str` | |
| `published_at` | `datetime \| None` | Present when status is `PUBLISHED` |
| `failure_reason` | `str \| None` | Present when status is `FAILED`; propagated to `RecordPublicationResultCommand` |

Source: `contracts/webhook-callback-v1.md` payload example:
`{"event_id":"evt_100","request_id":"req_01","publication_id":"pub_01",...}`

**Identity clarification** (from webhook-callback-v1.md):
- `event_id` here is the **transport delivery identifier** for this webhook
  callback — distinct from the internal event-bus `event_id` in `event_log`.
- `publish_dedup_key` is the authoritative identity of the human-visible
  publication intent.
- Consumer deduplicates by webhook `event_id`; reconciles state by
  `publish_dedup_key`.

**Header constants:**

```python
WEBHOOK_SIGNATURE_HEADER = "X-Yaga-Signature"
WEBHOOK_TIMESTAMP_HEADER = "X-Yaga-Timestamp"
WEBHOOK_EVENT_ID_HEADER = "X-Yaga-Event-Id"
WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS = 300
```

**Verification rules** (from webhook-callback-v1.md):
- Reject if timestamp drift > 300s
- HMAC SHA-256 over `timestamp + "." + event_id + "." + raw_body`
- Reject if `X-Yaga-Event-Id` header and payload `event_id` do not match

HMAC verification logic belongs in the API layer (Block F), not in contracts.

### commands.py — Internal Commands

**Base class — `CommandBase`:**

| Field | Type | Notes |
|-------|------|-------|
| `command_id` | `str` | |
| `command_type` | `str` | Discriminator, set per subclass |
| `aggregate_type` | `str` | e.g., `"request"`, `"task"`, `"handoff"` |
| `aggregate_id` | `str` | Target aggregate identifier |
| `correlation_id` | `str` | |
| `causation_id` | `str \| None` | |
| `dedup_key` | `str` | |
| `occurred_at` | `datetime` | |
| `actor` | `Actor` | |
| `schema_version` | `str` | Default `"v1"` |

Source: `data/sql-schema-v1.md` command_log table — all fields mapped 1:1.
Note: `actor` serializes to `actor_json` TEXT in SQL; `payload_json` is derived
from the command's additional fields at the persistence layer.

**Concrete commands (v1 minimum set from implementation-kickoff-v1.md):**

| Command | `command_type` | Additional fields |
|---------|---------------|-------------------|
| `AcceptRequestCommand` | `accept_request` | `request_id: str`, `idempotency_key: str`, `origin: str`, `origin_session_key: str \| None`, `request_class: RequestClass`, `reply_target: ReplyTarget \| None`, `payload: RequestPayload` |
| `CreateTaskCommand` | `create_task` | `task_id: str`, `request_id: str`, `owner_agent: str`, `callback_target: str` |
| `DispatchHandoffCommand` | `dispatch_handoff` | `handoff_id: str`, `task_id: str`, `request_id: str \| None`, `from_agent: str`, `to_agent: str`, `goal: str`, `definition_of_done: str`, `callback_target: str`, `execution_mode: ExecutionMode` |
| `AcceptHandoffCommand` | `accept_handoff` | `handoff_id: str`, `task_id: str`, `responder_agent: str` |
| `RejectHandoffCommand` | `reject_handoff` | `handoff_id: str`, `task_id: str`, `responder_agent: str`, `reason: str` |
| `CompleteTaskCommand` | `complete_task` | `task_id: str`, `request_id: str \| None`, `outcome: TaskOutcome`, `result_summary: str \| None`, `completed_by_agent: str` |
| `RecordPublicationAttemptCommand` | `record_publication_attempt` | `publication_id: str`, `request_id: str`, `publish_dedup_key: str`, `channel: str`, `session_key: str` |
| `RecordPublicationResultCommand` | `record_publication_result` | `publication_id: str`, `request_id: str`, `webhook_event_id: str`, `status: PublishStatus`, `failure_reason: str \| None` |
| `ScheduleJobCommand` | `schedule_job` | `job_id: str`, `job_type: str`, `subject_type: str`, `subject_id: str`, `run_at: datetime`, `payload_json: dict[str, Any] \| None` |
| `CancelJobCommand` | `cancel_job` | `job_id: str` |

Each subclass sets `command_type` as a class-level default.

Agent reference fields use the SQL schema naming convention: `owner_agent`,
`from_agent`, `to_agent`, `responder_agent`, `completed_by_agent` — matching
the column names in the SQL schema (e.g., `tasks.owner_agent`,
`handoffs.from_agent`).

### __init__.py — Re-exports

All public models, enums, value objects, and constants are re-exported from
`yaga_contracts.__init__` so consumers import directly:

```python
from yaga_contracts import EventEnvelope, CreateRequestBody, HandoffDispatch
```

## Non-Negotiable Boundary Preservation

These architectural boundaries (from `implementation-kickoff-v1.md`) must be
preserved in the contracts layer:

1. **Request routing/publication state vs task/workflow state** — separate DTOs,
   separate status enums (`RequestStatus`/`PublishStatus` vs `TaskStatus`).
2. **Task completion vs callback success vs reply publication success** — three
   distinct concerns with separate events and fields.
3. **Strategic ownership vs execution ownership** —
   `strategic_owner_agent_id` vs `owner_agent` on tasks.
4. **Handoff transport ack vs handoff acceptance vs task completion** — three
   separate DTOs (`HandoffAck`, `HandoffAcceptance`/`HandoffRejection`,
   `CompleteTaskCommand`).
5. **Internal event identity vs external webhook delivery identity** —
   `event_id`/`dedup_key` on `EventEnvelope` vs `event_id` on
   `PublicationStatusWebhook`.

## Testing Strategy

Contract tests (Block H) will verify:
- All models serialize to JSON and deserialize back without data loss.
- Required fields reject `None` / missing values.
- Enum fields reject invalid values.
- Frozen models reject attribute mutation.
- Event envelope `payload` round-trips through `dict`.
- Webhook header constants match expected string values.
- Handoff `from_agent != to_agent` invariant (if enforced via validator).

## Acceptance Criteria

1. All DTOs serialize and validate per architecture docs.
2. Handoff and webhook models preserve required identifier distinctions
   (`event_id` vs `dedup_key`, `request_id` vs `correlation_id`,
   `publish_dedup_key` semantics).
3. Handoff acceptance and task completion are separate contract layers.
4. Runtime-core services can consume internal DTOs rather than raw
   HTTP/persistence payloads.
5. Import-linter contracts pass (contracts remains a leaf package with no
   internal dependencies).
6. `scripts/lint.sh` passes with zero warnings.
7. `scripts/test.sh` passes with contract validation tests.

## Source Documents

- `docs/agent-runtime/02-core-model.md` — entity definitions
- `docs/agent-runtime/03-runtime-and-a2a.md` — request context, ID semantics
- `docs/agent-runtime/04-channel-sessions-and-main-owner-routing.md` — reply target, routing metadata
- `docs/agent-runtime/05-ownership-lifecycle-and-state.md` — task/request statuses, ownership
- `docs/agent-runtime/contracts/http-api-v1.md` — HTTP API contract
- `docs/agent-runtime/contracts/webhook-callback-v1.md` — webhook contract
- `docs/agent-runtime/contracts/event-bus-v1.md` — event bus contract
- `docs/agent-runtime/contracts/internal-a2a-v1.md` — handoff wire format, status enum
- `docs/agent-runtime/reference/canonical-events.md` — event taxonomy
- `docs/agent-runtime/reference/canonical-statuses.md` — status enums
- `docs/agent-runtime/reference/handoff-contract.md` — handoff field requirements
- `docs/agent-runtime/data/sql-schema-v1.md` — table definitions, column types, status vocabularies
- `docs/agent-runtime/data/state-projections-v1.md` — projection schemas
- `docs/agent-runtime/implementation/implementation-kickoff-v1.md` — v1 command set, frozen decisions
- `docs/agent-runtime/implementation/phase-1-task-breakdown-v1.md` — Block B scope
