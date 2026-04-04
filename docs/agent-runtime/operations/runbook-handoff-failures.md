# Runbook: Handoff Failures

## Detection
- `handoff.timeout` growth.
- Watchdog fired without `handoff.accepted`.

## Triage
1. Check assignee agent availability.
2. Validate handoff payload completeness.
3. Confirm callback target exists.

## Safe Retry
- Re-dispatch with new `handoff_id`, same `correlation_id`.
- Keep original handoff linked for audit.

## Rollback / Repair
- Reassign ownership to requester.
- Escalate to James after repeated rejection/timeout.

## Post-Incident
- Update timeout policy window if systematic.
