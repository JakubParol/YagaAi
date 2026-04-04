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
  "dedup_key":"msg_req_123_request_received_attempt_1",
  "event_type":"request.received",
  "aggregate_type":"request",
  "aggregate_id":"req_123",
  "occurred_at":"2026-04-04T10:00:00Z",
  "actor":{"type":"agent","id":"james"},
  "correlation_id":"corr_01",
  "causation_id":"evt_00",
  "schema_version":"v1",
  "stream_sequence":42,
  "payload":{}
}
```

Required fields: `event_id,dedup_key,event_type,aggregate_type,aggregate_id,occurred_at,actor,correlation_id,schema_version,stream_sequence,payload`. `causation_id` is required except on root events (first event in a causal chain), where it MAY be omitted.

Aggregate stream key is defined as `aggregate_type + ":" + aggregate_id` and is the key used for partitioning and ordering.

`stream_sequence` MUST be a monotonically increasing integer scoped to the aggregate stream key and MUST advance by exactly 1 for each new persisted event in that stream.

## Delivery Guarantees
- At-least-once delivery.
- Ordering guaranteed per aggregate stream key.
- Consumers must implement idempotent handling by `dedup_key`.
- `event_id` remains a unique event identity, but retries of the same intent must keep the same `dedup_key` even when transport republishes with a new `event_id`.

## Retry / Dead Letter
- Retry policy: 5 attempts, exponential backoff.
- Terminal failures routed to DLQ topic: `yaga.v1.dlq.<source_topic>`.
- DLQ handlers emit `retry.exhausted` and operator alert.
