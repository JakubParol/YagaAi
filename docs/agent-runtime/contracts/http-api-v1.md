# HTTP API Contract v1

## Base
- Base path: `/api/v1`
- Content-Type: `application/json`
- Auth (default): `Authorization: Bearer <token>`
- Auth exception: `POST /webhooks/publication-status` does **not** use bearer auth; it must be authenticated via `X-Yaga-Signature`, `X-Yaga-Timestamp`, and `X-Yaga-Event-Id` HMAC callback headers (see `webhook-callback-v1.md`).

## Endpoints

### `POST /requests`
Create normalized request ingress.

**Request**
```json
{
  "origin": "discord",
  "payload": {"text": "Implement feature X"},
  "reply_target": {"channel": "discord", "session_key": "disc:abc"}
}
```

Validation:
- `origin` enum: `whatsapp|discord|web|cli`.
- `payload.text` required for text inputs.
- `request_id` and `correlation_id` are runtime-owned identifiers and are **not accepted** from external callers in `POST /requests`.
- Runtime assigns `request_id` at ingress normalization and `correlation_id` at strategic-owner normalization per `03-runtime-and-a2a.md` ID generation rules.

**Response `202 Accepted`**
```json
{"status":"accepted","request_id":"req_01","task_ref":"task_01"}
```

`task_ref` is present when the strategic owner immediately creates a task upon acceptance; `null` when task creation is deferred to a subsequent workflow step.

### `GET /requests/{request_id}`
Returns request read model.

**Response `200 OK`**
```json
{
  "request_id": "req_01",
  "status": "delegated",
  "reply_publish_status": "pending",
  "origin": "discord",
  "strategic_owner_agent_id": "james",
  "reply_target": {"channel": "discord", "session_key": "disc:abc"},
  "correlation_id": "corr_01",
  "created_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T10:01:00Z"
}
```

`status` lifecycle: `received|normalized|delegated|awaiting_callback|reply_publish_pending|reply_published`.
`reply_publish_status` vocabulary: `pending|attempted|published|failed|unknown|fallback_required|abandoned`.

### `POST /webhooks/publication-status`
Adapter callback for publication outcome (canonical path; full route: `/api/v1/webhooks/publication-status`).
This endpoint is a signed inbound webhook and must accept valid `X-Yaga-*` signature headers without requiring `Authorization: Bearer <token>`.

## Error Taxonomy
| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Schema or field validation failed |
| `AUTH_REQUIRED` | 401 | Missing/invalid auth |
| `FORBIDDEN` | 403 | Caller lacks permission |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Duplicate or invalid state transition |
| `UNPROCESSABLE_STATE` | 422 | Business invariant failure |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected runtime error |

Error body:
```json
{"error":{"code":"VALIDATION_ERROR","message":"origin is required","details":[]}}
```

## Idempotency Rules
- `POST /requests` requires `Idempotency-Key` header.
- Same key + same payload => return original `202` response.
- Same key + different payload => `409 CONFLICT`.
- `Idempotency-Key` uniqueness is scoped to the authenticated caller identity (`idempotency_scope` in the `requests` table). Two different callers using the same `Idempotency-Key` value are treated as independent requests and do not conflict.
- Callback endpoints dedupe by stable `event_id`; signature timestamp is used only for freshness/replay-window validation.
