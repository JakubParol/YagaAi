# Runbook: Handoff Failures

## Detection
- `handoff.timeout` growth.
- Watchdog fired without `handoff.accepted`.

## Triage
1. Check assignee agent availability.
2. Validate handoff payload completeness.
3. Confirm callback target exists.

## Safe Retry

Two distinct operations — do not conflate them:

**Transport retry (same handoff intent):** Re-send the original message with the same `handoff_id` and same `dedup_key`. The `UNIQUE(dedup_key)` constraint on the `handoffs` table makes this idempotent — the assignee receives the message again but creates no duplicate record. Use this when the dispatch message was lost in transit but the handoff record was never created or accepted.

**Explicit reassignment (new handoff intent):** Create a new `handoff_id` (and derived `dedup_key`), same `correlation_id`, explicitly closing or voiding the prior handoff record first. Use this when the assignee timed out, rejected, or is unavailable — i.e., the original handoff record exists but is terminal. Audit linkage: record the prior `handoff_id` in the new handoff's `summary` or a `causation_id` reference.

## Rollback / Repair
- Reassign ownership to requester.
- Escalate to James after repeated rejection/timeout.

## Post-Incident
- Update timeout policy window if systematic.
