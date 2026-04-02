# 09 — Observability and Audit

## Design Principle

The system must be inspectable end to end. An operator must be able to answer without
digging through session chaos:

- Who owns this task right now?
- What happened and in what order?
- Where did this flow get stuck?
- What did the agent know when it made this decision?
- Can I replay this run and understand why it produced this output?

## Minimum Required Instrumentation

Every event must carry:

| Field | Purpose |
|-------|---------|
| `correlation_id` | Groups all events in one logical flow or request |
| `causation_id` | Points to the event that caused this event |
| `dedup_key` | Enables idempotent processing and safe re-delivery |
| `event_type` | Structured type identifier |
| `timestamp` | When this event was emitted |
| `actor` | Which agent or runtime produced this event |
| `task_ref` | Associated task or flow, if applicable |
| `version` | Event schema version |

## Per-Run Observability Requirements

For every run (task, flow, or session), the system must be able to reconstruct:

| View | What it shows |
|------|--------------|
| **Timeline** | Ordered sequence of events for this run |
| **Tool call ledger** | Every tool invocation: what was called, when, with what inputs, and what was returned |
| **Memory write ledger** | Every write to agent memory: what was written, why, and from which event |
| **Prompt / context snapshot** | What the agent was given as input at each significant decision point |
| **Status history** | Ordered list of status transitions for the task or US |
| **Artifact lineage** | Which artifacts were produced, from which tasks, and where they were used |
| **Policy / version lineage** | Which prompt version, skill version, or routing rule was active |

## Source-of-Truth Model

| What | Source of Truth | Query Path |
|------|----------------|-----------|
| Current task status and owner | Task store / Mission Control | Direct query |
| What happened (events) | Event log | Timeline query by `correlation_id` |
| Agent knowledge at time T | Memory store (timestamped) | Memory read at version |
| Work results | Artifact store | Artifact query by task or flow ref |
| Workflow state in dev flow | Mission Control | MC query |

Event history is the source of truth for what happened. It is immutable and append-only.
Memory is not a substitute for the event log when reconstructing what occurred.

## Replay and Debug Path

The system must support:

**Replay:** Given a `correlation_id`, reproduce the sequence of events and agent inputs
that led to an outcome. Replay does not re-execute side effects — it reconstructs the
decision context.

**Debug path:** For any failed run, an operator must be able to:
1. Find the last known good state (last successful event)
2. Identify the point of failure (first anomalous or missing event)
3. Read the agent's input context at that point
4. Determine which recovery path was triggered

Replay must not require reading session transcripts. It must work from structured events.

## Structured Events

Events are not log lines. They are structured records with defined schemas.

Event categories (see [reference/canonical-events.md](reference/canonical-events.md)):
- **Lifecycle events:** task-created, task-accepted, task-completed, task-blocked, task-escalated
- **Handoff events:** handoff-dispatched, handoff-accepted, handoff-rejected, handoff-claimed
- **Artifact events:** artifact-produced, artifact-validated, artifact-referenced
- **Memory events:** memory-write, memory-correction, memory-retraction
- **Execution events:** tool-called, tool-returned, execution-started, execution-timeout
- **Flow events:** flow-started, flow-completed, flow-escalated, review-loop-incremented

## Correlation and Causation

Every flow produces a tree of events linked by `correlation_id` and `causation_id`.

```
user-request (correlation_id: req-001)
  └─ james-creates-task (causation_id: req-001)
       └─ handoff-dispatched (causation_id: james-creates-task)
            └─ handoff-accepted (causation_id: handoff-dispatched)
                 └─ task-in-progress (causation_id: handoff-accepted)
                      └─ artifact-produced (causation_id: task-in-progress)
                           └─ callback-sent (causation_id: artifact-produced)
```

This tree enables:
- full causal reconstruction of any outcome
- identification of the exact event that triggered a failure
- replay from any node in the tree

## Operator UX Requirements

At minimum, an operator must be able to:
- list all tasks and flows currently in a non-terminal state
- for any task: see owner, status, age, and last event
- for any flow: see the full event timeline
- for any failure: see the recovery action taken and its outcome
- search by `correlation_id`, task reference, agent, or artifact reference
- trigger a manual status override with a reason (audit trail preserved)
