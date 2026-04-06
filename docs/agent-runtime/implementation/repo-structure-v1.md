# Repo Structure v1

> **Status:** This is the **target v1 layout** to be created during implementation. The repository currently contains only `docs/` and `README.md`. No application directories exist yet.

## Directory Convention

- `services/` — long-running daemons that own state and host background workers.
- `apps/` — user-facing entry points (UI, CLI) that consume service APIs but do not own state directly.

## Proposed Layout
```
/apps/web        ← Next.js Web UI (built-in surface per 14-hld-runtime-shape-and-installation.md)
/apps/cli        ← Typer CLI (yaga command per 15-tech-stack.md)
/services/runtime ← local runtime daemon: HTTP API, webhooks, projection workers, retry/watchdog loops
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
- `services/runtime`: local runtime daemon; hosts HTTP layer plus in-process worker loops and delegates to `runtime-core` and `persistence`.
- `apps/web`: read-only consumer of the runtime local API; no direct DB access.
- `apps/cli`: thin wrapper over the runtime local API/socket; no direct DB access.
