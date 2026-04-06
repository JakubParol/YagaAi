# State Projections v1

## Projections

### `request_projection`
Request lifecycle and publication state. Primary operator view for routing and publish status.

Fields:
- `request_id TEXT PK`
- `status TEXT NOT NULL` (lifecycle: `received|normalized|delegated|awaiting_callback|reply_publish_pending|reply_published|reply_publish_failed|fallback_required|closed`)
- `reply_publish_status TEXT NOT NULL DEFAULT 'pending'` (vocabulary: `pending|attempted|published|failed|unknown|fallback_required|abandoned`)
- `origin TEXT NOT NULL`
- `origin_session_key TEXT`
- `request_class TEXT NOT NULL`
- `strategic_owner_agent_id TEXT`
- `current_owner_agent_id TEXT`
- `reply_target_channel TEXT NOT NULL`
- `reply_target_session_key TEXT NOT NULL`
- `reply_target_json TEXT NOT NULL`
- `reply_target_version INTEGER NOT NULL`
- `publish_dedup_key TEXT`
- `correlation_id TEXT NOT NULL`
- `last_stream_sequence BIGINT NOT NULL`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

### `task_projection`
Current task owner, state, and loop counters. Read by policy handlers (escalation gates).

Fields:
- `task_id TEXT PK`
- `request_id TEXT` (nullable for tasks not tied to a user request)
- `owner_agent TEXT NOT NULL`
- `state TEXT NOT NULL` (canonical task statuses per `reference/canonical-statuses.md`)
- `priority TEXT NOT NULL DEFAULT 'normal'`
- `review_loop_count INTEGER NOT NULL DEFAULT 0` (EscalateOnReviewLimitReached fires at > 3 per `reference/canonical-statuses.md`)
- `verify_loop_count INTEGER NOT NULL DEFAULT 0` (EscalateOnVerifyLimitReached fires at > 2 per `reference/canonical-statuses.md`)
- `callback_target TEXT NOT NULL`
- `last_stream_sequence BIGINT NOT NULL`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

### `publication_projection`
Per-channel publication attempts and outcomes. Used for retry decisions and operator alerts.

Fields:
- `publication_id TEXT PK`
- `request_id TEXT NOT NULL`
- `publish_dedup_key TEXT NOT NULL`
- `channel TEXT NOT NULL`
- `session_key TEXT NOT NULL`
- `status TEXT NOT NULL` (`pending|attempted|published|failed|unknown|fallback_required|abandoned`)
- `attempt_count INTEGER NOT NULL DEFAULT 0`
- `last_attempt_at TIMESTAMP`
- `last_error TEXT`
- `last_delivery_event_id TEXT`
- `published_at TIMESTAMP`
- `last_stream_sequence BIGINT NOT NULL`
- `created_at TIMESTAMP NOT NULL`
- `updated_at TIMESTAMP NOT NULL`

## Materialization
- Event chronology source of truth: `event_log`.
- Request-routing and publication source of truth: runtime request/publication records.
- Projection workers consume ordered aggregate streams.
- Upsert by projection primary key.

## Writer Responsibility
- Runtime Projection Worker writes runtime projections.
- Mission Control Projection Worker writes review/verify loop projections.
- No direct writes from agent executors.

## Conflict Resolution
- Last-write-wins by `(occurred_at, event_id)` for tie-break safety only.
- Track and persist `last_stream_sequence` per projection row.
- Reject stale event if incoming `stream_sequence <= last_stream_sequence` for the same aggregate stream.
- Emit `transition.rejected` for invalid transitions.
