# Runbook: Ingress Failures

## Detection
- Spike in `request.normalization_rejected`.
- HTTP 5xx increase on `/api/v1/requests`.

## Triage
1. Confirm adapter health.
2. Validate auth and idempotency key presence.
3. Inspect recent `command.rejected` events.

## Safe Retry
- Retry only with same idempotency key.
- Do not replay malformed payloads without fix.

## Rollback / Repair
- Disable failing adapter route.
- Reprocess queued valid events from outbox.

## Post-Incident
- Add correlation IDs to incident timeline.
- Document root cause + policy updates.
