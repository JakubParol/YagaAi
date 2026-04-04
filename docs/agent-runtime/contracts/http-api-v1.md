# HTTP API Contract v1

## Base
- Base path: `/api/v1`
- Content-Type: `application/json`
- Auth: `Authorization: Bearer <token>`

## Endpoints

### `POST /requests`
Create normalized request ingress.

**Request**
```json
{
  "request_id": "req_01",
  "correlation_id": "corr_01",
  "origin": "discord",
  "payload": {"text": "Implement feature X"},
  "reply_target": {"channel": "discord", "session_key": "disc:abc"}
}
```

Validation:
- `request_id`, `correlation_id` required, max 128 chars.
- `origin` enum: `whatsapp|discord|web|cli`.
- `payload.text` required for text inputs.

**Response `202 Accepted`**
```json
{"status":"accepted","request_id":"req_01","task_ref":"task_01"}
```

### `GET /requests/{request_id}`
Returns request read model.

### `POST /callbacks/publication`
Adapter callback for publication outcome.

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
- Callback endpoints use `event_id` + signature timestamp as dedupe key.
