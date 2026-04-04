# Agent Runtime — Vision, Thesis, and Build Principles

## Short Name

- **Canonical name:** Agent Runtime
- **Plain-English descriptor:** a lightweight control plane for developer agents
- **Technical descriptor:** an event-driven, workflow-first multi-agent runtime

This is a better description than just “orchestrator” or “agent framework”.
It does more than route messages, but it is also much narrower and lighter than a general-purpose framework.

---

## What We Are Building

We are building a system shaped tightly around our own workflow and standards.

At the highest level, we are building:

- a runtime for **distinct agents** with clear responsibilities,
- a control plane for **developer-focused agent work**,
- an architecture that treats **A2A communication, recovery, and observability** as core product features,
- a system where **Mission Control** becomes an integral part of the development workflow,
- and a platform where agents can **remember, improve, and operate reliably over time**.

This is **not** meant to be:

- a universal chatbot platform,
- a generic marketplace of agents,
- a heavy enterprise BPM suite,
- a “one giant session with many personas hidden in prompts”,
- or a clever demo that works only on the happy path.

---

## Core Thesis

We want something that is:

- **simple**,
- **lightweight**,
- **practical**,
- **inspectable**,
- and above all **working in the real world**.

The design bias is deliberate:

- **reliability over cleverness**,
- **explicit ownership over hidden magic**,
- **events over transcript inference**,
- **recovery over wishful thinking**,
- **operator clarity over abstraction theatre**.

If a design is elegant on paper but hard to debug at 2 a.m., it is the wrong design.

---

## Primary Use Case

The first serious use case is **developer agents doing real delivery work**.

Target team shape:

- **James** — strategic owner, user interaction, delegation, final accountability
- **Naomi** — implementation and development execution
- **Amos** — review, QA, verification, quality escalation
- **Alex** — research, synthesis, option analysis

This means the runtime is optimized for flows such as:

- research,
- implementation,
- code review,
- verification,
- escalation,
- and final response to the human.

The human stays in control. Agents do real work, but they do it inside a system with ownership, callbacks, memory, and recovery.

---

## Mission Control Is Integral, Not Optional

Mission Control is not a side tool.
It is the first serious domain workflow layer inside the runtime.
It must be reachable both through **API** and **CLI**.
In practice, agents will often prefer the CLI for structured operational work, while UI and integrations will often prefer the API.

Mission Control should be the source of truth for the **development workflow state**, including:

- user stories,
- tasks,
- review loops,
- verify loops,
- status transitions,
- and escalation thresholds.

The Agent Runtime should remain responsible for:

- request ingress,
- ownership and delegation,
- A2A handoffs,
- callback routing,
- reply publication state,
- event history,
- per-agent memory,
- vectorization and retrieval infrastructure,
- observability and recovery.

Short version:

- **Mission Control owns dev workflow state**
- **Agent Runtime owns agent coordination and runtime semantics**

Together, they form one coherent system.

The runtime also needs a real **Web UI host**.
This is not optional.
We need a management/admin/configuration surface, but it must stay simple and operationally light.

---

## A2A Is a Priority, Not a Nice-to-Have

Agent-to-agent communication must be treated as a serious operational system.
Not as free-form chat. Not as “hope the other agent saw it”.

The core primitives are:

- **commands** — intent to do something (may be rejected; rejection emits a Domain Event)
- **events** — immutable Domain Event facts; cannot be undone
- **statuses** — canonical state snapshot
- **artifacts** — produced work results

Every non-trivial handoff should carry explicit structure such as:

- owner,
- requester,
- goal,
- definition of done,
- callback target,
- priority,
- execution mode,
- request link when applicable.

A handoff is **not complete** when it is sent.
It is complete only when it is **accepted** or **rejected**.

That one rule kills a lot of fake reliability.

---

## Event-Driven by Default

The system is built around Domain Events.
Domain Events are the nervous system of the runtime.

We want Domain Events for:

- request ingress,
- normalization,
- handoff dispatch and acceptance,
- task lifecycle,
- callback delivery,
- reply publication,
- memory writes,
- retries,
- timeouts,
- reconciliation,
- escalation,
- and audit.

Every operation — including fire-and-forget messages, adapter notifications, watchdog pings,
memory writes, and internal state transitions — emits a Domain Event. There are no silent
operations. If it happened, there is an event for it.

Why this matters:

- events make retries tractable,
- events make watchdogs possible,
- events make replay possible,
- events make debugging possible,
- events make cross-agent reasoning visible,
- events let us recover from failure without reading transcript soup.

If the system cannot explain what happened from durable records, it is not ready.

---

## We Design for Failure, Not for Demos

