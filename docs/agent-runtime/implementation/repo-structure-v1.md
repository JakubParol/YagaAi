# Repo Structure v1

> **Status:** This is the **target v1 layout** to be created during implementation. The repository currently contains only `docs/` and `README.md`. No application directories exist yet.

## Proposed Layout
```
/apps/api        ← FastAPI HTTP server (ingress, webhooks, read models)
/apps/worker     ← background event processor, watchdog loops, projection workers
/apps/ui         ← Next.js Web UI (built-in surface per 14-hld-runtime-shape-and-installation.md)
/apps/cli        ← Typer CLI (yaga command per 15-tech-stack.md)
/packages/       ← Python packages (not npm workspaces; ui is the only TypeScript app)
  runtime-core
  mission-control
  adapters
  persistence
  contracts
/tests
/docs
```

## Boundaries
- `runtime-core`: orchestration, handoffs, policies, watchdogs.
- `mission-control`: workflow loops and quality gates (review/verify counters, escalation).
- `adapters`: Discord/WhatsApp/web/CLI ingress + publication.
- `persistence`: SQL repositories + outbox/event store.
- `contracts`: shared schemas for HTTP/A2A/events.
- `apps/api`: thin HTTP layer; delegates to `runtime-core` and `persistence`.
- `apps/worker`: consumes event streams; runs projection workers, policy enforcer, retry loops.
- `apps/ui`: read-only consumer of `apps/api`; no direct DB access.
- `apps/cli`: thin wrapper over `apps/api` local socket; no direct DB access.
