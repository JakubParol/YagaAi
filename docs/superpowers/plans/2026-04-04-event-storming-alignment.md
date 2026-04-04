# Event Storming Alignment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Agent Runtime documentation explicitly and consistently Event Storming-aligned — formal vocabulary, Command/Event separation, named Policy catalog, event log as backbone.

**Architecture:** Pure documentation editing across 9 existing files and 1 new file in `docs/agent-runtime/`. No code, no tests, no build steps. Foundational files (glossary, canonical-events, policies) are edited first; narrative docs that reference those terms follow.

**Tech Stack:** Markdown. All files in `docs/agent-runtime/`.

**Spec:** `docs/superpowers/specs/2026-04-04-event-storming-alignment-design.md`

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `docs/agent-runtime/reference/glossary.md` | Modify | Add 7 new entries; update Command and Event entries |
| `docs/agent-runtime/reference/canonical-events.md` | Modify | Remove Scope Note; add 4 new event categories; add "no silent operations" rule |
| `docs/agent-runtime/reference/policies.md` | **Create** | Named Policy catalog |
| `docs/agent-runtime/00-input-one-pager.md` | Modify | "Event-Driven by Default" + A2A primitives sections |
| `docs/agent-runtime/02-core-model.md` | Modify | Add ES model subsection; Command→Aggregate→Event invariant; strengthen event log entry |
| `docs/agent-runtime/03-runtime-and-a2a.md` | Modify | Sharpen command table row; add invariant paragraph; label handoff transitions |
| `docs/agent-runtime/09-operational-flows.md` | Modify | Policy annotations; Domain Event labels on state transitions |
| `docs/agent-runtime/10-failure-recovery-and-timeouts.md` | Modify | Policy column in failure tables; watchdog sequences in timeout section; Policy framing in recovery section |
| `docs/agent-runtime/11-observability-and-audit.md` | Modify | Event log as backbone; Policy activation ledger row; updated event category list |

---

## Task 1: Update glossary — add new vocabulary entries

**File:** `docs/agent-runtime/reference/glossary.md`

The glossary is alphabetically ordered. Insert each new entry in its correct alphabetical position.

- [ ] **Step 1: Add `Aggregate` entry after the `Agent` entry**

Insert after the `Agent` block (after the line `See [02-core-model.md](../02-core-model.md).` that closes the Agent entry), leaving a blank line before the new entry:

```markdown
**Aggregate**  
A Domain Object that owns an invariant boundary: it validates incoming Commands, enforces
business rules, and emits Domain Events. Aggregates are the only things that change state.
In Yaga, the Aggregates are: `Agent`, `Request`, `Task`, `Handoff`, `Flow`. Each has
exactly one authoritative store.
```

- [ ] **Step 2: Add `Bounded Context` entry after the `Artifact` entry**

Insert after the `Artifact` block (after the line `See [artifact-model.md](artifact-model.md).`):

```markdown
**Bounded Context**  
A named subsystem with its own model, vocabulary, and Aggregate ownership boundary. In Yaga:
**Agent Runtime** (request routing, A2A, callbacks, events, memory, indexing) and **Mission
Control** (dev workflow state) are the two primary Bounded Contexts. Cross-context
communication goes through explicit Domain Events and Commands, not shared mutable state.
```

- [ ] **Step 3: Add `Domain Event` entry after the `Detached Execution` entry**

Insert after the `Detached Execution` block (after "The correct default for important work."):

```markdown
**Domain Event**  
An immutable, named fact that something happened inside a Bounded Context. Domain Events are
the primary output of Aggregates. They cannot be undone. See also **Event** (short alias).
Every operation in the system produces at least one Domain Event.
See [canonical-events.md](canonical-events.md).
```

- [ ] **Step 4: Add `External System` entry after the `Execution Timeout` entry**

Insert after the `Execution Timeout` block (after "See [10-failure-recovery-and-timeouts.md](../10-failure-recovery-and-timeouts.md)."):

```markdown
**External System**  
A system outside a Bounded Context that emits inputs or consumes outputs. In Yaga: surface
adapters (WhatsApp, Discord, web, CLI) are External Systems relative to the Agent Runtime
Bounded Context.
```

- [ ] **Step 5: Add `Policy` entry after the `Owner Session` entry and before `Procedural Memory / Skills`**

Insert after the `Owner Session` block (after the line ending "See [02-core-model.md](../02-core-model.md) and [04-channel-sessions-and-main-owner-routing.md](../04-channel-sessions-and-main-owner-routing.md)."):

```markdown
**Policy**  
An automatic reaction to a Domain Event, expressed as: "Whenever [Domain Event], issue
[Command]." Policies are first-class, named, and catalogued in [policies.md](policies.md).
They are not implementation details. Every watchdog start, retry schedule, loop-limit
escalation, and fallback invocation is a Policy.
```

- [ ] **Step 6: Add `Read Model` entry after the `Publish Intent` entry and before `Reply Intent`**