LLMs are flaky.
Runtimes crash.
Networks fail.
Callbacks go missing.
Adapters restart.
Messages duplicate.
Publication may fail after execution succeeds.

So the system must assume failure as normal.

We want first-class support for:

- retries,
- deduplication,
- watchdogs,
- execution timeouts,
- workflow timeouts,
- callback recovery,
- reconciliation,
- fallback paths,
- escalation,
- and replay.

A core invariant:

> **Task success, callback success, and human-visible reply success are separate concerns.**

“Done” does not automatically mean “the user got the answer”.

---

## Ownership Must Stay Explicit

We do not want invisible ownership derived from chat history.

We want explicit separation between:

- **strategic owner** — who owns the request as a whole,
- **execution owner** — who owns the delegated work,
- **callback target** — where operational results return,
- **reply target** — where the human-visible answer should be published.

For surface-originated durable work, the topology should stay strict:

- inbound through a surface/channel session,
- durable coordination through the owner’s `main`,
- specialist delegation `main-to-main`,
- human-visible reply through stored reply-target metadata.

That keeps ownership coherent across WhatsApp, Discord, web, and future surfaces.

---

## Memory and Controlled Self-Improvement

Each agent should have its own memory.
Memory is part of the system’s leverage, but it must stay disciplined.

We also want vectorization on multiple levels:

- **project-level codebase vectorization** for every managed repository,
- **project knowledge/document retrieval**,
- **agent memory retrieval**,
- and separate **session/transcript search** for replay and debugging.

We want layered memory:

- working memory,
- episodic memory,
- semantic memory,
- procedural memory.

We also want a **controlled self-improvement loop**:

- agents learn from outcomes,
- agents propose better procedures or heuristics,
- changes are reviewed,
- validated improvements are promoted,
- everything stays auditable and reversible.

Important constraint:

- memory is **not** workflow state,
- memory is **not** reply-routing truth,
- memory is **not** a substitute for proper runtime records.

No uncontrolled self-rewriting magic. No “the model probably remembers”.

Important retrieval principle:
- vectors are an index, not the source of truth,
- code retrieval needs structure, symbols, and exact search in addition to embeddings,
- and memory should be curated, typed, and inspectable.

---

## Simplicity Rules

Our system should prefer a small number of strong primitives over a large number of vague features.

Practical design rules:

- keep surface adapters thin,
- keep ownership explicit,
- keep callback contracts explicit,
- keep reply routing explicit,
- keep Mission Control as the dev workflow authority,
- keep both CLI and API as first-class interfaces,
- keep the Web UI as a built-in management surface,
- keep durable records queryable,
- keep recovery paths boring and predictable,
- keep agent memory separate from operational truth,
- keep retrieval/indexing inspectable and repairable,
- keep runtime concepts understandable to humans operating the system.

If a feature creates complexity without making reliability, recovery, or leverage better, it should probably not exist.

---

## Non-Goals for v1

v1 is not trying to solve everything.

It is **not**:

- a multi-tenant platform,
- an agent marketplace,
- a broad no-code workflow builder,
- a universal protocol compatibility layer,
- a full enterprise automation suite,
- or an autonomous self-governing agent society.

v1 is about getting the core right:

- distinct agents,
- serious A2A,
- reliable execution handoffs,
- Mission Control integration,
- durable memory,
- codebase vectorization and retrieval,
- clear observability,
- and graceful failure handling.

---

## What Good Looks Like

We are done when the system can support real developer work and still stay understandable.

That means:

- we always know who owns the work,
- we can always see what happened,
- we can recover from partial failure,
- we can trust retries and dedup,
- Mission Control and the runtime do not fight over state,
- agents improve over time without becoming chaotic,
- adding a new surface does not create a new ownership model,
- and operators do not need transcript archaeology to debug a broken run.

This should feel less like a flashy agent demo and more like a dependable operating system for agent work.

---

## Build Priorities

In order:

1. **Reliable A2A and ownership semantics**
2. **Event model, callbacks, retries, and watchdogs**
3. **Mission Control integration as first-class dev workflow, via both CLI and API**
4. **Built-in Web UI host for management, administration, and configuration**
5. **Per-agent memory plus project/codebase vectorization and retrieval**
6. **Observability, audit, and replay**
7. **Additional surfaces, tooling, and optimizations**

If priority 6 harms priority 1, 2, or 3, we are doing it backwards.

---

## One-Sentence Definition

**Agent Runtime is a lightweight, event-driven control plane for developer agents: it coordinates distinct agents, makes A2A reliable, uses Mission Control as the development workflow engine through both CLI and API, includes a built-in Web UI host, and treats memory, vectorization, callbacks, and recovery as first-class concerns.**
