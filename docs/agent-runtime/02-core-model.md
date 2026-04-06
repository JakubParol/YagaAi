# 02 — Core Model

## Entity Overview

| Entity | Meaning | Durable? | Owner | Source of Truth |
|--------|---------|----------|-------|----------------|
| **agent** | Durable role with memory and responsibility | Yes | itself | agent record |
| **session** | Current execution or conversation context | No (execution-scoped) | agent | event history |
| **request** | User-originated request record with routing and publication state | Yes | strategic owner agent | request store |
| **task** | Concrete unit of work | Yes | assigned agent | task store |
| **flow** | Progression spanning tasks, events, and handoffs | Yes | orchestrating agent / MC | task store / MC |
| **handoff** | Transfer of work and execution responsibility | Yes | requester until accepted | task store |
| **event** | Fact that something happened | Yes (immutable) | runtime / agent | event log |
| **artifact** | Work result passed further | Yes | producing agent | artifact store |
| **memory** | Persisted agent context | Yes | agent | memory store |
| **project index** | Durable retrieval/index state for one managed project | Yes | runtime | project index store |
| **work item / US** | Domain work object in Mission Control | Yes | assigned agent | Mission Control |

## Event Storming Model

The system maps to Event Storming vocabulary as follows:

**Aggregates** (validate Commands, emit Domain Events):

```
Agent | Request | Task | Handoff | Flow
```

**Bounded Contexts:**

```
Agent Runtime   — owns: request routing, A2A, callbacks, events, memory, indexing
Mission Control — owns: dev workflow state (US, tasks, review/verify loops)
```

**External Systems** (relative to the Agent Runtime Bounded Context):

```
Surface adapters: WhatsApp, Discord, web, CLI
```

**Fundamental invariant:**

```
Command → Aggregate validates → Domain Event emitted
```

No state change occurs without a Domain Event. A rejected Command produces a
`command.rejected` Domain Event. There are no silent operations.

See [reference/glossary.md](reference/glossary.md) for definitions of Aggregate,
Bounded Context, Domain Event, Policy, Read Model, and External System.

---

## Entity Definitions

### Agent

An agent is a durable operational entity with:
- a stable identity and role
- its own memory (working, episodic, semantic, procedural)
- a defined scope of responsibility and tool access
- ownership of tasks assigned to it

An agent is not a session. It persists across sessions, retains memory, and accumulates
knowledge and history. Multiple sessions may be associated with one agent over time.

An agent must not be confused with its execution runtime. The agent decides; the runtime executes.

### Session

A session is the current active execution or conversation context for an agent. It is
execution-scoped and does not persist independently. Session state is reflected in the
event history.

For user-facing work, sessions come in two important shapes:
- **channel/surface sessions** — ingress/egress adapters bound to WhatsApp, Discord, web, etc.
- **`main` session keys** — owner-facing coordination endpoints for durable work

The durable owner remains the agent, not the session object.

**One-main invariant:** At any given time, an agent has exactly one `main` coordination
context regardless of how many channel or surface adapters are active. Channel sessions
(WhatsApp, Discord, web, etc.) are transport adapters that feed into this single `main`
coordination context. They are not separate agent sessions. Adding a new channel adds
a new adapter — it does not create a new agent session or a new coordination context.

### Request

A request is the durable record for a **user-originated** unit of work.

A request record carries:
- request identity (`request_id`)
- origin session/context metadata
- strategic owner metadata
- reply target metadata
- reply publication state
- links to task/flow execution state

**Important boundary (v1):**
- callback metadata is **not** stored as first-class fields on `request`
- callback contract and delivery status live on `task`/`handoff` paths
- `request` remains the source of truth for routing and human-visible publication state

A request is not a replacement for:
- task
- flow
- handoff
- event
- artifact

