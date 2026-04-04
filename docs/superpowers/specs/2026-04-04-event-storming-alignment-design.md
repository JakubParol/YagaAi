# Design: Event Storming Alignment for Agent Runtime Docs

**Date:** 2026-04-04  
**Scope:** `docs/agent-runtime/`  
**Approach:** Full vocabulary integration (Approach B)

---

## Problem

The Agent Runtime documentation is event-driven in spirit but does not formally commit to Event Storming vocabulary or principles. Consequences:

- Commands and Domain Events are blurred in places
- Automatic reactions (watchdogs, loop limits, retry) are described as implementation details rather than named Policies
- The event log is framed as an audit trail, not the system backbone
- Vocabulary (Domain Event, Policy, Aggregate, Bounded Context, Read Model, External System) is absent from the glossary and inconsistently applied
- canonical-events.md has a "Scope Note" that actively limits event coverage, contradicting the "no silent operations" invariant

---

## Goal

After changes, the following must be true:

1. Every operation emits a Domain Event — no exceptions
2. Event Storming vocabulary is introduced, defined, and used consistently
3. Commands and Domain Events are formally separated and the distinction is crisp everywhere
4. Every Command traces to a Domain Event via explicit Command → Aggregate → Domain Event chain
5. Policies are named, catalogued, and treated as first-class concepts
6. The event log is explicitly framed as the system backbone, not an audit trail

The core architecture (agents, ownership model, routing topology, SQLite-first storage) is unchanged. This is not full Event Sourcing — mutable stores remain. Events are the nervous system and audit backbone, not the sole source of state reconstruction.

---

## Files Changed

| File | Change type |
|------|-------------|
| `reference/glossary.md` | Add 7 new entries; sharpen Command and Event |
| `reference/canonical-events.md` | Remove Scope Note; add 4 new event categories; add "no silent operations" rule |
| `reference/policies.md` | **New file** — named Policy catalog |
| `00-input-one-pager.md` | Sharpen "Event-Driven by Default" and A2A primitives sections |
| `02-core-model.md` | Add ES model subsection; add Command→Aggregate→Event chain; strengthen event log entry |
| `03-runtime-and-a2a.md` | Sharpen command row; add Command→Event invariant; label handoff transitions as Domain Events |
| `09-operational-flows.md` | Annotate Policy triggers inline; add Domain Event labels to state transitions |
| `10-failure-recovery-and-timeouts.md` | Frame recovery paths as Policies; add Policy column to failure tables; frame timeouts as watchdog event sequences |
| `11-observability-and-audit.md` | Reframe event log as backbone; add Policy activation ledger; reference new event categories |

---

## Section 1: Vocabulary (reference/glossary.md)

### New entries

**Domain Event**  
An immutable, named fact that something happened inside a Bounded Context. Domain Events are the primary output of Aggregates. They cannot be undone. The existing `Event` definition is retained as a short alias; `Domain Event` is the preferred term. Every operation in the system produces at least one Domain Event.

**Command**  
A message expressing intent to change state, addressed to an Aggregate. Commands may be rejected — rejection always produces a Domain Event (`command.rejected`). A Command that is accepted always produces one or more Domain Events. No Command is silent.

**Aggregate**  
A Domain Object that owns an invariant boundary: it validates incoming Commands, enforces business rules, and emits Domain Events. Aggregates are the only things that change state. In Yaga, the Aggregates are: `Agent`, `Request`, `Task`, `Handoff`, `Flow`. Each has exactly one authoritative store.

**Bounded Context**  
A named subsystem with its own model, vocabulary, and Aggregate ownership boundary. In Yaga: **Agent Runtime** (request routing, A2A, callbacks, events) and **Mission Control** (dev workflow state) are the two primary Bounded Contexts. Cross-context communication goes through explicit Domain Events and Commands, not shared mutable state.

**Policy**  
An automatic reaction to a Domain Event, expressed as: "Whenever [Domain Event], issue [Command]." Policies are first-class, named, and catalogued in `reference/policies.md`. They are not implementation details. Every watchdog start, retry schedule, loop-limit escalation, and fallback invocation is a Policy.

**Read Model**  
A projection of Domain Events optimised for querying. The request view, task view, index health view, and operator dashboard are Read Models built from the event log. Read Models are eventually consistent with the event log. They are not sources of command truth and cannot be used to validate Commands.

**External System**  
A system outside a Bounded Context that emits inputs or consumes outputs. In Yaga: surface adapters (WhatsApp, Discord, web) are External Systems relative to the Agent Runtime Bounded Context.

