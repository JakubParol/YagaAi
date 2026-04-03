# 08 — Failure, Recovery, and Timeouts

## Design Principle

Failures are expected operational events, not edge cases.

For every important failure mode, the system must define:
- a **recovery owner**
- a **default action**
- a **bounded retry / escalation path**
- an explicit terminal or near-terminal outcome

The integration of doc 12 adds one important rule:

> **Task success, callback success, and human-visible publication success are separate recovery concerns.**

---

## Failure Categories

### 1. Inbound / Normalization Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Duplicate inbound normalization | Same inbound request normalized more than once | owner-side request path | Dedup by request-level key; no duplicate work |
| Adapter failure before durable acceptance | Surface adapter received the message but owner path did not durably accept it | surface adapter | Retry normalization with same dedup identity |
| Main endpoint unavailable during normalization | Owner-facing `main` path unreachable/unavailable | surface adapter / runtime | Retry until timeout policy, then escalate |
| Normalization rejected | Owner path explicitly rejects malformed or invalid request | owner-side runtime | Emit rejection; surface may notify/fail visibly if needed |

### 2. Handoff / Callback Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Lost handoff | Handoff dispatched but never acknowledged | requester | Retry or reassign after timeout |
| Duplicate handoff / callback | Same handoff or callback delivered more than once | receiver | Dedup by `dedup_key`; second delivery is a no-op |
| Callback missing after task completion | Work completed but callback never received | completing owner / system | Retry callback; if persistent, block/escalate |
| Callback arrives after cancellation | Late callback for cancelled work | strategic owner | Reconcile; do not silently reopen cancelled work |
| Callback arrives after reassignment | Prior owner/executor returns late result after ownership moved | strategic owner | Reconcile against current authority; record late arrival |

### 3. Execution / Workflow Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Worker crash | Execution runtime terminates mid-task | task owner | Retry execution or reassign executor |
| Orphaned work | Task accepted but no progress events for defined period | task owner / James | Workflow timeout, prompt owner, escalate if needed |
| Partial tool failure | Some tool calls succeed, others fail | task owner | Block with explicit reason; decide retry or escalate |
| Incomplete artifact | Artifact produced but fails validation | task owner / reviewer | Return to `In Progress` with error |
| Status / ownership conflict | Durable state disagrees about current owner or status | James / MC | Use authoritative store, emit reconciliation event |

### 4. Reply Routing / Publication Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| Stale or missing reply target | Stored reply destination is invalid | strategic owner / request-state path | Mark `fallback_required` or retarget explicitly |
| Publication failure after specialist success | Task is done but human reply was not published | strategic owner / request-state path | Retry / fallback / escalate |
| Ambiguous publication after retry | Outcome unknown; reply may or may not have been delivered | strategic owner / request-state path | Mark `unknown`; reconcile before further publish |
| Publish acknowledgement missing | Publish attempt started but terminal result never confirmed | request-state path | Mark `attempted` or `unknown`; bounded retry or reconcile |
| Late publish success after ambiguity | Prior ambiguous attempt later proves successful | request-state path | Reconcile state; avoid duplicate publication |
| Fallback invocation required | Primary target no longer safe/valid | strategic owner / operator | Apply approved fallback or escalate |

### 5. Conversation Continuity Failures

| Failure | Description | Recovery owner | Default action |
|---------|-------------|----------------|----------------|
| User follow-up while work is in flight | New message arrives before prior request closes | strategic owner | New request by default; explicitly merge if needed |
| Cross-surface continuation | Same human continues on another surface | strategic owner | Create new request or explicit transfer/merge decision |
| Reply target mutated implicitly | Target changed by side effect or convenience logic | strategic owner / operator | Reject implicit mutation; require explicit audit event |

---

## Dedup Domains

Idempotency is domain-specific. The runtime must distinguish:

| Domain | Protected by |
|-------|---------------|
| inbound request normalization | request-level dedup identity |
| handoff / callback processing | message `dedup_key` |
| reply publication | `publish_dedup_key` |

Using one generic dedup story across all three domains creates bugs.

---

## Timeout Types

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

## Timeout Decision Table

| Scenario | Timeout type | Default action |
|----------|--------------|----------------|
| Execution runtime unresponsive | Execution | Retry execution |
| Task accepted, no work started | Workflow | Notify owner |
| Task in progress, no events for >N | Workflow | Notify owner; escalate if no response |
| Handoff not accepted within window | Workflow | Retry or reassign |
| Callback not received after completion | Delivery / workflow | Retry callback |
| Publish attempt has no terminal result | Publication | Reconcile, bounded retry, or fallback |

---

## Recovery Paths

### Retry
Used when:
- failure is transient
- idempotency is guaranteed
- no strategic routing/content decision is required

For publication, mechanical retry must reuse the same `publish_dedup_key`.

### Reassign
Used when:
- original owner/executor is unresponsive or unavailable
- execution runtime failed and cannot be resumed
- explicit rejection has occurred

Reassignment requires a new acceptance handoff. Prior ownership must be explicitly closed.

### Reconcile
Used when:
- late-arriving signals conflict with the currently believed state
- publication outcome is ambiguous
- callback or publish result arrives after cancellation/reassignment

Reconciliation must preserve the audit trail and must not silently duplicate human-visible output.

### Escalate
Used when:
- retry/reassign/reconcile do not converge
- a quality/scope deadlock exists
- fallback requires policy or operator approval
- publication remains unresolved beyond the allowed window

Escalation sends the full context to James (or operator path when required).

### Mark Blocked
Used when:
- external input is required
- no safe automated recovery exists yet
- work should not be cancelled, but must not proceed silently

A blocked request/task always needs an explicit recovery owner.

---

## Compensation and Terminal States

| State | Type | Meaning |
|-------|------|---------|
| `Done` | Terminal for task | Execution work complete |
| `Cancelled` | Terminal | Explicitly terminated |
| `Blocked` | Near-terminal | Cannot proceed; awaiting external resolution |
| `Escalated` | Near-terminal | James is active recovery owner |
| `published` | Terminal for reply intent | Human-visible reply confirmed |
| `abandoned` | Terminal for reply intent | Reply will not be attempted further |
| `unknown` | Near-terminal / reconcile-required | Publish result ambiguous |
| `fallback_required` | Near-terminal / decision-required | Primary path invalid; explicit choice needed |

A task may be `Done` while the request-level reply/publication path is still not terminal.
That is valid and must be observable.

---

## Minimum Reconciliation Expectations

The system should define reconciliation behavior for at least:
- callback after cancellation
- callback after reassignment
- publish success after retry ambiguity
- duplicate publish ack / duplicate publish failure signal
- cross-surface follow-up arriving before prior request closure

The minimum acceptable behavior is not “be clever”.
It is:
- preserve audit trail,
- avoid silent duplication,
- keep one authoritative current state,
- escalate when policy or human judgment is required.