Insert after the `Publish Intent` block (after the line ending "See [03-runtime-and-a2a.md](../03-runtime-and-a2a.md)."):

```markdown
**Read Model**  
A projection of Domain Events optimised for querying. The request view, task view, index
health view, and operator dashboard are Read Models built from the event log. Read Models
are eventually consistent with the event log. They are not sources of command truth and
cannot be used to validate Commands.
See [11-observability-and-audit.md](../11-observability-and-audit.md).
```

- [ ] **Step 7: Commit**

```bash
git add docs/agent-runtime/reference/glossary.md
git commit -m "docs(agent-runtime): add Event Storming vocabulary to glossary — Aggregate, Bounded Context, Domain Event, External System, Policy, Read Model"
```

---

## Task 2: Update glossary — sharpen existing Command and Event entries

**File:** `docs/agent-runtime/reference/glossary.md`

- [ ] **Step 1: Replace the existing `Command` entry**

Find and replace:

```markdown
**Command**  
A message expressing intent to perform an action. One of the A2A primitive types.
See [03-runtime-and-a2a.md](../03-runtime-and-a2a.md).
```

Replace with:

```markdown
**Command**  
A message expressing intent to change state, addressed to an Aggregate. Commands may be
rejected — rejection always produces a `command.rejected` Domain Event. A Command that is
accepted always produces one or more Domain Events. No Command is silent.
One of the A2A primitive types.
See [03-runtime-and-a2a.md](../03-runtime-and-a2a.md).
```

- [ ] **Step 2: Replace the existing `Event` entry**

Find and replace:

```markdown
**Event**  
An immutable fact that something happened. The authoritative execution trace.
See [canonical-events.md](canonical-events.md).
```

Replace with:

```markdown
**Event**  
An immutable fact that something happened. The authoritative execution trace.
Also referred to as **Domain Event** — the preferred term when distinguishing from
Commands. An Event is an immutable fact; a Command is an intent that may be refused.
See [canonical-events.md](canonical-events.md).
```

- [ ] **Step 3: Commit**

```bash
git add docs/agent-runtime/reference/glossary.md
git commit -m "docs(agent-runtime): sharpen Command and Event glossary entries — Commands may be rejected, Domain Event as preferred alias"
```

---

## Task 3: Create reference/policies.md

**File:** `docs/agent-runtime/reference/policies.md` (new file)

- [ ] **Step 1: Create the file with the full Policy catalog**

```markdown
# Policies

A Policy is an automatic reaction to a Domain Event.

Expressed as: "Whenever [Domain Event], issue [Command]."

Policies are enforced by the runtime or Mission Control, not by individual agents making
ad-hoc decisions. They are first-class system concepts, not implementation details.

Every watchdog start, retry schedule, loop-limit escalation, and fallback invocation in
the system is a named Policy in this catalog.

## Policy Catalog

| Policy | Trigger Event | Command Issued | Owner | Notes |
|--------|---------------|----------------|-------|-------|
| `WatchAcceptanceTimeout` | `handoff.dispatched` | `StartAcceptanceWatchdog` | runtime | Watchdog fires `watchdog.fired` → `handoff.timeout` if not accepted within window |
| `EscalateOnHandoffTimeout` | `handoff.timeout` | `EscalateToStrategicOwner` | runtime | |
| `WatchOrphanedWork` | `task.accepted` | `StartOrphanWatchdog` | runtime | Watchdog fires `execution.timeout` if no progress within window |
| `EscalateOnOrphanTimeout` | `execution.timeout` (orphan) | `NotifyTaskOwner` → `EscalateToJames` | runtime | Two-stage: notify first, escalate if no response |
| `WatchPublicationTimeout` | `reply.publication_attempted` | `StartPublicationWatchdog` | runtime | Watchdog fires `watchdog.fired` if no terminal outcome within policy window |
| `RetryPublicationOnFailure` | `reply.publication_failed` | `RetryPublish` | runtime / strategic owner | Reuses same `publish_dedup_key` |
| `InvokeFallbackOnPublicationTimeout` | `watchdog.fired` (policy: `WatchPublicationTimeout`) | `InvokeReplyFallback` | strategic owner | Requires explicit fallback target |
| `RetryNormalizationOnAdapterFailure` | `request.normalization_attempted` (no ack within window) | `RetryNormalization` | surface adapter | Idempotent; same dedup identity |
| `ReturnToInProgressOnReviewComment` | `review_loop.incremented` | `ReturnTaskToOwner` | Mission Control | Carries review comments as artifact |
| `EscalateOnReviewLimitReached` | `review_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `EscalateOnVerifyLimitReached` | `verify_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `ContinueOnMemoryWriteFailure` | `memory.write_failed` | _(none — explicit non-interruption)_ | runtime | Domain Event is emitted and observable. Policy explicitly chooses not to issue a blocking Command. Task continues. |

## Reading the Catalog

- **Policy** — the name used in inline annotations throughout the operational flow docs.
- **Trigger Event** — the Domain Event that causes the Policy to fire.
- **Command Issued** — what the Policy tells the system to do next. `_(none)_` means the Policy explicitly chooses non-interruption; the Domain Event is still observable.
- **Owner** — which component is responsible for enforcing this Policy.
- **Notes** — additional constraints, two-stage behaviour, or escalation clauses.

Watchdog-based Policies follow the sequence:
```
[trigger event] → watchdog.started → watchdog.fired → [reaction Policy] → [command]
```
`watchdog.cancelled` is emitted if the condition resolves before the watchdog fires (e.g., a handoff is accepted before the acceptance window closes).
```

