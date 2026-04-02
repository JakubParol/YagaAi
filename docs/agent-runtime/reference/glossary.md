# Glossary

**Agent**
A durable operational entity with a stable identity, its own memory, a defined scope
of responsibility, and ownership of assigned tasks. An agent persists across sessions.
See [02-core-model.md](../02-core-model.md).

**Artifact**
A work result produced by a task, passed between agents or stored for audit. Examples:
research report, PR reference, test result, review comments. Artifacts are durable and
versioned. See [reference/artifact-model.md](artifact-model.md).

**Callback**
An explicit return of a result to the requester or callback target after a task completes.
Callbacks are mandatory for detached tasks. Not optional for important work.

**Causation ID**
An identifier on an event that points to the event that caused it. Used to reconstruct
causal chains. See [09-observability-and-audit.md](../09-observability-and-audit.md).

**Command**
A message expressing intent to perform an action. One of four A2A primitive types.
See [03-runtime-and-a2a.md](../03-runtime-and-a2a.md).

**Correlation ID**
An identifier that groups all events belonging to one logical flow or request.
See [09-observability-and-audit.md](../09-observability-and-audit.md).

**Dedup Key**
An identifier on a message that enables idempotent processing. Delivering the same
message twice with the same dedup key has the same effect as delivering it once.

**Definition of Done**
The explicit acceptance criteria for a task or handoff. Required in every handoff contract.

**Detached Execution**
An execution mode for background tasks with an explicit callback contract, retry semantics,
and a full event trail. The correct default for important work.

**Episodic Memory**
The layer of agent memory that holds the history of completed tasks and their outcomes.
See [05-memory-model.md](../05-memory-model.md).

**Escalation**
The transfer of a deadlocked or unresolvable situation to James. Triggered by loop limits,
ownership conflicts, or quality deadlocks. See [04-ownership-lifecycle-and-state.md](../04-ownership-lifecycle-and-state.md).

**Event**
An immutable fact that something happened. The authoritative execution trace.
One of four A2A primitive types. See [reference/canonical-events.md](canonical-events.md).

**Event History**
The append-only log of all events. Source of truth for what happened. Not the same
as memory.

**Execution Timeout**
A timeout at the runtime or worker level: the execution runtime has not responded
within the expected window. See [08-failure-recovery-and-timeouts.md](../08-failure-recovery-and-timeouts.md).

**Final Accountability**
The responsibility James holds toward the user for the ultimate outcome, regardless
of which specialist agent performed the work.

**Flow**
A progression spanning multiple tasks, events, and handoffs with a defined goal and
terminal state. See [02-core-model.md](../02-core-model.md).

**Handoff**
A transfer of work and execution responsibility from one agent to another. Not complete
until explicitly accepted, rejected, or claimed. See [reference/handoff-contract.md](handoff-contract.md).

**Idempotency**
The property that processing the same message more than once produces the same outcome
as processing it once.

**Memory**
The persisted context of an agent, layered into working, episodic, semantic, and
procedural. Not the source of truth for operational state.
See [05-memory-model.md](../05-memory-model.md).

**Mission Control (MC)**
The first domain implementation of the Agent Runtime, specialized for the development
workflow. Source of truth for US and task state in the dev flow.
See [06-mission-control-model.md](../06-mission-control-model.md).

**Procedural Memory / Skills**
The layer of agent memory that holds validated ways of operating and effective patterns.
See [05-memory-model.md](../05-memory-model.md).

**Runtime**
The execution tool used by an agent: Claude Code, Codex, ACP, or similar. Subordinate
to the agent. Not a durable identity.

**Semantic Memory**
The layer of agent memory that holds durable knowledge, decisions, preferences, and
domain patterns. See [05-memory-model.md](../05-memory-model.md).

**Session**
The current active execution or conversation context for an agent. Execution-scoped,
not persistent. See [02-core-model.md](../02-core-model.md).

**Session-Bound Execution**
An execution mode for short interactions needing quick acknowledgment. Result returned
within the same session context.

**Shared Facts**
A governed layer of cross-agent knowledge that agents may rely on by default, after
promotion. Requires explicit governance. See [05-memory-model.md](../05-memory-model.md).

**Status**
A canonical snapshot of the current state of a task or work item. One of four A2A
primitive types. See [reference/canonical-statuses.md](canonical-statuses.md).

**Task**
A concrete unit of work with an owner, requester, status, and callback target.
The primary unit of delegation and accountability. See [02-core-model.md](../02-core-model.md).

**User Story (US)**
The primary work item type in Mission Control. A domain-level specialization of `flow`
for the development workflow. See [06-mission-control-model.md](../06-mission-control-model.md).

**Verify**
A QA step performed by Amos after code review passes, confirming functional correctness
before a US is marked Done.

**Working Memory**
The layer of agent memory that holds the current operational context within a session.
May be promoted to episodic or semantic memory. See [05-memory-model.md](../05-memory-model.md).

**Workflow Timeout (SLA Timeout)**
A timeout at the task or flow level: expected progress has not occurred within a defined
business window. See [08-failure-recovery-and-timeouts.md](../08-failure-recovery-and-timeouts.md).
