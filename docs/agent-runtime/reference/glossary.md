# Glossary

**Agent**  
A durable operational entity with a stable identity, its own memory, a defined scope
of responsibility, and ownership of assigned tasks. An agent persists across sessions.
See [02-core-model.md](../02-core-model.md).

**Artifact**  
A work result produced by a task, passed between agents or stored for audit. Artifacts
are durable and versioned. They are not the source of truth for request routing or
reply-publication state. See [artifact-model.md](artifact-model.md).

**Callback**  
An explicit return of a result to the requester or callback target after a task completes.
Callbacks are mandatory for detached tasks. Callback success is not the same thing as
human reply publication success.

**Causation ID**  
An identifier on an event that points to the event that caused it. Used to reconstruct
causal chains. See [09-observability-and-audit.md](../09-observability-and-audit.md).

**Channel Session**  
A session bound to a transport surface or surface context (for example WhatsApp,
Discord, or web chat). It is an ingress/egress adapter, not the durable owner of
important work.

**Command**  
A message expressing intent to perform an action. One of the A2A primitive types.
See [03-runtime-and-a2a.md](../03-runtime-and-a2a.md).

**Correlation ID**  
An identifier that groups all events belonging to one logical execution lineage.
Distinct from `request_id` in v1.

**Dedup Key**  
An identifier on a message that enables idempotent processing. Delivering the same
message twice with the same key has the same effect as delivering it once.

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
See [canonical-events.md](canonical-events.md).

**Event History**  
The append-only log of all events. Source of truth for what happened. Not the same as memory.

**Execution Owner**  
The specialist agent currently accountable for delegated execution work.
This is different from the strategic owner of the request as a whole.

**Execution Timeout**  
A timeout at the runtime or worker level: the execution runtime has not responded
within the expected window. See [08-failure-recovery-and-timeouts.md](../08-failure-recovery-and-timeouts.md).

**Final Accountability**  
The responsibility James holds toward the user for the ultimate outcome, regardless
of which specialist performed the work.

**Flow**  
A progression spanning multiple tasks, events, and handoffs with a defined goal and
terminal state. A flow may exist with or without a user-originated request.
See [02-core-model.md](../02-core-model.md).

**Handoff**  
A transfer of work and execution responsibility from one agent to another. Not complete
until explicitly accepted or rejected. See [handoff-contract.md](handoff-contract.md).

**Idempotency**  
The property that processing the same message more than once produces the same outcome
as processing it once.

**Main Session Key**  
The canonical owner-facing coordination endpoint for an agent, for example `agent:main:main`
or `agent:naomi:main`. The durable owner remains the agent, not the session key.

**Memory**  
The persisted context of an agent, layered into working, episodic, semantic, and
procedural. Not the source of truth for operational state. See [05-memory-model.md](../05-memory-model.md).

**Mission Control (MC)**  
The first domain implementation of the Agent Runtime, specialized for the development
workflow. Source of truth for US and task state in the dev flow. MC does not own request
routing or reply-publication truth. See [06-mission-control-model.md](../06-mission-control-model.md).

**Normalization Acceptance**  
Acceptance of a surface-originated request into the owner-facing durable path. This is
not the same as specialist handoff acceptance.

**Owner-Facing Coordination Endpoint**  
The agent’s canonical `main` session key used for durable coordination, callbacks, and
cross-agent routing.

**Procedural Memory / Skills**  
The layer of agent memory that holds validated ways of operating and effective patterns.
See [05-memory-model.md](../05-memory-model.md).

**Publish Dedup Key**  
Idempotency key for one human-visible publication intent. Reused across safe mechanical
retry of the same reply intent.

**Reply Publication**  
The human-visible publish step to a surface or delivery endpoint. Distinct from task
completion and callback success.

**Reply Session Key**  
One concrete current publish-capable endpoint that may satisfy a reply target. Advisory /
read-only when carried in handoffs.

**Reply Target**  
The durable human reply destination concept stored on the request record. Broader than a
literal session key.

**Request**  
The durable record for a user-originated unit of work. It carries request identity,
routing metadata, callback metadata, reply-target metadata, and publication state.
It does not replace task, flow, handoff, event, or artifact.

**Request Class**  
Classification of a request as `session-bound` or `durable`.

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
A canonical snapshot of the current state of a task or work item. Request/publication
projection labels are not canonical task statuses. See [canonical-statuses.md](canonical-statuses.md).

**Strategic Owner**  
The agent accountable for the request as a whole and for the final human-facing outcome.
For James-routed user work, this is typically James.

**Surface Adapter**  
The runtime component bound to a surface/channel session that receives inbound messages
and performs concrete publish operations. Thin by design.

**Surface Session**  
A presentation-capable session that can publish back to the human on the original
transport surface.

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