# Runbook: Publication Failures

## Detection
- `reply.publication_failed` rate alert.
- DLQ growth for publication topics.

## Triage
1. Verify external channel API status.
2. Check signature/auth failures.
3. Confirm payload size and format limits.

## Safe Retry
- Reuse original `publish_dedup_key` for the same human-visible publication intent.
- Follow backoff policy; do not hot-loop.

## Rollback / Repair
- Invoke fallback reply target.
- Queue manual publish for critical responses.

## Post-Incident
- Annotate request records with publication RCA.
