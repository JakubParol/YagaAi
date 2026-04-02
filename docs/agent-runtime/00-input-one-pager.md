# Agent Runtime — One Pager

## What We Are Building and Why
We are building our own opinionated multi-agent runtime: a workflow-first control plane for agent work that is more predictable, operationally lighter, and better aligned with our workflow than today’s heavy agent frameworks.

The problem is not that there are no agents on the market. It is that existing systems are too heavy, too opaque, and too poorly shaped for owner-first work with durable agents, reliable handoffs, disciplined memory, and strong observability.

## Target Workload
The system is designed for:
- owner-first work with durable agent identities,
- asynchronous tasks with callbacks,
- multi-agent handoffs across orchestration, execution, review, and research,
- workflows that require auditability, replay, recovery, and memory continuity.

It is not designed as:
- a universal chatbot,
- an agent marketplace,
- a full enterprise BPM suite,
- a v1 system built for multi-tenancy and broad product-market distribution.

## Main Use Case
Several distinct agents collaborate on development and research, with one main agent that talks to the user and delegates work.

Target setup:
- **James** — main agent; user interaction, continuity, delegation, coordination
- **Naomi** — senior developer; implementation, dev memory, self-improvement
- **Amos** — senior QA; review, verify, quality escalation
- **Alex** — senior researcher; research, synthesis, return to James

## Architectural Thesis
The core value comes from combining:
- separated agents with their own memory and responsibility,
- simple and reliable A2A,
- event-centric orchestration,
- controlled self-improvement,
- boringly reliable task relay,
- strong operator UX.

This should be closer to a **distributed workflow engine for agents** than to a general-purpose agent framework.

## System Boundary
This is a runtime/control plane for agent work.

At the start, it is responsible for:
- routing commands and events,
- task lifecycle,
- ownership and callback handling,
- per-agent memory,
- audit/replay/debugging,
- controlled improvement loops,
- workflow state for the most important flows.

At the start, it does **not** try to be:
- a full enterprise scheduler,
- an integration marketplace,
- a complete IDE host,
- an autonomous system that rebuilds agent topology on its own,
- a general framework for everything.

## Core Model
### 1. Agents, Runtime, and Separation
This should be an environment of cooperating operational entities, not one agent with multiple personas hidden in prompts.

Important rule: **agent != execution runtime**.
The agent is the durable owner of decisions, memory, and responsibility. The runtime — for example Claude Code, Codex, or ACP — is an execution tool.

If a worker or executor exists, it is subordinate to the owner, not an independent domain owner.

Core entities:
- **agent** — durable role, memory, responsibility
- **session** — current execution or conversation context
- **task** — concrete unit of work
- **flow** — progression spanning tasks, events, and handoffs
- **handoff** — transfer of work and execution responsibility
- **memory** — persisted agent context
- **artifact** — work result passed further

Mission Control-specific distinctions:
- **work item / US** — domain work object in Mission Control
- **task** — execution unit attached to a work item or flow
- **handoff** — work transfer between owners or executors
- **flow** — progression spanning steps, statuses, and decisions

Each agent must have separated:
- context,
- memory,
- task ownership,
- event history,
- tool and permission scope where that affects safety or predictability.

The trade-off is explicit: more separation gives more control, but increases coordination, synchronization, and conflict-resolution cost.

### 2. Runtime and Communication Model
A2A should not be modeled primarily as free-form chat.
The core contract is:
- **commands** — intent to perform an action
- **events** — fact that something happened
- **statuses** — canonical snapshot of task or work-item state
- **artifacts** — result or reference to a result

A2A should be designed from day one with:
- idempotency,
- deduplication,
- correlation IDs,
- causation IDs,
- contract versioning.

Each handoff should include a minimal contract:
- owner
- requester
- goal
- definition of done
- input artifacts or input context
- callback target
- priority
- deadline or SLA, if it exists

A handoff does not end at dispatch. It is not complete until it is explicitly accepted, rejected, or claimed, with a concrete status and reason.

## Ownership and Accountability
Every task and flow should explicitly store:
- owner,
- requester,
- optional executor / worker,
- callback target,
- status,
- related events and artifacts.

