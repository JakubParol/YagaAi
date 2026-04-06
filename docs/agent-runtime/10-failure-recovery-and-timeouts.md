# 10 — Failure, Recovery, and Timeouts

## Design Principle

Failures are expected operational events, not edge cases.

For every important failure mode, the system must define:
- a **recovery owner**
- a **default action**
- a **bounded retry / escalation path**
- an explicit terminal or near-terminal outcome

Recovery paths are Policies: automatic reactions to Domain Events with named owners and
bounded retry clauses. Each failure mode below has a corresponding named Policy in
[reference/policies.md](reference/policies.md) where one exists.

The channel session routing model (see [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md)) adds one important rule:

> **Task success, callback success, and human-visible publication success are separate recovery concerns.**

---

## Failure Categories

### 1. Inbound / Normalization Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Duplicate inbound normalization | Same inbound request normalized more than once | owner-side request path | Dedup by request-level key; no duplicate work | — |
| Adapter failure before durable acceptance | Surface adapter received the message but owner path did not durably accept it | surface adapter | Retry normalization with same dedup identity | `RetryNormalizationOnAdapterFailure` |
| Main endpoint unavailable during normalization | Owner-facing `main` path unreachable/unavailable | surface adapter / runtime | Retry until timeout policy, then escalate | `RetryNormalizationOnAdapterFailure` |
| Normalization rejected | Owner path explicitly rejects malformed or invalid request | owner-side runtime | Emit `command.rejected` Domain Event; surface may notify/fail visibly if needed | — |

### 2. Handoff / Callback Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Lost handoff | Handoff dispatched but never acknowledged | requester | Retry or reassign after timeout | `WatchAcceptanceTimeout` → `EscalateOnHandoffTimeout` |
| Duplicate handoff / callback | Same handoff or callback delivered more than once | receiver | Dedup by `dedup_key`; second delivery is a no-op | — |
| Callback missing after task completion | Work completed but callback never received | completing owner / system | Retry callback; if persistent, escalate callback recovery | `WatchCallbackTimeout` → `EscalateOnCallbackTimeout` |
| Callback arrives after cancellation | Late callback for cancelled work | strategic owner | Reconcile; do not silently reopen cancelled work | — |
| Callback arrives after reassignment | Prior owner/executor returns late result after ownership moved | strategic owner | Reconcile against current authority; record late arrival | — |

### 3. Execution / Workflow Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Worker crash | Execution runtime terminates mid-task | task owner | Retry execution or reassign executor | — |
| Execution stall / worker heartbeat loss | Runtime execution started but execution heartbeat/result is missing | runtime / task owner | Retry execution, optionally reassign executor | `WatchExecutionTimeout` → `RecoverOnExecutionTimeout` |
| Orphaned work (workflow inactivity) | Task accepted but no business progress events for defined period | task owner / James | Workflow timeout, prompt owner, escalate if needed | `WatchWorkflowInactivityTimeout` → `EscalateOnWorkflowTimeout` |
| Partial tool failure | Some tool calls succeed, others fail | task owner | Block with explicit reason; decide retry or escalate | — |
| Incomplete artifact | Artifact produced but fails validation | task owner / reviewer | Return to `In Progress` with error | — |
| Status / ownership conflict | Durable state disagrees about current owner or status | James / MC | Use authoritative store, emit reconciliation Domain Event | — |

### 4. Reply Routing / Publication Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| Stale or missing reply target | Stored reply destination is invalid | strategic owner / request-state path | Mark `fallback_required` or retarget explicitly | — |
| Publication failure after specialist success | Task is done but human reply was not published | strategic owner / request-state path | Retry / fallback / escalate | `RetryPublicationOnFailure` |
| Ambiguous publication after retry | Outcome unknown; reply may or may not have been delivered | strategic owner / request-state path | Mark `unknown`; reconcile before further publish | `WatchPublicationTimeout` → `InvokeFallbackOnPublicationTimeout` |
| Publish acknowledgement missing | Publish attempt started but terminal result never confirmed | request-state path | Mark `attempted` or `unknown`; bounded retry or reconcile | `WatchPublicationTimeout` → `InvokeFallbackOnPublicationTimeout` |
| Late publish success after ambiguity | Prior ambiguous attempt later proves successful | request-state path | Reconcile state; avoid duplicate publication | — |
| Fallback invocation required | Primary target no longer safe/valid | strategic owner / operator | Apply approved fallback or escalate | `InvokeFallbackOnPublicationTimeout` |

### 5. Conversation Continuity Failures