Instead:
- a request may create or reference tasks, flows, and handoffs
- a request may span multiple delegated tasks/handoffs
- a flow may exist with or without a request depending on origin
- scheduled/system/operator-originated flows do not necessarily begin with a request

The request record is the source of truth for request routing and human-visible publication
state. It is not a second workflow engine.

### Task

A task is a concrete unit of work:
- has an owner, requester, and optional executor
- has a canonical status (see [canonical-statuses.md](reference/canonical-statuses.md))
- has a callback target
- may produce one or more artifacts
- belongs to a flow or work item

Tasks are the primary unit of delegation and accountability in the system.

### Flow

A flow is a progression spanning multiple tasks, events, and handoffs. It models a
process that unfolds over time, involves multiple agents, and has a defined goal and
terminal state.

Examples: the implementation flow, the research flow, the code review loop.

A flow is not a chat thread. It is a structured process with defined participants,
transitions, and outcomes.

### Handoff

A handoff is a transfer of work and execution responsibility from one agent to another.

A handoff is not complete when dispatched. It is complete only when explicitly:
- **accepted** — the receiving agent takes ownership
- **rejected** — the receiving agent declines with a reason

Until one of these occurs, the handoff is pending and the original owner retains responsibility.

Every handoff must include a minimal contract (see [reference/handoff-contract.md](reference/handoff-contract.md)).

### Handoff vs Task

A handoff and a task are distinct objects with different lifecycles:

| Aspect | Handoff | Task |
|--------|---------|------|
| Purpose | Transfer of responsibility | Unit of work to be done |
| Lifecycle | dispatched → accepted / rejected | Created → Accepted → In Progress → Done / Blocked / Escalated |
| Created by | requester | requester (or MC for domain tasks) |
| Completed when | accepted or rejected | Done, Cancelled, or Escalated |
| Persists after completion | Yes (audit record) | Yes (permanent record) |

Accepting a handoff transitions the corresponding task to `Accepted`. If no task exists
yet at dispatch time, accepting the handoff creates the task. A task may exist without a
handoff (e.g., tasks created internally by MC under a US), but a handoff always
references or creates a task.

### Event

An event is an immutable fact that something happened. Events are the authoritative
execution trace. They are not memory — they are the append-only log from which memory
may be derived.

Events carry:
- a correlation ID (execution lineage)
- a causation ID (links an event to the event that caused it)
- a dedup key (for idempotent processing)
- `occurred_at`
- a type and payload
- a `schema_version`

For user-originated work, events also remain linked back to the request record.

### Artifact

An artifact is a work result that can be passed between agents. Artifacts are durable
and versioned. They are the primary means by which work products move through the system.

Examples: a research report, a code diff, a test result, a review comment set, a PR reference.

Artifacts are not the same as memory. An artifact is produced by a task; memory is
maintained by an agent.

### Memory

Memory is the persisted context of an agent. It is layered (see [07-memory-model-and-vectorization.md](07-memory-model-and-vectorization.md))
and per-agent. Memory informs future decisions; it is not the source of truth for
operational state.

Operational state (who owns what, what status a task is in, where a reply should be
published) does not live in memory.

### Project Index

A project index is the durable retrieval/index state for one managed project.
It exists to support:
- codebase semantic retrieval
- lexical retrieval
- symbol-aware navigation
- project document retrieval
- freshness/repair tracking

A project index is not the source of truth for the project’s code or workflow state.
It is a retrieval accelerator over canonical source material.

### Work Item / User Story

A work item is a domain-level concept in Mission Control. It is a specialization of
the generic `flow` concept for the development workflow.

A user story (US) is the primary work item type. It has its own lifecycle, owns a set
of tasks, and may move through statuses like In Progress, Code Review, Verify, Done,
Blocked, Escalated.

## Key Relations

### User-originated durable work