Ownership must not be inferred from chat context.

In practice:
- **James** owns the strategic conversation, delegation, and final outcome toward the user
- **Alex** owns research tasks
- **Naomi** owns implementation tasks and the execution plan in the dev flow
- **Amos** owns quality, review, and verify

This creates a deliberate split between:
- **final accountability** — James toward the user
- **execution ownership** — the specialist within their domain

## Execution Model
At the start, the system supports two modes:
- **session-bound / short-turn synchronous** — short interactions that need quick ACK or short answers
- **detached / async durable** — background tasks with callback, retry, and full event trail

Detached runs are first-class. Best-effort fire-and-forget without an explicit callback contract should not be the default for important work.

## Memory Model
Memory should be layered and per-agent.

Minimal split:
- **working memory** — current operational context
- **episodic memory** — history of completed tasks and outcomes
- **semantic / long-term memory** — durable knowledge, decisions, preferences, and patterns
- **procedural memory / skills** — validated ways of operating
- **event history** — execution log, not the same thing as memory

Write and correction policy must stay selective:
- not every event belongs in long-term memory
- durable memory writes should be justified
- incorrect or outdated entries must be correctable or retractable
- event history remains the source of execution trace, but does not replace memory

If a shared-facts layer exists, it needs governance:
- who can propose facts,
- who can approve them,
- what lifecycle and versioning they have,
- when an agent may rely on them by default.

## Self-Improvement Loop
Self-improvement matters, but at the start it must not mean autonomous self-rewriting.

Minimal v1 version:
- the agent may update local working notes,
- the agent may propose improvements,
- the system stores an improvement candidate,
- the change goes to review,
- there is audit trail, versioning, and rollback.

We need to distinguish between:
- **local notes / working heuristics**
- **memory updates**
- **behavior changes** — prompts, procedures, routing heuristics, skill library
- **platform changes** — runtime policy, contracts, topology rules, memory governance

At the start, self-improvement should mainly target behavior, not platform.

## Observability, Auditability, and Source of Truth
The system must be inspectable end to end.

Minimum:
- structured events,
- correlation IDs,
- causation IDs,
- dedup keys,
- per-run timeline,
- tool call ledger,
- memory write ledger,
- prompt/context snapshot,
- policy/version lineage,
- replay/debug path.

Source of truth must be explicit:
- **status and ownership** — one workflow-state layer backed by tasks and work items
- **history and facts** — event history
- **durable knowledge** — memory
- **work result** — artifacts

Memory must never be the source of truth for operational state.

## Mission Control as the First Domain Implementation
Mission Control is a first-class operational layer on top of the generic task/flow model.

The core runtime defines universal primitives: agent, session, task, flow, status, memory, event, and artifact. Mission Control is the first privileged domain implementation of that model for the development workflow.

User stories, tasks, review, and verify are not architectural exceptions; they are domain-level specializations of the generic `task / flow / status / artifact / ownership` model.

Mission Control should be the source of truth for workflow state in the dev flow. It is not the domain owner instead of agents, but it may act as the active orchestrator/state machine for status transitions and process rules.

## Main Operational Flows
### Research
1. The user asks James for research.
2. James delegates it to Alex.
3. Alex performs the research, stores relevant findings in memory, and produces a result artifact.
4. Alex returns the result to James.
5. James reviews it and may ask for clarification.
6. James returns a final answer to the user.

### Implementation
1. The user asks James for a development task.
2. James delegates it to Naomi.
3. Naomi performs the work using an appropriate coding runtime, such as Claude Code or Codex, for example through ACP.
4. Naomi records the execution trail, strengthens memory around her specialization, and returns the result to James.
5. James decides whether the result is ready or needs another pass.

### QA
1. James or the system flow passes the result to Amos.
2. Amos performs review or verify.
3. Amos records comments, outcome, and status.
4. If needed, he sends the work back to Naomi.
5. If the issue does not converge, it escalates to James.

## Development Flow Through Mission Control
James can assign Naomi a user story or another work item.

