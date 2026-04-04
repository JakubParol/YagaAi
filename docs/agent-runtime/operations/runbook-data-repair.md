# Runbook: Data Repair

## Detection
- Projection drift vs event log.
- Missing request/task links.

## Triage
1. Identify affected aggregate IDs.
2. Compare projection versions to event stream.
3. Confirm corruption scope (single projection vs schema issue).

## Safe Retry
- Rebuild projection from event log checkpoint.
- Pause writers for affected projection during repair.

## Rollback / Repair
- Restore from snapshot backup if event log damaged.
- Run targeted SQL fix script with peer review.

## Post-Incident
- Create audit record of changed rows and operator.
- Add automated drift detector rule if missing.