```text
user
  └─ sends message via → surface / channel session
                           └─ creates / updates → request record
                                                    └─ normalizes into → owner main
                                                                            └─ delegates via handoff → specialist main
                                                                                                           └─ executes via runtime
                                                                                                           └─ produces artifacts
                                                                                                           └─ emits events
                                                                                                           └─ callback → owner main
                                                                            └─ decides reply
                                                                            └─ instructs surface publish
                                                                                 └─ publish outcome → request record
```

### Development workflow

```text
request record
  └─ may create / reference → flow / US
                                └─ contains → tasks
                                └─ tracked by → Mission Control
                                └─ produces → artifacts
                                └─ returns callback → owner main
                                └─ final human reply tracked on → request record
```

## Agent vs Runtime

This distinction is critical:

| Aspect | Agent | Runtime |
|--------|-------|---------|
| Identity | Durable, persistent | Execution-scoped |
| Memory | Yes, layered | No |
| Responsibility | Owns tasks and outcomes | Executes instructions |
| Decision authority | Yes | No |
| Examples | James, Naomi, Amos, Alex | Claude Code, Codex, ACP |

A runtime is a tool the agent uses. If a worker or executor exists, it is subordinate
to the owner, not an independent domain owner.

## Agent, Owner Session, Worker Session, and Harness

These four layers must not be collapsed into each other.

| Layer | What it is | Examples |
|-------|-----------|---------|
| **Agent** | Durable operational owner with identity, memory, responsibility, and accountability | James, Naomi, Amos, Alex |
| **Owner session (`main`)** | The agent's canonical coordination endpoint for durable routing, acceptance, delegation, and callback handling | `agent:main:main`, `agent:naomi:main`, `agent:amos:main` |
| **Worker / sub session** | A temporary execution context created by an owning agent to perform bounded work on its behalf; not a durable owner | an implementation worker spawned by any owning agent (e.g. a dev worker spawned by the implementation agent; a review-analysis worker spawned by the QA agent) |
| **Harness / execution backend** | A tool or backend used by an owner session or worker session to perform execution; not an agent, task owner, or workflow owner | ACP, Claude Code, Codex, acpx |

### Invariant

> **Agent owns. `main` coordinates. Worker executes. Harness is a tool.**

A2A contracts operate between owning agents. Worker spawning and harness choice are
internal execution decisions of the receiving owner and sit below the A2A contract layer.

**Sub-session return invariant:** Results from any worker or sub-session always return
to the spawning agent's `main`. A worker does not report directly to other agents,
Mission Control, or channel adapters. The return path is strictly: worker →
spawning agent's `main`. There are no shortcuts to other agents or to the top of the
delegation chain. If agent A delegated to agent B, and B spawned a worker, the worker
reports to B's `main` — not to A.

All named agents in v1 (James, Naomi, Amos, Alex) have the same architectural standing.
Their differences are responsibility-domain differences, not architectural-species differences.
Harness choice does not redefine agent identity, task ownership, or workflow ownership.

## Source-of-Truth Rules

| What | Source of Truth |
|------|----------------|
| Request routing + publication state | Request store |
| Task status and execution ownership | Task store (Mission Control for dev flow) |
| Workflow state in dev flow | Mission Control |
| Execution history / chronology | Event log |
| Agent knowledge | Memory store |
| Project retrieval/index state | Project index store |
| Work results | Artifact store |

### Practical split

- **Request store** answers: who owns the request strategically, where should the human-visible reply go, was it published successfully?
- **Task / flow systems** answer: what work is currently in progress, who owns that execution work, what is the current task/US status?
- **Event log** answers: what happened, in what order, and why — the backbone from which watchdogs arm, Policies react, retries schedule, and recovery paths operate. Read Models (operator views, status projections) are derived from it.
- **Memory** answers: what should the agent remember for future work?
- **Project index store** answers: what retrieval/index state exists for code/docs, how fresh it is, and what retrieval artifacts are available

Memory must never be the source of truth for operational state.
Event history is the source of truth for what happened, not for what the current state is.
