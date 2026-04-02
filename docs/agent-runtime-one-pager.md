# Agent Runtime — One Pager

## Goal
Build our own opinionated multi-agent runtime that is more predictable, lighter operationally, and better aligned with our workflow than today’s heavy agent frameworks.

This is not meant to be “a chatbot with tools” or a copy of OpenClaw. It is meant to be a workflow-first runtime and control plane for agent work: separated entities with their own memory, explicit ownership, and predictable handoffs.

## Problem We Are Solving
Current agent frameworks are powerful, but they are often:
- too heavy,
- too magical,
- too operationally unpredictable,
- too weak at owner-first relay and handoffs,
- too undisciplined around memory and observability.

The problem is not: **“there are no agents on the market.”**
It is closer to:
**“there is no system whose operational shape really fits our way of working.”**

## Who It Is For / What Workload It Targets
The system is designed for:
- owner-first work with durable agent identities,
- longer asynchronous tasks with callbacks,
- multi-agent handoffs between roles like orchestrator / builder / reviewer / researcher,
- workflows that require auditability, replay, memory continuity, and recovery,
- operational work where reliability and observability matter more than demo effect.

The system is not designed as:
- a universal chatbot for everything,
- an agent marketplace,
- a full enterprise BPM suite,
- a system designed from v1 for multi-tenancy and broad product-market distribution.

## Main Use Case
The primary use case is concrete: several separated agents collaborate on development and research, with one main agent that talks to the user and delegates work further.

Target setup:
- **James** — the main agent, Chief Strategy Officer; talks to the user, remembers what we are doing and what we have done, delegates work, and keeps the whole picture together
- **Naomi** — senior developer; takes implementation work, builds memory around her work, and develops her own self-improvement loop
- **Amos** — senior QA; handles code review, verify, and quality escalations
- **Alex** — senior researcher; takes research work, synthesizes findings, and returns them to James

This means the system should be designed primarily around an owner-first multi-agent workflow, not around a single universal assistant.

## Main Architectural Thesis
The biggest value does not come from a single model or from the number of features. It comes from combining:
- separated agents with their own memory and responsibility,
- simple and reliable A2A,
- event-centric orchestration,
- a controlled self-improvement loop,
- boringly reliable task relay,
- and strong operator UX.

This should be closer to a **distributed workflow engine for agents** than to a general-purpose agent framework.

## System Boundary
This is a runtime / control plane for agent work, not a full “agent OS for everything.”

At the start, the system is responsible for:
- routing commands and events,
- task lifecycle,
- ownership and callback handling,
- per-agent memory,
- audit / replay / debugging,
- controlled improvement loop,
- workflow state for the most important flows.

At the start, the system does **not** try to be:
- a full enterprise scheduler,
- an integration marketplace,
- a complete IDE host,
- an autonomous system that rebuilds agent topology on its own,
- a general framework for everything.

## Core Model
### 1. Real Multi-Agent Environment
This should be an environment of cooperating operational entities, not one agent with multiple personas hidden in prompts.

Important rule: **an execution runtime is not the same thing as an agent**.
The agent owns decisions, memory, and responsibility.
An execution runtime — for example Claude Code, Codex, or ACP — is a tool the agent uses to get work done.

If a worker or executor exists, it should be treated as an execution-level subordinate entity of the owner, not as an independent domain owner.

Core system entities:
- **agent** — a durable entity with role, memory, and responsibility
- **session** — the current execution or conversation context
- **task** — a concrete unit of work
- **flow** — a broader progression spanning multiple tasks, events, and handoffs
- **handoff** — the act of transferring work and execution responsibility
- **memory** — persisted agent context
- **artifact** — a work result that can be passed further

In the Mission Control context, we also need to distinguish:
- **work item / US** — a domain work object in Mission Control
- **task** — an execution unit attached to a work item or flow
- **handoff** — work transfer between owners or executors
- **flow** — a progression spanning multiple steps, statuses, and decisions

### 2. Agent Separation Is First-Class
Each agent must have separated:
- context,
- memory,
- task ownership,
- event history,
- tool and permission scope wherever that affects safety or predictability.

The goal of separation is:
- reducing chaos,
- improving auditability,
- making ownership legible,
- making debugging easier.

The trade-off is explicit: more separation gives more control, but increases coordination, synchronization, and conflict-resolution cost.

### 3. Minimal Runtime and Communication Model
The minimal model should stay simple:
- the agent is the durable owner of role, memory, and responsibility,
- the session is the current execution or conversation context,
- the task is the basic unit of work and has an explicit status,
- the flow ties together multiple tasks, events, and handoffs,
- memory is scoped to the agent,
- artifacts are durable work outputs.

A2A communication should not be modeled primarily as free-form chat.
The core contract is:
- **commands** — an intent to perform an action,
- **events** — the fact that something happened,
- **statuses** — a canonical snapshot of task or work-item state,
- **artifacts** — a result or reference to a result.

Simple usage rules:
- **commands** are used to assign work to a specific owner or executor
- **events** describe facts that already happened and may matter to multiple consumers
- **request-response** is used for direct questions and answers when modeling everything as events makes no sense
- **artifacts** are durable work outputs, not just another message type

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

A handoff does not end at dispatch. It must be explicitly:
- accepted,
- rejected,
- or claimed,
with a concrete status and reason.

## Ownership and Accountability
Every task and every flow should explicitly store:
- owner,
- requester,
- optional executor / worker,
- callback target,
- status,
- related events and artifacts.

Ownership must not be inferred from chat context.

In practice:
- **James** owns the strategic conversation, delegation, and the final outcome toward the user
- **Alex** owns research tasks
- **Naomi** owns implementation tasks and the execution plan in the dev flow
- **Amos** owns quality, review, and verify

