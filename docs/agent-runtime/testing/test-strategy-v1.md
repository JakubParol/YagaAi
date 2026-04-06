# Test Strategy v1

## Test Pyramid
- Unit: domain rules, policy handlers, DTO validation.
- Integration: repositories, event outbox, adapter integrations.
- E2E: ingress -> task -> handoff -> publication callback.

## Contract Matrix
- HTTP contracts: request validation + error mapping.
- A2A contracts: handoff acceptance/rejection semantics.
- Task contracts: task completion semantics.
- Event contracts: envelope schema and topic routing.
- Webhook contracts: signature verification and retries.

## Failure-Recovery Matrix
- Timeout: handoff acceptance timeout -> escalation.
- Retry: publication failure -> retry -> DLQ.
- Duplicate delivery: idempotency on ingress and callbacks.
- Partial failure: memory write failure should not block task completion.
- Ambiguous publication: retry ambiguity reconciles without duplicate human-visible output.
- Late signals: callback or publish confirmation after reassignment/cancellation reconciles against current authority.
