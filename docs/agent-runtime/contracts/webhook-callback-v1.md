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
  "status":"published",
  "channel":"discord",
  "session_key":"disc:abc",
  "published_at":"2026-04-04T10:05:00Z"
}
```

## Retry Semantics
- Producer retries on non-2xx with exponential backoff (1s, 5s, 30s, 2m, 10m).
- Max 5 attempts then dead-letter.
- Consumer must be idempotent by `event_id`.

> **Why `event_id` here, not `dedup_key`?** For external inbound webhooks, `event_id` is bound to the HMAC signature (it appears in the signed string and in `X-Yaga-Event-Id`). The producer guarantees `event_id` stability across retries of the same publication event. This makes `event_id` serve the idempotency-fence role that `dedup_key` serves internally. The webhook payload has no `dedup_key` field; do not add one — callers should use `event_id` exclusively.