- [ ] **Step 2: Commit**

```bash
git add docs/agent-runtime/reference/policies.md
git commit -m "docs(agent-runtime): add reference/policies.md — named Policy catalog as first-class concept"
```

---

## Task 4: Update canonical-events.md

**File:** `docs/agent-runtime/reference/canonical-events.md`

- [ ] **Step 1: Replace the opening paragraph with a "no silent operations" statement**

Find the current opening (first four lines after the `# Canonical Events` heading):

```markdown
All events carry:
- `correlation_id`
- `causation_id`
- `dedup_key`
- `event_type`
- `timestamp`
- `actor`
- `version`

For user-originated durable work, events should also retain the link to `request_id`
even when the request record remains the primary routing/publication store.
```

Replace with:

```markdown
Every operation in the system emits a Domain Event. There are no silent operations.
If it happened, there is an event for it. This applies to fire-and-forget messages,
adapter notifications, watchdog activations, retry schedules, memory writes, and
publication attempts — without exception.

All events carry:
- `correlation_id`
- `causation_id`
- `dedup_key`
- `event_type`
- `timestamp`
- `actor`
- `version`

For user-originated durable work, events should also retain the link to `request_id`
even when the request record remains the primary routing/publication store.
```

- [ ] **Step 2: Remove the "Scope Note" section at the bottom**

Find and delete the entire `## Scope Note` section:

```markdown
## Scope Note

Keep the canonical request/publication event set tight.
Additional events such as publish acknowledgement, retry scheduled, or retry exhausted
should only be introduced if the implementation needs them beyond the minimum v1 model.

The same principle applies to indexing/retrieval events: keep the core set focused on freshness, failures, repairs, and query observability rather than turning the event catalog into a low-level parser trace.
```

Remove it entirely. Nothing replaces it — the "no silent operations" rule at the top is the replacement.

- [ ] **Step 3: Add the Watchdog / Timer Events category**

Add before the end of the file (which now ends at `retrieval.query_failed`):

```markdown
## Watchdog / Timer Events

Watchdogs are armed by Policies and disarmed when the condition resolves.
See [reference/policies.md](policies.md) for which Policy arms each watchdog.

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `watchdog.started` | runtime | `watchdog_ref`, `trigger_event_id`, `policy`, `timeout_at` | Watchdog armed by a Policy |
| `watchdog.fired` | runtime | `watchdog_ref`, `policy`, `elapsed` | Watchdog timeout elapsed; Policy reaction triggered |
| `watchdog.cancelled` | runtime | `watchdog_ref`, `reason`, `cancelled_by_event_id` | Watchdog disarmed before firing (condition resolved) |
```

- [ ] **Step 4: Add the Retry Events category**

Add immediately after the Watchdog / Timer Events section:

```markdown
## Retry Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `retry.scheduled` | runtime | `subject_ref`, `attempt`, `retry_at`, `policy` | Retry scheduled by a Policy |
| `retry.attempted` | runtime | `subject_ref`, `attempt`, `dedup_key` | Retry attempt made |
| `retry.exhausted` | runtime | `subject_ref`, `attempts`, `policy` | All retry attempts consumed; escalation path triggered |
```

- [ ] **Step 5: Add the Adapter Notification Events category**

Add immediately after the Retry Events section:

```markdown
## Adapter Notification Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `adapter.notification_sent` | surface adapter | `adapter_id`, `target`, `notification_type`, `dedup_key` | Fire-and-forget adapter push sent |
| `adapter.notification_failed` | surface adapter | `adapter_id`, `target`, `notification_type`, `error` | Adapter push failed |
```

- [ ] **Step 6: Add the Command Rejection Events category**

Add immediately after the Adapter Notification Events section:

```markdown
## Command Rejection Events

A Command that is rejected by an Aggregate invariant check always produces this event.
No Command is silent.

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `command.rejected` | Aggregate (via runtime) | `command_type`, `aggregate_id`, `aggregate_type`, `reason`, `actor` | Command received but rejected by Aggregate invariant check |
```

- [ ] **Step 7: Commit**

```bash
git add docs/agent-runtime/reference/canonical-events.md
git commit -m "docs(agent-runtime): canonical-events — no silent operations rule, remove Scope Note, add 4 new event categories"
```

---

## Task 5: Update 00-input-one-pager.md

**File:** `docs/agent-runtime/00-input-one-pager.md`