### Updated entries

**Command** (existing entry)  
Add: "Commands may be rejected. Rejection always produces a `command.rejected` Domain Event. A Command that is accepted always produces one or more Domain Events."

**Event** (existing entry)  
Add: "Also referred to as `Domain Event` — the preferred term when distinguishing from Commands. An Event is an immutable fact; a Command is an intent that may be refused."

---

## Section 2: New Artifacts

### reference/policies.md (new file)

A Policy is an automatic reaction to a Domain Event. Expressed as: "Whenever [Domain Event], issue [Command]." Policies are enforced by the runtime or Mission Control, not by individual agents making ad-hoc decisions.

Named Policy catalog:

| Policy | Trigger Event | Command Issued | Owner | Notes |
|--------|---------------|----------------|-------|-------|
| `WatchAcceptanceTimeout` | `handoff.dispatched` | `StartAcceptanceWatchdog` | runtime | Watchdog fires `handoff.timeout` if not accepted within window |
| `EscalateOnHandoffTimeout` | `handoff.timeout` | `EscalateToStrategicOwner` | runtime | |
| `ReturnToInProgressOnReviewComment` | `review_loop.incremented` | `ReturnTaskToOwner` | Mission Control | Carries review comments as artifact |
| `EscalateOnReviewLimitReached` | `review_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `EscalateOnVerifyLimitReached` | `verify_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `ContinueOnMemoryWriteFailure` | `memory.write_failed` | _(none — explicit non-interruption)_ | runtime | Domain Event is emitted and observable. Policy explicitly chooses not to issue a blocking Command. Task continues. |
| `RetryPublicationOnFailure` | `reply.publication_failed` | `RetryPublish` | runtime / strategic owner | Reuses same `publish_dedup_key` |
| `InvokeFallbackOnPublicationTimeout` | `watchdog.fired` (policy: `WatchPublicationTimeout`) | `InvokeReplyFallback` | strategic owner | Requires explicit fallback target |
| `WatchPublicationTimeout` | `reply.publication_attempted` | `StartPublicationWatchdog` | runtime | Watchdog fires `watchdog.fired` if no terminal outcome within window |
| `WatchOrphanedWork` | `task.accepted` | `StartOrphanWatchdog` | runtime | Watchdog fires `execution.timeout` if no progress within window |
| `EscalateOnOrphanTimeout` | `execution.timeout` (orphan) | `NotifyTaskOwner` → `EscalateToJames` | runtime | Two-stage: notify first, escalate if no response |
| `RetryNormalizationOnAdapterFailure` | `request.normalization_attempted` (no ack) | `RetryNormalization` | surface adapter | Idempotent; same dedup identity |

### reference/canonical-events.md changes

Remove the "Scope Note" section. Replace with:

> Every operation in the system emits a Domain Event. There are no silent operations. If it happened, there is an event for it. This applies to fire-and-forget messages, adapter notifications, internal transitions, watchdog activations, retry schedules, memory writes, and publication attempts — without exception.

Add four new event categories (removing "Internal Transition Events" — all named task and request transitions already have dedicated Domain Events in the Lifecycle and Request categories above; any gap should get a specific named event, not a generic one):

**Watchdog / Timer Events**

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `watchdog.started` | runtime | `watchdog_ref`, `trigger_event_id`, `policy`, `timeout_at` | Watchdog armed by a Policy |
| `watchdog.fired` | runtime | `watchdog_ref`, `policy`, `elapsed` | Watchdog timeout elapsed; Policy reaction triggered |
| `watchdog.cancelled` | runtime | `watchdog_ref`, `reason`, `cancelled_by_event_id` | Watchdog disarmed before firing |

**Retry Events**

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `retry.scheduled` | runtime | `subject_ref`, `attempt`, `retry_at`, `policy` | Retry scheduled by a Policy |
| `retry.attempted` | runtime | `subject_ref`, `attempt`, `dedup_key` | Retry attempt made |
| `retry.exhausted` | runtime | `subject_ref`, `attempts`, `policy` | All retry attempts consumed; escalation path triggered |

**Adapter Notification Events**

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `adapter.notification_sent` | surface adapter | `adapter_id`, `target`, `notification_type`, `dedup_key` | Fire-and-forget adapter push sent |
| `adapter.notification_failed` | surface adapter | `adapter_id`, `target`, `notification_type`, `error` | Adapter push failed |

**Command Rejection Events**

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `command.rejected` | Aggregate (via runtime) | `command_type`, `aggregate_id`, `aggregate_type`, `reason`, `actor` | Command received but rejected by Aggregate invariant check |

