# 11 — Observability and Audit

## Design Principle

The system must be inspectable end to end.

An operator must be able to answer without digging through transcript chaos:
- Who owns this request strategically right now?
- Who owns the execution work right now?
- Has the work finished?
- Has the human-visible reply actually been published?
- If not, what failed and who owns recovery?
- Is project indexing fresh, stale, or broken?
- Is memory retrieval healthy and explainable?

The channel session routing model adds one important observability requirement:

> **Operators must be able to distinguish task success, callback success, and reply publication success.**

---

## Minimum Required Instrumentation

Every event must carry:

| Field | Purpose |
|-------|---------|
| `correlation_id` | Groups all events in one logical execution lineage |
| `causation_id` | Points to the event that caused this event |
| `dedup_key` | Enables idempotent processing and safe redelivery |
| `event_type` | Structured type identifier |
| `timestamp` | When this event was emitted |
| `actor` | Which agent, runtime, or adapter produced this event |
| `version` | Event schema version |

For user-originated durable work, the system must also preserve:
- `request_id`
- origin session / surface context
- current reply target / reply session key (or request-state pointer)
- publication-state changes over time

---

## Per-Run Observability Requirements

For every relevant run (request, task, flow, or session), the system must be able to reconstruct:

| View | What it shows |
|------|--------------|
| **Request timeline** | Ordered request-routing/publication events |
| **Flow / task timeline** | Ordered execution events and status transitions |
| **Tool call ledger** | What tools were called, when, with what inputs, and what they returned |
| **Memory write ledger** | What memory was written, why, and from which event |
| **Retrieval / indexing ledger** | Which indexes were queried or updated, with what versions, freshness state, and outcomes |
| **Prompt / context snapshot** | What the agent was given at each significant decision point |
| **Artifact lineage** | Which artifacts were produced, from which tasks, and where they were used |
| **Policy / version lineage** | Which prompt / skill / routing version was active |

---

## Source-of-Truth Model

| What | Source of Truth | Query Path |
|------|----------------|-----------|
| Current request routing/publication state | request store | query by `request_id` |
| Current task status and execution owner | task store / Mission Control | direct query |
| What happened (chronology) | event log | timeline query by `correlation_id` and/or `request_id` |
| Agent knowledge at time T | memory store (timestamped) | versioned memory read |
| Code/doc index state | project index store | query by project / path / index run |
| Work results | artifact store | artifact query by task or flow ref |

Event history is the source of truth for what happened.
The request record is the source of truth for request routing/publication state.
Memory is not a substitute for either.

---

## Required Operator Views

### 1. Request view

For any `request_id`, an operator must be able to see:
- strategic owner
- origin session / surface
- request class
- current reply target
- reply target history
- current reply publication state
- publication attempts and outcomes
- fallback history
- linked task/flow references

### 2. Task / flow view

For any task or flow, an operator must be able to see:
- current execution owner
- status and status history
- last event
- callback target
- linked request if applicable

### 2a. Index / retrieval view

For any managed project or retrieval plane, an operator must be able to see:
- index freshness state
- last successful index run
- current dirty queue / stale count
- parser/chunker/embedding versions
- failed files/chunks if any
- last retrieval errors or timeouts

### 3. Joined operator view

The operator should be able to see, in one joined view:
- request state
- task/flow state
- callback state
- publication state
- retrieval/index health when relevant
- links between `request_id` and `correlation_id`

This is the minimum necessary to debug “work is done but the human never got the answer”.

---

## Replay and Debug Path

The system must support:

### Replay
Given a `request_id` and/or `correlation_id`, reconstruct:
- the ordered event sequence
- the request routing/publication context
- the agent inputs used for key decisions
- the task / flow transitions

Replay does not re-execute side effects. It reconstructs decision context.

### Debug path
For any failed or ambiguous run, an operator must be able to:
1. find the last known good state
2. identify the first anomalous or missing event
3. inspect request state, task state, and publication state at that point
4. see which recovery path was triggered
5. decide whether retry, fallback, reconciliation, or escalation is appropriate

Replay must not require reading session transcripts to understand the durable state.

---

## Correlation and Request Identity

`correlation_id` and `request_id` serve different purposes and must both be visible.

| Identifier | Meaning |
|-----------|---------|
| `request_id` | Durable identity of the user-originated request |
| `correlation_id` | Logical execution lineage / event tree |

### Practical rule

Operators must be able to:
- search by `request_id`
- search by `correlation_id`
- move from one to the other quickly

Do not force operators to guess which identifier matters in a given failure.

---

## Structured Events

Events are not log lines. They are structured records with defined schemas.

Important categories include:
- request / routing / publication events
- lifecycle events
- handoff events
- callback events
- artifact events
- execution events
- memory events
- flow events

See [reference/canonical-events.md](reference/canonical-events.md).

---

## Operator UX Requirements

At minimum, an operator must be able to:
- list all requests currently in a non-terminal publication/routing state
- list all tasks / flows currently in a non-terminal execution state
- list all projects/indexes currently stale, failed, or repair-required
- for any request: see owner, reply target, publication state, age, and last request event
- for any task: see owner, status, age, and last task event
- for any index: see freshness state, age, and last index event
- for any failure: see the recovery action taken and its outcome
- search by `request_id`, `correlation_id`, task reference, agent, artifact reference, or project/path
- trigger a manual override / reconciliation decision with a reason (audit trail preserved)

---

## Required Operator Scenarios

The system should support direct inspection of scenarios such as:
- work done but reply unpublished
- reply published but callback chain incomplete
- request waiting on fallback authorization
- cross-surface follow-up linked to prior request
- late callback after reassignment
- ambiguous publish after retry

If the runtime cannot answer those cleanly, observability is still incomplete.

## Operator Surfaces

The built-in Web UI host is the primary operator/admin/configuration surface.
The CLI is the parallel operational surface for agents and operators.
Both must expose the same authoritative runtime and Mission Control state rather than creating divergent operational stories.