- [ ] **Step 1: Sharpen the "Event-Driven by Default" section opening**

Find:

```markdown
## Event-Driven by Default

The system should be built around events.
Events are the nervous system of the runtime.

We want events for:
```

Replace with:

```markdown
## Event-Driven by Default

The system is built around Domain Events.
Domain Events are the nervous system of the runtime.

We want Domain Events for:
```

- [ ] **Step 2: Add the "no silent operations" rule after the events list**

Find the block that ends with:

```markdown
- and audit.

Why this matters:
```

Insert before "Why this matters:" the following paragraph:

```markdown
Every operation — including fire-and-forget messages, adapter notifications, watchdog pings,
memory writes, and internal state transitions — emits a Domain Event. There are no silent
operations. If it happened, there is an event for it.

```

- [ ] **Step 3: Sharpen the A2A primitives list**

Find:

```markdown
The core primitives are:

- **commands** — intent to do something
- **events** — fact that something happened
- **statuses** — canonical state snapshot
- **artifacts** — produced work results
```

Replace with:

```markdown
The core primitives are:

- **commands** — intent to do something (may be rejected; rejection emits a Domain Event)
- **events** — immutable Domain Event facts; cannot be undone
- **statuses** — canonical state snapshot
- **artifacts** — produced work results
```

- [ ] **Step 4: Commit**

```bash
git add docs/agent-runtime/00-input-one-pager.md
git commit -m "docs(agent-runtime): 00-input-one-pager — Domain Event terminology, no silent operations rule, sharpen A2A primitives"
```

---

## Task 6: Update 02-core-model.md

**File:** `docs/agent-runtime/02-core-model.md`

- [ ] **Step 1: Add the Event Storming Model subsection after the Entity Overview table**

Find the line that ends the Entity Overview table (the last row ends with `| Mission Control |`), followed by the `## Entity Definitions` heading. Insert a new subsection between the table and `## Entity Definitions`:

```markdown
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

```

- [ ] **Step 2: Strengthen the event log entry in the Source-of-Truth Rules section**

Find in the "Practical split" subsection:

```markdown
- **Event log** answers: what happened, in what order, and why?
```

Replace with:

```markdown
- **Event log** answers: what happened, in what order, and why — the backbone from which
  watchdogs arm, Policies react, retries schedule, and recovery paths operate. Read Models
  (operator views, status projections) are derived from it.
```

- [ ] **Step 3: Commit**

```bash
git add docs/agent-runtime/02-core-model.md
git commit -m "docs(agent-runtime): 02-core-model — add Event Storming model subsection, strengthen event log description"
```

---

## Task 7: Update 03-runtime-and-a2a.md

**File:** `docs/agent-runtime/03-runtime-and-a2a.md`

- [ ] **Step 1: Sharpen the command row in the communication model table**

Find:

```markdown
| **command** | Intent to perform an action | agent / adapter | `assign-task`, `request-review`, `publish-reply` |
```

Replace with:

```markdown
| **command** | Intent to perform an action, addressed to an Aggregate. May be rejected — rejection always produces a `command.rejected` Domain Event | agent / adapter | `assign-task`, `request-review`, `publish-reply` |
```

- [ ] **Step 2: Sharpen the event row in the communication model table**

Find:

```markdown
| **event** | Fact that something happened | agent / runtime / adapter | `handoff.accepted`, `reply.published` |
```

Replace with:

```markdown
| **event** | Immutable Domain Event fact that something happened; cannot be undone | agent / runtime / adapter | `handoff.accepted`, `reply.published` |
```

- [ ] **Step 3: Add the Command→Aggregate→Domain Event invariant paragraph**

Find:

```markdown
Commands express intent. Events express facts. Status is derived state. Artifacts are outputs.
These must not be conflated.
```

Replace with:

```markdown
Commands express intent. Events express facts. Status is derived state. Artifacts are outputs.
These must not be conflated.

The Command → Aggregate → Domain Event chain is the fundamental unit of state change. No
state change occurs without a Domain Event. A rejected Command produces a `command.rejected`
Domain Event. There are no silent operations.
```

- [ ] **Step 4: Label handoff transitions as Domain Events in acceptance semantics**

Find:

```markdown
A handoff is not complete at dispatch. It transitions through:

```text
dispatched → pending → accepted | rejected → in-progress → done | failed | escalated
```
```

Replace with:

```markdown
A handoff is not complete at dispatch. It transitions through Domain Events:

```text
handoff.dispatched → pending → handoff.accepted | handoff.rejected → in-progress → done | failed | escalated
```
```

- [ ] **Step 5: Commit**

```bash
git add docs/agent-runtime/03-runtime-and-a2a.md
git commit -m "docs(agent-runtime): 03-runtime-and-a2a — sharpen Command/Event table rows, add Command→Aggregate→Event invariant, label handoff transitions as Domain Events"
```

---

## Task 8: Update 09-operational-flows.md

**File:** `docs/agent-runtime/09-operational-flows.md`

