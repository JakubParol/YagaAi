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
- Compute HMAC SHA-256 over `timestamp + "." + raw_body`.

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