Target flow:
1. James assigns a **US** to Naomi.
2. Naomi takes ownership of the US and sets it to **In Progress**.
3. Naomi analyzes the user story.
4. Naomi creates a plan and stores it as tasks under the US.
5. Each task has status: **In Progress / Done / Blocked**.
6. Naomi works through the tasks until they are completed or blocked.
7. When all tasks are complete, Naomi moves the US to **Code Review** and assigns Amos.
8. James is notified via an explicit callback or event.

A minimal task or handoff lifecycle should be explicit, for example:
**Created -> Accepted -> In Progress -> Review -> Verify -> Done / Blocked / Escalated / Cancelled**

We also need to define explicitly:
- which roles may perform which status transitions,
- which transitions are automatic,
- which transitions require explicit acceptance.

### Code Review Loop
1. Amos performs code review.
2. If there are comments, he adds them, moves the US back to **In Progress**, and reassigns Naomi.
3. Naomi fixes the issues and sends the work back to review.
4. There are at most **3 Code Review loops**.
5. If the issue is still not closed after 3 loops, it escalates to James.

In practice, this limit means a quality, scope, or ownership deadlock — not just a raw counter.

### Verify Loop
1. If Code Review passes, the US moves to **Verify** and is assigned to Amos.
2. Amos performs verify.
3. If he finds a problem, he records comments in the US, moves the work item back to **In Progress**, and reassigns Naomi.
4. Naomi fixes the issue and returns it to the appropriate step.
5. The flow continues until **Done**, **Blocked**, or **Escalated**.

Work items, tasks, review loops, verify loops, and escalations are not UI details. They are one of the main reasons the system exists.

## Failure Modes and Recovery
The system must be designed for more than the happy path.

At minimum it must handle:
- delivery issues such as missing callbacks, duplicate events, or out-of-order delivery,
- execution issues such as worker crashes, orphaned work, partial tool failures, or incomplete artifacts,
- state issues such as ownership conflicts, status conflicts, or accepted tasks with no progress,
- side effects completed without confirmation back to the workflow.

For each such case there must be:
- a recovery owner,
- a default action: retry / reassign / escalate / mark blocked,
- an explicit terminal state or compensation path.

We also need to distinguish between:
- **execution timeout** — a problem at the runtime or worker level
- **workflow / SLA timeout** — lack of expected progress in the process

This means idempotency, deduplication, retry, semantic timeouts, and replay are part of the architectural core.

## Human Control Points
A human must have explicit control points for:
- approving published changes,
- rolling back changes,
- overriding policy,
- incident review,
- promoting shared facts,
- approving platform-level changes.

## Non-Goals, v1 Scope, and Success Criteria
v1 is internal-first.

v1 primarily supports:
- 4 agents,
- 3 main flow types: research, development, and QA,
- a privileged development workflow in Mission Control.

v1 does not try to solve:
- broad onboarding,
- multi-tenancy,
- agent marketplaces,
- product-grade support,
- full capability parity with existing platforms,
- an autonomous self-modifying production loop,
- a full declarative workflow DSL when a simpler event/state contract is enough.

The system should not try to win on feature breadth at the start. It should win operationally.

At the v1 level, success means:
- handoffs between agents are predictable and visible end-to-end,
- for each task we can unambiguously identify owner, status, and callback target,
- an operator can replay a flow and understand what happened without digging through session chaos,
- per-agent memory improves future work without collapsing into an execution log,
- execution failures can be retried or escalated safely.

v1 should also pass contract-style edge-case tests for:
- duplicate event,
- lost callback,
- worker crash mid-task,
- review reassignment,
- stale ownership conflict,
- retry after partial artifact,
- replay after failure.

## MVP Success Metrics
- callback success rate,
- handoff completion rate,
- mean time to debug a failed run,
- duplicate-safe processing rate,
- share of tasks requiring manual recovery.

## Bottom Line
This is a work system for separated agents with local memory, explicit ownership, and controlled self-improvement.

Success will be measured by whether:
- handoffs are predictable,
- ownership is explicit,
- each agent has its own memory and history,
- the whole thing is operationally simpler than existing frameworks,
- and the operator can quickly answer: who owns this, what happened, where did the task get stuck, and where should the result return.