- [ ] **Step 1: Add Policy annotation to Research Flow step 3**

Find:

```markdown
3. James main decides the work is durable and delegates to `agent:alex:main`.
```

Replace with:

```markdown
3. James main decides the work is durable and delegates to `agent:alex:main`. `[Policy: WatchAcceptanceTimeout fires on handoff.dispatched]`
```

- [ ] **Step 2: Add Domain Event labels to Research Flow state shape**

Find:

```markdown
```text
request: received → normalized → delegated → awaiting_callback → reply_publish_pending → reply_published

task: Created → Accepted (Alex) → In Progress → Done
```
```

Replace with:

```markdown
```text
request: received →[request.received]→ normalized →[request.normalization_accepted]→ delegated →[handoff.dispatched]→ awaiting_callback →[callback.received]→ reply_publish_pending →[reply.publication_attempted]→ reply_published →[reply.published]

task: Created →[task.created]→ Accepted →[task.accepted]→ In Progress →[task.started]→ Done →[task.completed]
```
```

- [ ] **Step 3: Add Policy annotation to Research Flow escalation path**

Find:

```markdown
If publication fails after research succeeds, the request remains operationally open until retry,
fallback, or abandonment is resolved.
```

Replace with:

```markdown
If publication fails after research succeeds: `[Policy: RetryPublicationOnFailure fires on reply.publication_failed]`; if unresolved within window: `[Policy: InvokeFallbackOnPublicationTimeout fires on watchdog.fired]`. The request remains operationally open until a terminal publication outcome is recorded.
```

- [ ] **Step 4: Add Policy annotation to Implementation Flow step 3**

Find:

```markdown
3. James main creates or identifies the relevant US and delegates implementation to `agent:naomi:main`.
```

Replace with:

```markdown
3. James main creates or identifies the relevant US and delegates implementation to `agent:naomi:main`. `[Policy: WatchAcceptanceTimeout fires on handoff.dispatched]`
```

- [ ] **Step 5: Add Domain Event labels to Implementation Flow state shape**

Find:

```markdown
```text
request: received → normalized → delegated → awaiting_callback → reply_publish_pending → reply_published

US: Created → In Progress → Code Review → Verify → Done
Tasks: Created → Accepted → In Progress → Done (or Blocked / Escalated)
```
```

Replace with:

```markdown
```text
request: received →[request.received]→ normalized →[request.normalization_accepted]→ delegated →[handoff.dispatched]→ awaiting_callback →[callback.received]→ reply_publish_pending →[reply.publication_attempted]→ reply_published →[reply.published]

US: Created →[flow.started]→ In Progress →[task.started]→ Code Review →[review_loop.incremented]→ Verify →[task.accepted]→ Done →[flow.completed]
Tasks: Created →[task.created]→ Accepted →[task.accepted]→ In Progress →[task.started]→ Done →[task.completed] (or Blocked →[task.blocked] / Escalated →[task.escalated])
```
```

- [ ] **Step 6: Add Policy annotations to QA Flow — Code Review loop**

Find:

```markdown
3. If approved: Amos / MC move the US to `Verify`.
4. If comments: Amos returns it to `In Progress`; Naomi receives loop-return callback.
5. Loop repeats up to the configured limit.
6. If the loop limit is exceeded: escalate to James main.
```

Replace with:

```markdown
3. If approved: Amos / MC move the US to `Verify`.
4. If comments: `[Policy: ReturnToInProgressOnReviewComment fires on review_loop.incremented]`; Naomi receives loop-return callback with review comments as artifact.
5. Loop repeats up to the configured limit.
6. If the loop limit is exceeded: `[Policy: EscalateOnReviewLimitReached fires on review_loop.limit_reached]`, escalating to James main.
```

- [ ] **Step 7: Add Policy annotation to QA Flow — Verify loop**

Find:

```markdown
4. If failed: MC returns the US to `In Progress`; Naomi receives loop-return callback.
5. If verify does not converge: escalate to James main.
```

Replace with:

```markdown
4. If failed: MC returns the US to `In Progress`; Naomi receives loop-return callback.
5. If verify does not converge: `[Policy: EscalateOnVerifyLimitReached fires on verify_loop.limit_reached]`, escalating to James main.
```

- [ ] **Step 8: Commit**

```bash
git add docs/agent-runtime/09-operational-flows.md
git commit -m "docs(agent-runtime): 09-operational-flows — Policy annotations, Domain Event labels on state transitions"
```

---

## Task 9: Update 10-failure-recovery-and-timeouts.md

**File:** `docs/agent-runtime/10-failure-recovery-and-timeouts.md`

- [ ] **Step 1: Add Policy framing to the Design Principle section**

Find:

```markdown
For every important failure mode, the system must define:
- a **recovery owner**
- a **default action**
- a **bounded retry / escalation path**
- an explicit terminal or near-terminal outcome
```

Replace with:

