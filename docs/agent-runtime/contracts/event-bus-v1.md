# Event Bus Contract v1

## Topic Naming
`yaga.v1.<bounded_context>.<aggregate>.<event_name>`

Examples:
- `yaga.v1.runtime.request.received`
- `yaga.v1.runtime.handoff.accepted`
- `yaga.v1.mission_control.review_loop.incremented`

## Event Envelope
```json
{
  "event_id":"evt_01",
  "event_type":"request.received",
  "occurred_at":"2026-04-04T10:00:00Z",
  "actor":{"type":"agent","id":"james"},
  "correlation_id":"corr_01",
  "causation_id":"evt_00",
  "version":"v1",
  "payload":{}
}
```

Required fields: `event_id,event_type,occurred_at,correlation_id,version,payload`.

## Delivery Guarantees
- At-least-once delivery.
- Ordering guaranteed per aggregate stream key.
- Consumers must implement idempotent handling by `event_id`.

## Retry / Dead Letter
- Retry policy: 5 attempts, exponential backoff.
- Terminal failures routed to DLQ topic: `yaga.v1.dlq.<source_topic>`.
- DLQ handlers emit `retry.exhausted` and operator alert.
