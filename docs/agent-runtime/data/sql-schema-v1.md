# SQL Schema v1

## Tables

### `requests`
- `id TEXT PK`
- `correlation_id TEXT NOT NULL`
- `origin TEXT NOT NULL`
- `origin_session_key TEXT`
- `idempotency_key TEXT NOT NULL` (maps to `Idempotency-Key` header)
- `idempotency_scope TEXT NOT NULL` (caller/auth scope used to isolate idempotency domains for `POST /requests`)
- `payload_fingerprint TEXT NOT NULL` (deterministic hash of canonical request payload)
- `request_class TEXT NOT NULL DEFAULT 'durable'`
- `status TEXT NOT NULL DEFAULT 'received'`
- `reply_publish_status TEXT NOT NULL DEFAULT 'pending'` (vocabulary: `pending|attempted|published|failed|unknown|fallback_required|abandoned` per `13-implementation-decisions.md`)
- `reply_target_channel TEXT NOT NULL`
- `reply_target_session_key TEXT NOT NULL`
- `reply_target_json TEXT NOT NULL` (JSON object: `{"channel":"<channel>","session_key":"<key>","adapter_metadata":{}}` — canonical structured reply target; `reply_target_channel` and `reply_target_session_key` are denormalized projections of this field for indexed queries)
- `reply_target_version INTEGER NOT NULL DEFAULT 1` (incremented when reply target is updated, e.g. fallback routing)
- `publish_dedup_key TEXT` (nullable; set when the first publication intent is created for this request. `UNIQUE` constraint only activates for non-NULL values — multiple requests without a publish intent yet are allowed)
- `fallback_reply_target_json TEXT` (same JSON shape as `reply_target_json`; nullable; used by `InvokeReplyFallback` policy when primary target fails)
- `strategic_owner_agent_id TEXT` (nullable; set by strategic owner at normalization; authoritative per `13-implementation-decisions.md` Decision 7)
- `current_owner_agent_id TEXT`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(correlation_id)`
- `UNIQUE(idempotency_scope, idempotency_key)`
- `UNIQUE(publish_dedup_key)`
- `INDEX(status, created_at)`
- `INDEX(idempotency_scope, idempotency_key, payload_fingerprint)`
- `INDEX(reply_publish_status, updated_at)`

### `tasks`
- `id TEXT PK`
- `request_id TEXT FK -> requests(id)` (nullable for agent-internal tasks not tied to a user request)
- `owner_agent TEXT NOT NULL`
- `state TEXT NOT NULL` (vocabulary: `Created|Accepted|In Progress|Review|Verify|Done|Blocked|Escalated|Cancelled` per `reference/canonical-statuses.md`)
- `priority TEXT NOT NULL DEFAULT 'normal'`
- `callback_target TEXT NOT NULL` (where task completion result returns; routes to strategic owner main for user-originated work)
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `INDEX(request_id, state)`

### `handoffs`
- `id TEXT PK`
- `task_id TEXT NOT NULL FK -> tasks(id)` (set by the runtime at dispatch time from the originating task context; not present in the A2A wire payload — see `contracts/internal-a2a-v1.md`)
- `from_agent TEXT NOT NULL`
- `to_agent TEXT NOT NULL`
- `goal TEXT NOT NULL` (assignee mandate; persisted for restart recovery per `13-implementation-decisions.md`)
- `definition_of_done TEXT NOT NULL` (completion criteria; persisted for restart recovery)
- `callback_target TEXT NOT NULL` (where completion result returns; required for routing per `05-ownership-lifecycle-and-state.md`)
- `correlation_id TEXT NOT NULL` (audit/replay linkage per `11-observability-and-audit.md`)
- `status TEXT NOT NULL` (vocabulary: `received|accepted|rejected|completed|failed|blocked`)
- `outcome TEXT` (nullable; set on completion: `done|partial|failed|blocked|escalated`)
- `summary TEXT` (nullable; completion summary provided by assignee agent)
- `artifacts_json TEXT` (nullable; JSON array of artifact references, e.g. `["artifact://research/v1.md"]`)
- `dedup_key TEXT NOT NULL`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(dedup_key)`
- `INDEX(to_agent, status)`
- `INDEX(correlation_id)`
- `INDEX(status, updated_at)`

