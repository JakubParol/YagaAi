# 01 — System Overview

## What We Are Building and Why

We are building an opinionated multi-agent runtime: a workflow-first control plane
for agent work that is more predictable, operationally lighter, and better aligned
with owner-first work than today's heavy agent frameworks.

The problem is not that there are no agents on the market. The problem is that existing
systems are too heavy, too opaque, and too poorly shaped for durable agents, reliable
handoffs, disciplined memory, and strong observability.

This system should be closer to a **distributed workflow engine for agents** than to
a general-purpose agent framework.

## Target Workload

The system is designed for:
- owner-first work with durable agent identities
- asynchronous tasks with callbacks
- multi-agent handoffs across orchestration, execution, review, and research
- workflows that require auditability, replay, recovery, and memory continuity

It is not designed as:
- a universal chatbot
- an agent marketplace
- a full enterprise BPM suite
- a system built for multi-tenancy and broad product-market distribution (v1)

## Main Agents and Roles

Four agents collaborate on development and research:

| Agent | Role | Primary responsibility |
|-------|------|----------------------|
| **James** | Main agent | User interaction, continuity, delegation, coordination |
| **Naomi** | Senior developer | Implementation, dev memory, self-improvement |
| **Amos** | Senior QA | Review, verify, quality escalation |
| **Alex** | Senior researcher | Research, synthesis, return to James |

The standard interaction pattern is:

```
user → James → specialist agent → callback → James → user
```

James owns the strategic conversation and final outcome toward the user.
Each specialist owns their domain: Alex owns research tasks, Naomi owns implementation
tasks, Amos owns quality and review.

## Owner-First Model

Every task has an explicit owner. Ownership is not inferred from chat context.

An agent is the durable owner of decisions, memory, and responsibility within their domain.
The runtime (Claude Code, Codex, ACP, or similar) is an execution tool subordinate to
that owner.

This means:
- ownership survives session boundaries
- accountability is traceable end-to-end
- delegation is explicit, not implicit from conversation flow
- the operator can always answer: who owns this, what is its status, where should the result return

## Architectural Thesis

The core value comes from combining:
- separated agents with their own memory and responsibility
- simple and reliable agent-to-agent communication
- event-centric orchestration
- controlled self-improvement
- boringly reliable task relay
- strong operator UX

## System Boundary

The runtime is responsible for:
- routing commands and events
- task lifecycle
- ownership and callback handling
- per-agent memory
- audit, replay, and debugging
- controlled improvement loops
- workflow state for the most important flows

The runtime does not try to be (at start):
- a full enterprise scheduler
- an integration marketplace
- a complete IDE host
- an autonomous system that rebuilds agent topology on its own
- a general framework for everything