```markdown
For every important failure mode, the system must define:
- a **recovery owner**
- a **default action**
- a **bounded retry / escalation path**
- an explicit terminal or near-terminal outcome

Recovery paths are Policies: automatic reactions to Domain Events with named owners and
bounded retry clauses. Each failure mode below has a corresponding named Policy in
[reference/policies.md](reference/policies.md) where one exists.
```

- [ ] **Step 2: Add Policy column to the Inbound / Normalization Failures table**

Find:

```markdown
### 1. Inbound / Normalization Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Duplicate inbound normalization | Same inbound request normalized more than once | owner-side request path | Dedup by request-level key; no duplicate work |
| Adapter failure before durable acceptance | Surface adapter received the message but owner path did not durably accept it | surface adapter | Retry normalization with same dedup identity |
| Main endpoint unavailable during normalization | Owner-facing `main` path unreachable/unavailable | surface adapter / runtime | Retry until timeout policy, then escalate |
| Normalization rejected | Owner path explicitly rejects malformed or invalid request | owner-side runtime | Emit rejection; surface may notify/fail visibly if needed |
```

Replace with:

```markdown
### 1. Inbound / Normalization Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Duplicate inbound normalization | Same inbound request normalized more than once | owner-side request path | Dedup by request-level key; no duplicate work | — |
| Adapter failure before durable acceptance | Surface adapter received the message but owner path did not durably accept it | surface adapter | Retry normalization with same dedup identity | `RetryNormalizationOnAdapterFailure` |
| Main endpoint unavailable during normalization | Owner-facing `main` path unreachable/unavailable | surface adapter / runtime | Retry until timeout policy, then escalate | `RetryNormalizationOnAdapterFailure` |
| Normalization rejected | Owner path explicitly rejects malformed or invalid request | owner-side runtime | Emit `command.rejected` Domain Event; surface may notify/fail visibly if needed | — |
```

- [ ] **Step 3: Add Policy column to the Handoff / Callback Failures table**

Find:

```markdown
### 2. Handoff / Callback Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Lost handoff | Handoff dispatched but never acknowledged | requester | Retry or reassign after timeout |
| Duplicate handoff / callback | Same handoff or callback delivered more than once | receiver | Dedup by `dedup_key`; second delivery is a no-op |
| Callback missing after task completion | Work completed but callback never received | completing owner / system | Retry callback; if persistent, block/escalate |
| Callback arrives after cancellation | Late callback for cancelled work | strategic owner | Reconcile; do not silently reopen cancelled work |
| Callback arrives after reassignment | Prior owner/executor returns late result after ownership moved | strategic owner | Reconcile against current authority; record late arrival |
```

Replace with:

```markdown
### 2. Handoff / Callback Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Lost handoff | Handoff dispatched but never acknowledged | requester | Retry or reassign after timeout | `WatchAcceptanceTimeout` → `EscalateOnHandoffTimeout` |
| Duplicate handoff / callback | Same handoff or callback delivered more than once | receiver | Dedup by `dedup_key`; second delivery is a no-op | — |
| Callback missing after task completion | Work completed but callback never received | completing owner / system | Retry callback; if persistent, block/escalate | `WatchOrphanedWork` → `EscalateOnOrphanTimeout` |
| Callback arrives after cancellation | Late callback for cancelled work | strategic owner | Reconcile; do not silently reopen cancelled work | — |
| Callback arrives after reassignment | Prior owner/executor returns late result after ownership moved | strategic owner | Reconcile against current authority; record late arrival | — |
```

- [ ] **Step 4: Add Policy column to the Execution / Workflow Failures table**

Find:

```markdown
### 3. Execution / Workflow Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Worker crash | Execution runtime terminates mid-task | task owner | Retry execution or reassign executor |
| Orphaned work | Task accepted but no progress events for defined period | task owner / James | Workflow timeout, prompt owner, escalate if needed |
| Partial tool failure | Some tool calls succeed, others fail | task owner | Block with explicit reason; decide retry or escalate |
| Incomplete artifact | Artifact produced but fails validation | task owner / reviewer | Return to `In Progress` with error |
| Status / ownership conflict | Durable state disagrees about current owner or status | James / MC | Use authoritative store, emit reconciliation event |
```

Replace with:

```markdown
### 3. Execution / Workflow Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Worker crash | Execution runtime terminates mid-task | task owner | Retry execution or reassign executor | — |
| Orphaned work | Task accepted but no progress events for defined period | task owner / James | Workflow timeout, prompt owner, escalate if needed | `WatchOrphanedWork` → `EscalateOnOrphanTimeout` |
| Partial tool failure | Some tool calls succeed, others fail | task owner | Block with explicit reason; decide retry or escalate | — |
| Incomplete artifact | Artifact produced but fails validation | task owner / reviewer | Return to `In Progress` with error | — |
| Status / ownership conflict | Durable state disagrees about current owner or status | James / MC | Use authoritative store, emit `task.state_transition` reconciliation Domain Event | — |
```

- [ ] **Step 5: Add Policy column to the Reply Routing / Publication Failures table**

Find:

```markdown
### 4. Reply Routing / Publication Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Stale or missing reply target | Stored reply destination is invalid | strategic owner / request-state path | Mark `fallback_required` or retarget explicitly |
| Publication failure after specialist success | Task is done but human reply was not published | strategic owner / request-state path | Retry / fallback / escalate |
| Ambiguous publication after retry | Outcome unknown; reply may or may not have been delivered | strategic owner / request-state path | Mark `unknown`; reconcile before further publish |
| Publish acknowledgement missing | Publish attempt started but terminal result never confirmed | request-state path | Mark `attempted` or `unknown`; bounded retry or reconcile |
| Late publish success after ambiguity | Prior ambiguous attempt later proves successful | request-state path | Reconcile state; avoid duplicate publication |
| Fallback invocation required | Primary target no longer safe/valid | strategic owner / operator | Apply approved fallback or escalate |
```

Replace with:

```markdown
### 4. Reply Routing / Publication Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Stale or missing reply target | Stored reply destination is invalid | strategic owner / request-state path | Mark `fallback_required` or retarget explicitly | — |
| Publication failure after specialist success | Task is done but human reply was not published | strategic owner / request-state path | Retry / fallback / escalate | `RetryPublicationOnFailure` |
| Ambiguous publication after retry | Outcome unknown; reply may or may not have been delivered | strategic owner / request-state path | Mark `unknown`; reconcile before further publish | `WatchPublicationTimeout` → `InvokeFallbackOnPublicationTimeout` |
| Publish acknowledgement missing | Publish attempt started but terminal result never confirmed | request-state path | Mark `attempted` or `unknown`; bounded retry or reconcile | `WatchPublicationTimeout` → `InvokeFallbackOnPublicationTimeout` |
| Late publish success after ambiguity | Prior ambiguous attempt later proves successful | request-state path | Reconcile state; avoid duplicate publication | — |
| Fallback invocation required | Primary target no longer safe/valid | strategic owner / operator | Apply approved fallback or escalate | `InvokeFallbackOnPublicationTimeout` |
```

- [ ] **Step 6: Add Policy column to the Conversation Continuity Failures table**

Find:

```markdown
### 5. Conversation Continuity Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| User follow-up while work is in flight | New message arrives before prior request closes | strategic owner | New request by default; explicitly merge if needed |
| Cross-surface continuation | Same human continues on another surface | strategic owner | Create new request or explicit transfer/merge decision |
| Reply target mutated implicitly | Target changed by side effect or convenience logic | strategic owner / operator | Reject implicit mutation; require explicit audit event |
```

Replace with:

```markdown
### 5. Conversation Continuity Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| User follow-up while work is in flight | New message arrives before prior request closes | strategic owner | New request by default; explicitly merge if needed | — |
| Cross-surface continuation | Same human continues on another surface | strategic owner | Create new request or explicit transfer/merge decision | — |
| Reply target mutated implicitly | Target changed by side effect or convenience logic | strategic owner / operator | Reject implicit mutation; require explicit audit Domain Event | — |
```

- [ ] **Step 7: Add watchdog event sequences to the Timeout Types section**

Find:

```markdown
### Execution Timeout
- **Definition:** runtime/worker has not responded within the expected execution window
- **Scope:** runtime level
- **Handler:** retry execution, optionally with a new worker

### Workflow Timeout (SLA Timeout)
- **Definition:** expected process progress has not occurred within a business window
- **Scope:** task / flow level
- **Handler:** notify owner, prompt, escalate if needed

### Publication Timeout / Ambiguity Timeout
- **Definition:** a user-visible publish intent has no confirmed terminal outcome within policy window
- **Scope:** request/publication level
- **Handler:** bounded retry, reconciliation, fallback decision, or escalation
```

Replace with:

```markdown
### Execution Timeout
- **Definition:** runtime/worker has not responded within the expected execution window
- **Scope:** runtime level
- **Handler:** retry execution, optionally with a new worker
- **Event sequence:** `execution.started` → `watchdog.started` (`WatchOrphanedWork` Policy) → `watchdog.fired` → `EscalateOnOrphanTimeout` Policy → `NotifyTaskOwner` Command

### Workflow Timeout (SLA Timeout)
- **Definition:** expected process progress has not occurred within a business window
- **Scope:** task / flow level
- **Handler:** notify owner, prompt, escalate if needed
- **Event sequence:** `task.accepted` → `watchdog.started` (`WatchOrphanedWork` Policy) → `watchdog.fired` → `EscalateOnOrphanTimeout` Policy → `NotifyTaskOwner` → if unresolved → `EscalateToJames` Command

### Publication Timeout / Ambiguity Timeout
- **Definition:** a user-visible publish intent has no confirmed terminal outcome within policy window
- **Scope:** request/publication level
- **Handler:** bounded retry, reconciliation, fallback decision, or escalation
- **Event sequence:** `reply.publication_attempted` → `watchdog.started` (`WatchPublicationTimeout` Policy) → `watchdog.fired` → `InvokeFallbackOnPublicationTimeout` Policy → `InvokeReplyFallback` Command
```

