# Webhook Callback Contract v1

## Endpoint
`POST /api/v1/webhooks/publication-status` (canonical publication callback endpoint used across runtime contracts)

## Signature
Headers:
- `X-Yaga-Signature: sha256=<hex>`
- `X-Yaga-Timestamp: <unix-seconds>`
- `X-Yaga-Event-Id: <unique-id>`

Verification:
- Reject if timestamp drift > 300s.
- Compute HMAC SHA-256 over `timestamp + "." + event_id + "." + raw_body`, where `event_id` is the exact value from `X-Yaga-Event-Id`.
- Reject if `X-Yaga-Event-Id` and payload `event_id` do not match exactly.

## Payload
```json
{
  "event_id":"evt_100",
  "request_id":"req_01",
  "publication_id":"pub_01",
  "publish_dedup_key":"pub_req_01_final",
  "status":"published",
  "channel":"discord",
  "session_key":"disc:abc",
  "published_at":"2026-04-04T10:05:00Z"
}
```

## Retry Semantics
- Producer retries on non-2xx with exponential backoff (1s, 5s, 30s, 2m, 10m).
- Max 5 attempts then dead-letter.
- Consumer must be idempotent by webhook delivery `event_id`.

`event_id` here is the transport delivery identifier for this webhook callback. It is distinct
from the internal event-bus `event_id` stored in `event_log`.

`publish_dedup_key` remains the authoritative identity of the human-visible publication intent.
The webhook uses `event_id` for transport-level idempotency and `publish_dedup_key` to reconcile
with runtime publication state.
