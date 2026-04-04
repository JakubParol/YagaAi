# Security Baseline v1

## AuthN / AuthZ
- Service-to-service: signed JWT with short TTL.
- Operator access: OIDC + role-based authorization.
- Least privilege per service account.

## Secrets
- Secrets loaded from secret manager, never committed.
- Rotation every 90 days.
- Webhook signing secrets scoped per adapter.

## Data Retention / Redaction
- Prompt payload retention: 30 days default.
- Audit logs retention: 180 days.
- Redact access tokens, credentials, and direct PII in logs.

## PII and Audit
- Classify user text as potentially sensitive by default.
- Record read/write access in immutable audit trail.
- Incident review required for unauthorized access signals.
