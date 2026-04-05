# Definition of Done v1

## Required PR Checks
- Lint/format pass.
- Unit tests pass.
- Relevant integration tests pass.
- Contract tests updated for changed API/event schemas.
- Docs updated for behavioral changes.

## Coverage Targets
- Domain critical path (ingress, handoff, publication): >= 85% lines.
- Overall project floor: >= 70% lines.

## Critical Path Checks
- Idempotent ingress verified.
- Handoff timeout/escalation path verified.
- Publication retry and DLQ behavior verified.
