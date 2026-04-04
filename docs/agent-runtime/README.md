# Agent Runtime — Documentation

This directory describes the target architecture and operating model for the Agent Runtime.
It covers how the system is designed to behave, what contracts it enforces, and where the
sources of truth live.

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

Read in order. Each document assumes the previous ones.

**Start here for the mental model:**
1. [00-input-one-pager.md](00-input-one-pager.md) — vision and build principles
2. [01-system-overview.md](01-system-overview.md) — high-level mental model
3. [02-core-model.md](02-core-model.md) — core entities and their relationships

**Communication and routing:**

4. [03-runtime-and-a2a.md](03-runtime-and-a2a.md) — message types, A2A contracts
5. [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md) — ingress topology, normalization contract
6. [05-ownership-lifecycle-and-state.md](05-ownership-lifecycle-and-state.md) — ownership rules, task lifecycle

**How agents work internally:**

7. [06-internal-prompt-architecture.md](06-internal-prompt-architecture.md) — prompt layering, runtime enforcement, skills
8. [07-memory-model-and-vectorization.md](07-memory-model-and-vectorization.md) — memory layers, retrieval planes, vectorization

**Operations and flows:**

9. [08-mission-control-model.md](08-mission-control-model.md) — MC as the development-flow domain implementation
10. [09-operational-flows.md](09-operational-flows.md) — end-to-end flows for research, implementation, QA
11. [10-failure-recovery-and-timeouts.md](10-failure-recovery-and-timeouts.md) — failure modes, recovery paths, timeouts
12. [11-observability-and-audit.md](11-observability-and-audit.md) — request/task observability, audit trail, replay

**Governance and implementation:**

13. [12-governance-and-v1-boundaries.md](12-governance-and-v1-boundaries.md) — v1 scope, non-goals, control points
14. [13-implementation-decisions.md](13-implementation-decisions.md) — blocking implementation choices for request/routing/publication
15. [14-hld-runtime-shape-and-installation.md](14-hld-runtime-shape-and-installation.md) — runtime shape, deployment patterns
16. [15-tech-stack.md](15-tech-stack.md) — concrete technology choices with rationale

The `reference/` directory contains canonical definitions you can link to from anywhere.

## File Map

| File | What it covers |
|------|---------------|
| [00-input-one-pager.md](00-input-one-pager.md) | Vision, thesis, build principles, and v1 priorities |
| [01-system-overview.md](01-system-overview.md) | High-level mental model, agent roles, surface vs owner-main topology |
| [02-core-model.md](02-core-model.md) | Definitions of entities: request, task, flow, handoff, memory, artifact |
| [03-runtime-and-a2a.md](03-runtime-and-a2a.md) | Message types, A2A handoff contract, callbacks, correlation/dedup |
| [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md) | Ingress normalization contract, mandatory routing topology for surface-originated work |
| [05-ownership-lifecycle-and-state.md](05-ownership-lifecycle-and-state.md) | Ownership rules, task lifecycle, request closure, completion vs publication |
| [06-internal-prompt-architecture.md](06-internal-prompt-architecture.md) | Prompt layering, runtime enforcement split, skills/playbooks, memory injection |
| [07-memory-model-and-vectorization.md](07-memory-model-and-vectorization.md) | Memory layers, write/read policy, retrieval planes, hybrid search, vectorization |
| [08-mission-control-model.md](08-mission-control-model.md) | MC as development-flow specialization of the runtime |
| [09-operational-flows.md](09-operational-flows.md) | End-to-end flows for research, implementation, QA |
| [10-failure-recovery-and-timeouts.md](10-failure-recovery-and-timeouts.md) | Failure modes, recovery paths, timeout semantics |
| [11-observability-and-audit.md](11-observability-and-audit.md) | Request/task observability, audit trail, replay |
| [12-governance-and-v1-boundaries.md](12-governance-and-v1-boundaries.md) | v1 scope, non-goals, human control points, edge-case tests |
| [13-implementation-decisions.md](13-implementation-decisions.md) | Blocking implementation decisions for request/routing/publication |
| [14-hld-runtime-shape-and-installation.md](14-hld-runtime-shape-and-installation.md) | Recommended runtime shape, deployment patterns, Mission Control integration |
| [15-tech-stack.md](15-tech-stack.md) | Concrete technology choices: Python/TS split, FastAPI, SQLAlchemy, event bus, LlamaIndex, Next.js |

## Reference

| File | What it covers |
|------|---------------|
| [reference/glossary.md](reference/glossary.md) | Definitions of all terms used across docs |
| [reference/canonical-statuses.md](reference/canonical-statuses.md) | Canonical task/US statuses and transition notes |
| [reference/canonical-events.md](reference/canonical-events.md) | Canonical event types and semantics |
| [reference/handoff-contract.md](reference/handoff-contract.md) | Required fields and semantics of a handoff |
| [reference/artifact-model.md](reference/artifact-model.md) | Artifact types, lifecycle, and usage |
| [reference/agent-roles.md](reference/agent-roles.md) | Agent definitions, ownership, and scope |
