# Repo Structure v1

## Proposed Layout
```
/apps/api
/apps/worker
/packages/runtime-core
/packages/mission-control
/packages/adapters
/packages/persistence
/packages/contracts
/tests
/docs
```

## Boundaries
- `runtime-core`: orchestration, handoffs, policies.
- `mission-control`: workflow loops and quality gates.
- `adapters`: Discord/WhatsApp/web/CLI ingress + publication.
- `persistence`: SQL repositories + outbox/event store.
- `contracts`: shared schemas for HTTP/A2A/events.