- [ ] **Step 8: Add Policy framing to the Recovery Paths section**

Find:

```markdown
### Retry
Used when:
```

Replace with:

```markdown
### Retry
Implemented automatically by `RetryPublicationOnFailure` and `RetryNormalizationOnAdapterFailure` Policies. Manual retry applies when no named Policy covers the failure mode.

Used when:
```

Find:

```markdown
### Reassign
Used when:
```

Replace with:

```markdown
### Reassign
No named Policy — requires an explicit owner or operator decision after the current assignment is closed.

Used when:
```

Find:

```markdown
### Reconcile
Used when:
```

Replace with:

```markdown
### Reconcile
No named Policy — requires explicit investigation and a decision. Triggered when late-arriving signals conflict with believed state.

Used when:
```

Find:

```markdown
### Escalate
Used when:
```

Replace with:

```markdown
### Escalate
Implemented automatically by `EscalateOnHandoffTimeout`, `EscalateOnReviewLimitReached`, `EscalateOnVerifyLimitReached`, and `EscalateOnOrphanTimeout` Policies. Manual escalation applies when convergence fails despite automatic Policies firing.

Used when:
```

- [ ] **Step 9: Commit**

```bash
git add docs/agent-runtime/10-failure-recovery-and-timeouts.md
git commit -m "docs(agent-runtime): 10-failure-recovery — Policy framing, Policy column in failure tables, watchdog event sequences in timeout types"
```

---

## Task 10: Update 11-observability-and-audit.md

**File:** `docs/agent-runtime/11-observability-and-audit.md`

- [ ] **Step 1: Add event log backbone framing to the Design Principle section**

Find:

```markdown
## Design Principle

The system must be inspectable end to end.
```

Replace with:

```markdown
## Design Principle

The event log is the system's backbone. Watchdogs arm from it. Policies react to it.
Retries are scheduled from it. Read Models are derived from it. State reconstruction for
replay and recovery flows from it. It is not an audit trail appended after the fact; it is
the primary record from which all other views are derived.

The system must be inspectable end to end.
```

- [ ] **Step 2: Add Policy activation ledger row to the Per-Run Observability table**

Find the Per-Run Observability table. It ends with:

```markdown
| **Policy / version lineage** | Which prompt / skill / routing version was active |
```

Add immediately after that row (still inside the table):

```markdown
| **Policy activation ledger** | Which Policies fired, on which Domain Events, with what Commands issued and outcomes |
```

- [ ] **Step 3: Update the Structured Events section to reference new categories**

Find:

```markdown
Important categories include:
- request / routing / publication events
- lifecycle events
- handoff events
- callback events
- artifact events
- execution events
- memory events
- flow events
```

Replace with:

```markdown
Important categories include:
- request / routing / publication events
- lifecycle events
- handoff events
- callback events
- artifact events
- execution events
- memory events
- flow events
- watchdog / timer events
- retry events
- adapter notification events
- command rejection events
```

- [ ] **Step 4: Commit**

```bash
git add docs/agent-runtime/11-observability-and-audit.md
git commit -m "docs(agent-runtime): 11-observability — event log as backbone, Policy activation ledger, new event categories"
```

---

## Self-Review

### Spec coverage check

| Spec requirement | Covered by task |
|-----------------|-----------------|
| Every message emits a Domain Event — no exceptions | Task 4 (canonical-events no-silent rule), Task 5 (00 one-pager) |
| ES vocabulary introduced and defined | Tasks 1–2 (glossary) |
| Commands and Events formally separated | Tasks 2, 7 |
| Command → Aggregate → Domain Event chain explicit | Tasks 6, 7 |
| Policies named and treated as first-class | Task 3 (policies.md), Tasks 8, 9 |
| Event log as backbone, not audit trail | Tasks 6, 10 |
| Scope Note removed from canonical-events | Task 4 |
| 4 new event categories in canonical-events | Task 4 |
| Policy column in failure tables | Task 9 |
| Watchdog event sequences in timeout types | Task 9 |
| Policy annotations in operational flows | Task 8 |
| Domain Event labels on state transitions | Task 8 |
| Policy activation ledger in observability | Task 10 |
| Core architecture unchanged | All tasks (doc edits only) |
| No Event Sourcing introduced | All tasks (mutable stores not touched) |

### Placeholder scan

No placeholders, TBDs, or TODOs in any step. Every step contains exact replacement text.

### Consistency check

- Policy names used in Task 8 (09-operational-flows) and Task 9 (10-failure-recovery) match exactly the names defined in Task 3 (policies.md).
- Domain Event types used in state transition labels (Task 8) match entries in canonical-events.md (existing catalog + Task 4 additions).
- Watchdog event sequences in Task 9 use `watchdog.started`, `watchdog.fired` — defined in Task 4.
- Glossary cross-references in Task 1 point to `policies.md` — created in Task 3. Execute tasks in order.