This creates a deliberate split between:
- **final accountability** — James toward the user
- **execution ownership** — the specialist inside their domain

## Execution Model
At the start, the system supports two main modes:
- **session-bound / sync-ish** — short interactions that need quick ACK or short answers
- **detached / async durable** — background tasks with callback, retry, and a full event trail

Detached runs are first-class. Best-effort fire-and-forget without an explicit callback contract should not be the default for important work.

## Memory Model
Memory should be layered and per-agent.

Minimal split:
- **working memory** — the current operational context needed right now
- **episodic memory** — the history of completed tasks and their outcomes
- **semantic / long-term memory** — durable knowledge, decisions, preferences, and patterns
- **procedural memory / skills** — validated ways of operating
- **event history** — an execution log, which is not the same thing as memory

Memory should not be just RAG glued onto context. It should be part of the agent’s identity and operating quality.

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
The system must be end-to-end inspectable.

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

Source of truth in the system must be explicit:
- **status and ownership** — one workflow-state layer backed by tasks and work items
- **history and facts** — event history
- **durable knowledge** — memory
- **work result** — artifacts

Memory must never be the source of truth for operational state.

## Mission Control as the First Domain Implementation
Mission Control is a first-class operational layer on top of the generic task/flow model.

The core runtime defines universal primitives:
- agent,
- session,
- task,
- flow,
- status,
- memory,
- event,
- artifact.

Mission Control is the first privileged domain implementation of that model for development workflow.

That means:
- user story,
- task,
- review,
- verify,
are not concepts outside the architecture, but domain specializations of the generic `task / flow / status / artifact / ownership` model.

Mission Control should be the source of truth for workflow state in the dev flow. It is not the domain owner instead of agents, but it may act as the active orchestrator / state machine for status transitions and process rules.

## Main Operational Flows
### 1. Research Flow
1. The user asks James for research.
2. James delegates the research to Alex.
3. Alex performs the research, records that he did it, stores relevant findings in his memory, and produces a result artifact.
4. Alex returns the result to James.
5. James reviews it and may ask for clarification.
6. James returns a final answer to the user.

### 2. Implementation Flow
1. The user asks James for a development task.
2. James delegates the work to Naomi.
3. Naomi performs the work using an appropriate coding runtime, such as Claude Code or Codex, likely through ACP over time.
4. Naomi records the execution trail, builds memory around her specialization, and returns the result to James.
5. James decides whether the result is ready for the next step or whether it needs refinement or a return trip.

### 3. QA Flow
1. James or the system flow passes the result to Amos.
2. Amos performs review or verify.
3. Amos records comments, outcome, and status.
4. If needed, he sends the work back to Naomi.
5. If the issue does not converge, it is escalated to James.

## Development Flow Through Mission Control
James can assign Naomi a user story or another work item.

Target flow:
1. James assigns a **US** to Naomi.
2. Naomi takes ownership of the US and sets it to **In Progress**.
3. Naomi analyzes the user story.
4. Naomi creates a plan and stores it as tasks under the US.
5. Each task has its own flow and status: **In Progress / Done / Blocked**.
6. Naomi works through the tasks until they are completed or blocked.
7. When all tasks are complete, Naomi moves the US to **Code Review** and assigns Amos.
8. James is notified.

A minimal task or handoff lifecycle should be explicit, for example:
**Created -> Accepted -> In Progress -> Review -> Verify -> Done / Blocked / Escalated / Cancelled**

We also need to define explicitly:
- which roles may perform which status transitions,
- which transitions are automatic,
- which transitions require explicit acceptance.

### Code Review Loop
1. Amos performs code review.
2. If there are comments, he adds them (for example as git comments), moves the US back to **In Progress**, and reassigns Naomi.
3. Naomi fixes the issues, updates the state, and sends it back to review.
4. There are at most **3 Code Review loops**.
5. If the issue is still not closed after 3 loops, it escalates to James.

In practice, this limit means a quality, scope, or ownership deadlock — not just a raw counter.

### Verify Loop
1. If Code Review passes, the US moves to **Verify** and is assigned to Amos.
2. Amos performs verify.
3. If he finds a problem, he records comments in the US, moves the work item back to **In Progress**, and reassigns Naomi.
4. Naomi fixes the issue and returns it to the appropriate step.
5. The flow continues until **Done**, **Blocked**, or **Escalated**.

This means work items, tasks, review loops, verify loops, and escalations are not UI details — they are one of the main reasons the system exists.

## Failure Modes and Recovery
The system must be designed for more than the happy path.

At minimum it must handle:
- missing callback or reply,
- duplicate event,
- out-of-order delivery,
- worker crash in the middle of a task,
- incomplete artifact,
- ownership or status conflict,
- accepted task with no progress for too long,
- orphaned work after the execution runtime ends or disappears,
- partial tool failure,
- side effects without confirmation.

For each such case there must be:
- a recovery owner,
- a default action: retry / reassign / escalate / mark blocked,
- an explicit terminal state or compensation path.

We also need to distinguish between:
- **execution timeout** — a problem at the runtime or worker level
- **workflow / SLA timeout** — lack of expected progress in the process

This means idempotency, deduplication, retry, semantic timeouts, and replay are not UX extras. They are part of the architectural core.

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
This does not sound like “building our own bot.” It sounds like building a work system for separated agents with local memory, explicit ownership, and controlled learning.

If we build it, success will not be measured by feature count. It will be measured by whether:
- handoffs are predictable,
- ownership is explicit,
- each agent has its own memory and history,
- the whole thing is operationally simpler than existing frameworks,
- and the operator can quickly answer: who owns this, what happened, where did the task get stuck, and where should the result return.
