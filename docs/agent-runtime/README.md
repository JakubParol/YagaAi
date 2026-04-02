# Agent Runtime — Documentation

This is the target architecture and target operating model for the Agent Runtime.
It is not an implementation plan. It describes how the system is designed to behave,
what contracts it enforces, and why.

## What Is the Agent Runtime

A workflow-first control plane for multi-agent work. It coordinates separated agents
with their own memory and responsibility, routes commands and events, manages task
lifecycle, and provides full auditability and replay.

It is closer to a distributed workflow engine for agents than to a general-purpose agent framework.

## Who These Docs Are For

- Anyone designing or implementing the runtime
- Anyone building on top of it (new agents, new flows, new domain implementations)
- Anyone operating or debugging a running system

## How to Read These Docs

Start with `01-system-overview.md` for a mental model of the system.
Then `02-core-model.md` for precise definitions of all entities.
Then `03-runtime-and-a2a.md` and `04-ownership-lifecycle-and-state.md` for the
operational contracts.

The remaining files cover specific subsystems. The `reference/` directory contains
canonical definitions you can link to from anywhere.

## File Map

| File | What it covers |
|------|---------------|
| [01-system-overview.md](01-system-overview.md) | What we are building, why, who the agents are |
| [02-core-model.md](02-core-model.md) | Definitions of all entities and their relations |
| [03-runtime-and-a2a.md](03-runtime-and-a2a.md) | Communication contracts, handoff protocol, A2A |
| [04-ownership-lifecycle-and-state.md](04-ownership-lifecycle-and-state.md) | Ownership rules, task lifecycle, status transitions |
| [05-memory-model.md](05-memory-model.md) | Memory layers, write/read policy, shared facts |
| [06-mission-control-model.md](06-mission-control-model.md) | MC as domain implementation of the runtime |
| [07-operational-flows.md](07-operational-flows.md) | End-to-end flows: research, dev, QA |
| [08-failure-recovery-and-timeouts.md](08-failure-recovery-and-timeouts.md) | Failure modes, recovery paths, timeout semantics |
| [09-observability-and-audit.md](09-observability-and-audit.md) | Structured events, correlation, audit trail, replay |
| [10-governance-and-v1-boundaries.md](10-governance-and-v1-boundaries.md) | v1 scope, non-goals, human control points, success criteria |
| [11-implementation-decisions.md](11-implementation-decisions.md) | Architectural decisions to make before implementation: transport, deployment, runtime interface |

### Reference

| File | What it covers |
|------|---------------|
| [reference/glossary.md](reference/glossary.md) | Definitions of all terms used across docs |
| [reference/canonical-statuses.md](reference/canonical-statuses.md) | Complete status list with transitions |
| [reference/canonical-events.md](reference/canonical-events.md) | Event types, shape, and semantics |
| [reference/handoff-contract.md](reference/handoff-contract.md) | Required fields and semantics of a handoff |
| [reference/artifact-model.md](reference/artifact-model.md) | Artifact types, lifecycle, and usage |
| [reference/agent-roles.md](reference/agent-roles.md) | Agent definitions, ownership, and scope |