### `publications`
- `id TEXT PK`
- `request_id TEXT NOT NULL FK -> requests(id)`
- `publish_dedup_key TEXT NOT NULL`
- `channel TEXT NOT NULL`
- `session_key TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'pending'` (vocabulary: `pending|attempted|published|failed|unknown|fallback_required|abandoned` per `13-implementation-decisions.md` Decision 4)
- `attempt_count INTEGER NOT NULL DEFAULT 0`
- `last_attempt_at TIMESTAMP`
- `last_error TEXT`
- `last_delivery_event_id TEXT`
- `published_at TIMESTAMP`
- `last_stream_sequence BIGINT NOT NULL DEFAULT 0`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Uniqueness note: publications are keyed by `publish_dedup_key` (intent identity) rather than `(request_id, channel, session_key)` (delivery coordinates). This allows the same request to target different channels over its lifetime (e.g. fallback routing) while ensuring each publication intent is tracked exactly once.

Indexes:
- `UNIQUE(publish_dedup_key)`
- `INDEX(status, updated_at)`

### `event_log`
- `event_id TEXT PK`
- `dedup_key TEXT NOT NULL` (stable across retries of the same intent; idempotency fence for at-least-once delivery)
- `event_type TEXT NOT NULL`
- `aggregate_type TEXT NOT NULL`
- `aggregate_id TEXT NOT NULL`
- `correlation_id TEXT NOT NULL`
- `causation_id TEXT`
- `actor_json TEXT NOT NULL` (JSON: `{"type":"agent"|"runtime"|"adapter","id":"<id>"}`)
- `payload_json TEXT NOT NULL`
- `schema_version TEXT NOT NULL`
- `stream_sequence BIGINT NOT NULL`
- `occurred_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(dedup_key)`
- `UNIQUE(aggregate_type, aggregate_id, stream_sequence)`
- `INDEX(aggregate_type, aggregate_id, stream_sequence)`
- `INDEX(aggregate_type, aggregate_id, occurred_at)`
- `INDEX(correlation_id, occurred_at)`
- `INDEX(dedup_key, occurred_at)`

### `command_log`
- `command_id TEXT PK`
- `command_type TEXT NOT NULL`
- `aggregate_type TEXT NOT NULL`
- `aggregate_id TEXT NOT NULL`
- `correlation_id TEXT NOT NULL`
- `causation_id TEXT`
- `actor_json TEXT NOT NULL`
- `payload_json TEXT NOT NULL`
- `dedup_key TEXT NOT NULL`
- `status TEXT NOT NULL` (`accepted|rejected|processed`)
- `schema_version TEXT NOT NULL`
- `occurred_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(dedup_key)`
- `INDEX(aggregate_type, aggregate_id, occurred_at)`
- `INDEX(correlation_id, occurred_at)`

### `event_outbox`
- `id TEXT PK`
- `event_id TEXT NOT NULL FK -> event_log(event_id)`
- `status TEXT NOT NULL` (`pending|dispatched|failed`)
- `attempt_count INTEGER NOT NULL DEFAULT 0`
- `next_attempt_at TIMESTAMP`
- `last_error TEXT`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(event_id)`
- `INDEX(status, next_attempt_at)`

### `jobs`
- `id TEXT PK`
- `job_type TEXT NOT NULL`
- `subject_type TEXT NOT NULL`
- `subject_id TEXT NOT NULL`
- `policy_name TEXT`
- `status TEXT NOT NULL` (`scheduled|running|completed|failed|cancelled`)
- `run_at TIMESTAMP NOT NULL`
- `attempt_count INTEGER NOT NULL DEFAULT 0`
- `payload_json TEXT`
- `last_error TEXT`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `INDEX(status, run_at)`
- `INDEX(job_type, status, run_at)`
- `INDEX(subject_type, subject_id)`

## Migration Strategy
- Baseline: `alembic revision --autogenerate -m "schema v1 baseline"`.
- Forward-only migrations, no destructive rollback in prod.
- Data migrations separated from schema migrations.

## Type Notes
- `BIGINT` columns (`stream_sequence`, `last_stream_sequence`) map to SQLite's `INTEGER` affinity (64-bit signed). SQLite ignores the type name; Alembic handles dialect-specific mapping. No data loss risk on SQLite — this notation documents the intended numeric range.
