# Agent Runtime — Documentation

This directory describes the target architecture and operating model for the Agent Runtime.
It covers how the system is designed to behave, what contracts it enforces, and where the
sources of truth live.

Most files here describe the architecture itself.
One file (`11-implementation-decisions.md`) records blocking implementation choices.
One file (`12-channel-sessions-and-main-owner-routing.md`) defines the routing topology for
surface-originated durable work and its integration into the rest of the corpus.

## What Is the Agent Runtime

A workflow-first control plane for multi-agent work. It coordinates separated agents
with their own memory and responsibility, routes commands and events, manages task
lifecycle, tracks request routing and reply publication for user-originated work, and
provides auditability and replay.

It is closer to a distributed workflow engine for agents than to a general-purpose agent framework.

## Who These Docs Are For

- Anyone designing or implementing the runtime
- Anyone building on top of it (new agents, new flows, new domain implementations)
- Anyone operating or debugging a running system

## How to Read These Docs

For the architecture mental model, start with:
1. [00-input-one-pager.md](00-input-one-pager.md)
2. [01-system-overview.md](01-system-overview.md)
3. [02-core-model.md](02-core-model.md)
4. [03-runtime-and-a2a.md](03-runtime-and-a2a.md)
5. [04-ownership-lifecycle-and-state.md](04-ownership-lifecycle-and-state.md)
6. [12-channel-sessions-and-main-owner-routing.md](12-channel-sessions-and-main-owner-routing.md)

If you are implementing the model, read this early as well:
- [11-implementation-decisions.md](11-implementation-decisions.md)

The `reference/` directory contains canonical definitions you can link to from anywhere.

## File Map

| File | What it covers |
|------|---------------|
| [00-input-one-pager.md](00-input-one-pager.md) | Vision, thesis, build principles, and v1 priorities |
| [01-system-overview.md](01-system-overview.md) | High-level mental model, agent roles, surface vs owner-main topology |
| [02-core-model.md](02-core-model.md) | Definitions of entities including request, task, flow, handoff, memory |
| [03-runtime-and-a2a.md](03-runtime-and-a2a.md) | Ingress normalization contract, A2A handoff contract, callbacks |
| [04-ownership-lifecycle-and-state.md](04-ownership-lifecycle-and-state.md) | Ownership rules, task lifecycle, request closure, completion vs publication |
| [05-memory-model.md](05-memory-model.md) | Memory layers, write/read policy, shared facts |
| [06-mission-control-model.md](06-mission-control-model.md) | MC as development-flow specialization of the runtime |
| [07-operational-flows.md](07-operational-flows.md) | End-to-end flows for research, implementation, QA |
| [08-failure-recovery-and-timeouts.md](08-failure-recovery-and-timeouts.md) | Failure modes, recovery paths, timeout semantics |
| [09-observability-and-audit.md](09-observability-and-audit.md) | Request/task observability, audit trail, replay |
| [10-governance-and-v1-boundaries.md](10-governance-and-v1-boundaries.md) | v1 scope, non-goals, control points, edge-case tests |
| [11-implementation-decisions.md](11-implementation-decisions.md) | Blocking implementation decisions, especially for request/routing/publication |
| [12-channel-sessions-and-main-owner-routing.md](12-channel-sessions-and-main-owner-routing.md) | Mandatory topology for surface-originated durable work |

## Reference

| File | What it covers |
|------|---------------|
| [reference/glossary.md](reference/glossary.md) | Definitions of all terms used across docs |
| [reference/canonical-statuses.md](reference/canonical-statuses.md) | Canonical task/US statuses and transition notes |
| [reference/canonical-events.md](reference/canonical-events.md) | Canonical event types and semantics |
| [reference/handoff-contract.md](reference/handoff-contract.md) | Required fields and semantics of a handoff |
| [reference/artifact-model.md](reference/artifact-model.md) | Artifact types, lifecycle, and usage |
| [reference/agent-roles.md](reference/agent-roles.md) | Agent definitions, ownership, and scope |

## Important Navigation Note

Doc 12 is no longer just an isolated side note.
It defines the ingress / owner-coordination / reply-publication topology for durable
surface-originated work, and the rest of this corpus is now aligned to that model.