| Failure | Description | Recovery owner | Default action | Policy |
|---------|-------------|----------------|----------------|--------|
| User follow-up while work is in flight | New message arrives before prior request closes | strategic owner | New request by default; explicitly merge if needed | — |
| Cross-surface continuation | Same human continues on another surface | strategic owner | Create new request or explicit transfer/merge decision | — |
| Reply target mutated implicitly | Target changed by side effect or convenience logic | strategic owner / operator | Reject implicit mutation; require explicit audit Domain Event | — |

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
- **Event sequence:** `execution.started` → `watchdog.started` (`WatchExecutionTimeout` Policy) → `watchdog.fired` → `execution.timeout` → `RecoverOnExecutionTimeout` Policy → `RetryExecution` (or `ReassignExecutor`) Command

### Workflow Timeout (SLA Timeout)
- **Definition:** expected process progress has not occurred within a business window
- **Scope:** task / flow level
- **Handler:** notify owner, prompt, escalate if needed
- **Event sequence:** `task.accepted` → `watchdog.started` (`WatchWorkflowInactivityTimeout` Policy) → `watchdog.fired` → `workflow.timeout` → `EscalateOnWorkflowTimeout` Policy → `NotifyTaskOwner` → if unresolved → `EscalateToJames` Command

### Callback Delivery Timeout
- **Definition:** task completed, but callback acknowledgement from callback target is missing within the callback window
- **Scope:** callback delivery path (post-completion, pre-publication)
- **Handler:** retry callback delivery, then escalate to strategic owner
- **Event sequence:** `task.completed` → `watchdog.started` (`WatchCallbackTimeout` Policy) → `watchdog.fired` → `callback.timeout` → `EscalateOnCallbackTimeout` Policy → `RetryCallback` → if unresolved → `EscalateToStrategicOwner` Command

### Publication Timeout / Ambiguity Timeout
- **Definition:** a user-visible publish intent has no confirmed terminal outcome within policy window
- **Scope:** request/publication level
- **Handler:** bounded retry, reconciliation, fallback decision, or escalation
- **Event sequence:** `reply.publication_attempted` → `watchdog.started` (`WatchPublicationTimeout` Policy) → `watchdog.fired` → `InvokeFallbackOnPublicationTimeout` Policy → `InvokeReplyFallback` Command

## Timeout Decision Table

| Scenario | Timeout type | Default action |
|----------|--------------|----------------|
| Execution runtime unresponsive | Execution | Retry execution |
| Task accepted, no work started | Workflow | Notify owner |
| Task in progress, no events for >N | Workflow | Notify owner; escalate if no response |
| Handoff not accepted within window | Workflow | Retry or reassign |
| Callback not received after completion | Callback delivery | Retry callback; escalate if unresolved |
| Publish attempt has no terminal result | Publication | Reconcile, bounded retry, or fallback |

---

## Recovery Paths

### Retry
Implemented automatically by `RetryPublicationOnFailure` and `RetryNormalizationOnAdapterFailure` Policies. Manual retry applies when no named Policy covers the failure mode.

Used when:
- failure is transient
- idempotency is guaranteed
- no strategic routing/content decision is required

For publication, mechanical retry must reuse the same `publish_dedup_key`.

### Reassign
No named Policy — requires an explicit owner or operator decision after the current assignment is closed.

Used when:
- original owner/executor is unresponsive or unavailable
- execution runtime failed and cannot be resumed
- explicit rejection has occurred

Reassignment requires a new acceptance handoff. Prior ownership must be explicitly closed.

### Reconcile
No named Policy — requires explicit investigation and a decision. Triggered when late-arriving signals conflict with believed state.

Used when:
- late-arriving signals conflict with the currently believed state
- publication outcome is ambiguous
- callback or publish result arrives after cancellation/reassignment

Reconciliation must preserve the audit trail and must not silently duplicate human-visible output.

### Escalate
Implemented automatically by `EscalateOnHandoffTimeout`, `EscalateOnReviewLimitReached`, `EscalateOnVerifyLimitReached`, `EscalateOnWorkflowTimeout`, and `EscalateOnCallbackTimeout` Policies. Manual escalation applies when convergence fails despite automatic Policies firing.

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

### Escalate vs Block — Decision Rule

| Question | If YES → | If NO → |
|----------|----------|---------|
| Can the system make progress without human/operator input? | Escalate (James or operator can decide) | Block |
| Is there a quality or scope disagreement that requires judgment? | Escalate | — |
| Is the blocker external (third-party, environment, access)? | Block | — |
| Is the work safe to pause indefinitely? | Block | Escalate (time-bounded concern) |
| Has retry/reassign already failed at least once? | Escalate | Retry first |

**Key distinction:**
- **Escalate** means "a decision-maker needs to act now."
- **Block** means "we cannot proceed; a condition must be met before continuing."

A task that is escalated has an active recovery owner (James or operator).
A task that is blocked is paused, waiting for an external signal.
Escalated tasks should not stay escalated indefinitely — if the escalation itself is not resolved
within the workflow timeout, it becomes a blocked-escalation requiring operator intervention.

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
