# Security Baseline v1

## AuthN / AuthZ
- Service-to-service: signed JWT with short TTL. This path is used by surface adapters calling `POST /requests` and by internal services calling runtime endpoints. Each adapter has a dedicated service account with least-privilege scope.
- Operator access: OIDC + role-based authorization.
- Least privilege per service account.
- Inbound webhook callbacks (`POST /webhooks/publication-status`): authenticated via HMAC signature (`X-Yaga-Signature`), not bearer token. See `contracts/webhook-callback-v1.md`.

## Secrets
- Secrets loaded from secret manager, never committed.
- Rotation every 90 days.
- Webhook signing secrets scoped per adapter.

## Data Retention / Redaction
- Prompt payload retention: 30 days default.
- Audit logs retention: 180 days.
- Redact access tokens, credentials, and direct PII in logs.

## Rate Limiting
- Default: 60 requests/minute per authenticated caller (`idempotency_scope`) for `POST /requests`.
- Read endpoints (`GET /requests/{id}`): 300 requests/minute per caller.
- Webhook callback endpoint: 120 requests/minute per adapter (identified by signing secret scope).
- Burst headroom: 2× limit for up to 10 seconds before throttling applies.
- All rate limit violations return `429 RATE_LIMITED` with `Retry-After` header (seconds until next window).
- Limits are configurable per environment; production defaults above. Do not hard-code limits in application code — read from config.

## PII and Audit
- Classify user text as potentially sensitive by default.
- Record read/write access in immutable audit trail.
- Incident review required for unauthorized access signals.
