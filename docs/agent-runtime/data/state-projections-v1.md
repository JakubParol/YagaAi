# State Projections v1

## Projections
- `request_projection`: request lifecycle + publication status.
- `task_projection`: current task owner/state/loop counters.
- `publication_projection`: channel publication attempts and outcomes.

## Materialization
- Source of truth: `event_log`.
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
