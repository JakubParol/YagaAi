# 01 — System Overview

## What We Are Building and Why

We are building an opinionated multi-agent runtime: a workflow-first control plane
for agent work that is more predictable, operationally lighter, and better aligned
with owner-first work than heavy agent frameworks.

The system is closer to a **distributed workflow engine for agents** than to a
general-purpose agent framework.

## Target Workload

The system is designed for:
- owner-first work with durable agent identities
- user-originated requests that may arrive through multiple surfaces
- asynchronous tasks with explicit callbacks
- multi-agent handoffs across orchestration, execution, review, and research
- workflows that require auditability, replay, recovery, and memory continuity
- project/codebase vectorization and retrieval
- operation through both CLI and API

It is not designed as:
- a universal chatbot
- an agent marketplace
- a full enterprise BPM suite
- a system built for multi-tenancy and broad product-market distribution (v1)

## Main Agents and Roles

Four agents collaborate on development and research:

| Agent | Role | Primary responsibility |
|-------|------|----------------------|
| **James** | Main / strategic owner | User interaction, continuity, delegation, coordination |
| **Naomi** | Senior developer | Implementation, dev memory, self-improvement |
| **Amos** | Senior QA | Review, verify, quality escalation |
| **Alex** | Senior researcher | Research, synthesis, return to James |

## Surface Ingress Path vs Durable Coordination Path

The old compressed model:

```text
user → James → specialist → callback → James → user
```

is directionally useful but incomplete.

The actual v1 baseline for durable user-originated work is:

```text
surface session → owner main
owner main → specialist main → owner main → publish-capable surface
```

### Practical meaning

- surface/channel sessions are ingress/egress adapters
- durable coordination happens through the owning agent’s `main` endpoint
- specialist delegation is owner-to-owner (`main` to `main`)
- final human-visible replies are routed via stored reply-target metadata

## Owner-First Model

Every important unit of work has an explicit owner.
Ownership is not inferred from chat context.

The runtime keeps these concerns separate:
- **strategic owner** — accountable for the request as a whole
- **execution owner** — accountable for delegated work
- **callback target** — where execution results return
- **reply target** — where the human-visible reply should be published

This means:
- ownership survives session boundaries
- accountability is traceable end to end
- delegation is explicit, not implicit from conversation flow
- channel transcripts are not the recovery mechanism

## Architectural Thesis

The core value comes from combining:
- separated agents with their own memory and responsibility
- explicit request routing and reply publication state
- simple and reliable agent-to-agent communication
- event-centric orchestration
- controlled self-improvement
- project-aware retrieval and vectorization
- boringly reliable task relay
- strong operator UX across Web UI, CLI, and API

## System Boundary

The runtime is responsible for:
- receiving surface-originated requests
- normalizing durable work into owner-facing coordination endpoints
- routing commands and events
- task lifecycle
- ownership and callback handling
- explicit reply-target and publication state
- per-agent memory
- project/code/document vectorization and retrieval
- audit, replay, and debugging
- controlled improvement loops
- integrating with planning/control-plane systems such as Mission Control when present
- built-in Web UI host plus CLI/API operational surfaces

The runtime does not try to be (at start):
- a full enterprise scheduler
- an integration marketplace
- a complete IDE host
- an autonomous system that rebuilds topology on its own
- a general framework for everything

## Mental Model to Preserve

For durable work, the right mental model is:

```text
human message arrives on a surface
  → request becomes durable
  → owner main coordinates
  → specialists execute
  → execution callback returns to owner
  → owner decides response
  → surface publishes response
```

This is the baseline that the rest of the docs now formalize.