---

## Section 3: Narrative Doc Changes

### 00-input-one-pager.md

"Event-Driven by Default" section, first sentence:  
Before: "The system should be built around events."  
After: "The system is built around Domain Events."

Add after the events-list: "Every operation — including fire-and-forget messages, adapter notifications, watchdog pings, memory writes, and internal state transitions — emits a Domain Event. There are no silent operations. If it happened, there is an event for it."

A2A primitives list: sharpen `commands` entry — add "(may be rejected; rejection emits a Domain Event)"; sharpen `events` — add "(immutable Domain Event facts; cannot be undone)".

### 02-core-model.md

Add subsection **"Event Storming Model"** after the Entity Overview table:

```
Aggregates (validate Commands, emit Domain Events):
  Agent | Request | Task | Handoff | Flow

Bounded Contexts:
  Agent Runtime — owns: request routing, A2A, callbacks, events, memory, indexing
  Mission Control — owns: dev workflow state (US, tasks, review/verify loops)

External Systems (relative to Agent Runtime BC):
  Surface adapters (WhatsApp, Discord, web, CLI)

Fundamental invariant:
  Command → Aggregate validates → Domain Event emitted
  No state change occurs without a Domain Event.
  No Command is silent.
```

Strengthen the event log entry in Source-of-Truth Rules:  
Before: "what happened, in what order, and why?"  
After: "what happened, in what order, and why — the backbone from which watchdogs arm, Policies react, retries schedule, and recovery paths operate. Read Models (operator views, status projections) are derived from it."

### 03-runtime-and-a2a.md

Communication model table, `command` row — add to Meaning column: "may be rejected; rejection always produces a `command.rejected` Domain Event."

After the four-row table, add:

> The Command → Aggregate → Domain Event chain is the fundamental unit of state change. No state change occurs without a Domain Event. A rejected Command produces a rejection Domain Event. There are no silent operations.

In acceptance semantics, label each transition explicitly:  
`handoff.dispatched` (Domain Event) → `handoff.accepted` (Domain Event) | `handoff.rejected` (Domain Event)

### 09-operational-flows.md

Each flow step that triggers a Policy reaction gets an inline annotation:  
`[Policy: PolicyName]`

Research Flow:
- Step 3 (James delegates): `[Policy: WatchAcceptanceTimeout fires on handoff.dispatched]`
- Escalation path: `[Policy: EscalateOnHandoffTimeout fires on handoff.timeout]`

QA Flow:
- Review comment return: `[Policy: ReturnToInProgressOnReviewComment fires on review_loop.incremented]`
- Review limit: `[Policy: EscalateOnReviewLimitReached fires on review_loop.limit_reached]`
- Verify limit: `[Policy: EscalateOnVerifyLimitReached fires on verify_loop.limit_reached]`

Implementation Flow:
- Publication failure: `[Policy: RetryPublicationOnFailure fires on reply.publication_failed]`

State shape diagrams: add Domain Event type labels to each transition arrow.  
Example: `Created →[task.created]→ Accepted →[task.accepted]→ In Progress →[task.started]→ Done →[task.completed]`

### 10-failure-recovery-and-timeouts.md

Opening design principle — add:

> Recovery paths are Policies: automatic reactions to Domain Events with named owners and bounded retry clauses. Each failure mode below has a corresponding named Policy in `reference/policies.md`.

Each failure category table: add a **Policy** column.

Timeout types section: frame each as a watchdog Domain Event sequence:  
`[trigger event] → watchdog.started (WatchXxx Policy) → watchdog.fired → [reaction Policy] → [command]`

Recovery paths section (Retry, Reassign, Reconcile, Escalate): open each with "This is the default action of the relevant Policy when [condition]."

### 11-observability-and-audit.md

Design principle, replace opening framing — add:

> The event log is the system's backbone. Watchdogs arm from it. Policies react to it. Retries are scheduled from it. Read Models are derived from it. State reconstruction for replay and recovery flows from it. It is not an audit trail appended after the fact; it is the primary record.

Per-Run Observability table: add row:

| View | What it shows |
|------|--------------|
| **Policy activation ledger** | Which Policies fired, on which Domain Events, with what Commands issued and outcomes |

Structured Events section: add references to the five new event categories from canonical-events.md.

---

## What Does Not Change

- Core architecture: agents, ownership model, routing topology, SQLite-first storage
- No Event Sourcing: mutable stores remain the source of operational state
- No new features invented
- No files outside `docs/agent-runtime/` touched
- Writing style: terse, opinionated, no fluff
