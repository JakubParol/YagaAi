# SQL Schema v1

## Tables

### `requests`
- `id TEXT PK`
- `correlation_id TEXT NOT NULL`
- `origin TEXT NOT NULL`
- `idempotency_key TEXT NOT NULL` (maps to `Idempotency-Key` header)
- `idempotency_scope TEXT NOT NULL` (caller/auth scope used to isolate idempotency domains for `POST /requests`)
- `payload_fingerprint TEXT NOT NULL` (deterministic hash of canonical request payload)
- `status TEXT NOT NULL DEFAULT 'received'`
- `reply_publish_status TEXT NOT NULL DEFAULT 'pending'` (vocabulary: `pending|attempted|published|failed|unknown|fallback_required|abandoned` per `13-implementation-decisions.md`)
- `reply_target_channel TEXT NOT NULL`
- `reply_target_session_key TEXT NOT NULL`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(correlation_id)`
- `UNIQUE(idempotency_scope, idempotency_key)`
- `INDEX(status, created_at)`
- `INDEX(idempotency_scope, idempotency_key, payload_fingerprint)`
- `INDEX(reply_publish_status, updated_at)`

### `tasks`
- `id TEXT PK`
- `request_id TEXT NOT NULL FK -> requests(id)`
- `owner_agent TEXT NOT NULL`
- `state TEXT NOT NULL`
- `priority TEXT NOT NULL DEFAULT 'normal'`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

Indexes:
- `INDEX(request_id, state)`

### `handoffs`
- `id TEXT PK`
- `task_id TEXT NOT NULL FK -> tasks(id)`
- `from_agent TEXT NOT NULL`
- `to_agent TEXT NOT NULL`
- `callback_target TEXT NOT NULL` (where completion result returns; required for routing per `05-ownership-lifecycle-and-state.md`)
- `correlation_id TEXT NOT NULL` (audit/replay linkage per `11-observability-and-audit.md`)
- `status TEXT NOT NULL`
- `dedup_key TEXT NOT NULL`
- `created_at TIMESTAMP NOT NULL`

Indexes:
- `UNIQUE(dedup_key)`
- `INDEX(to_agent, status)`
- `INDEX(correlation_id)`

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

## Migration Strategy
- Baseline: `alembic revision --autogenerate -m "schema v1 baseline"`.
- Forward-only migrations, no destructive rollback in prod.
- Data migrations separated from schema migrations.
