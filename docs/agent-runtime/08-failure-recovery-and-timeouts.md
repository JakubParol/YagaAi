# 08 — Failure, Recovery, and Timeouts

## Design Principle

The system must be designed for more than the happy path. Failures are not edge cases —
they are expected operational events that require defined handling.

For every failure mode, the system must have:
- a **recovery owner** (who is responsible for resolving it)
- a **default action** (retry / reassign / escalate / mark blocked)
- an **explicit terminal state** or compensation path

## Failure Categories

### 1. Delivery Failures

| Failure | Description | Default Action |
|---------|-------------|----------------|
| Missing callback | Task completed but callback never received | Retry callback; if persistent, mark task as `Blocked` and notify James |
| Duplicate event | Same event delivered more than once | Idempotent processing via `dedup_key`; second delivery is a no-op |
| Out-of-order delivery | Events arrive in wrong sequence | Buffer and reorder using `causation_id`; if unresolvable, emit an ordering-error event |
| Lost handoff | Handoff dispatched but never acknowledged | Retry after timeout; if no response, reassign or escalate |

### 2. Execution Failures

| Failure | Description | Default Action |
|---------|-------------|----------------|
| Worker crash | Execution runtime terminates mid-task | Reassign to a new execution; resume from last known checkpoint if available |
| Orphaned work | Task accepted but no progress events for defined period | Workflow timeout triggered; owner notified; escalate if unresponsive |
| Partial tool failure | Some tool calls succeed, others fail | Task moves to `Blocked` with partial artifact; owner decides retry or escalate |
| Incomplete artifact | Artifact produced but fails validation | Task returns to `In Progress`; owner notified with validation error |

### 3. State Failures

| Failure | Description | Default Action |
|---------|-------------|----------------|
| Ownership conflict | Two agents claim ownership of the same task | James resolves; one ownership record is authoritative |
| Status conflict | Task store and event log disagree on current state | Task store is authoritative; reconciliation event emitted |
| Accepted task with no progress | Task accepted, status never moved to `In Progress` | Workflow timeout; owner prompted; escalate if no response |
| Stale ownership | Previous owner no longer responsive or available | James reassigns; prior ownership is explicitly closed |

### 4. Side-Effect Failures

| Failure | Description | Default Action |
|---------|-------------|----------------|
| Side effect completed without confirmation | Execution runtime performed an action (commit, API call) but no callback received | Verify via artifact or event; mark as `Blocked (unconfirmed)` pending verification |
| Partial commit | Some changes applied, others not | Block US; Naomi performs reconciliation before resuming |

## Timeout Types

Execution timeout and workflow timeout are distinct and must not be conflated.

### Execution Timeout

- **Definition:** The execution runtime or worker has not responded within the expected execution window
- **Scope:** Runtime level
- **Handler:** Runtime recovery — retry the execution, optionally with a new worker
- **Does not automatically escalate** to workflow level until retries are exhausted

### Workflow Timeout (SLA Timeout)

- **Definition:** Expected progress in the process has not occurred within a defined business window
- **Scope:** Task / flow level
- **Handler:** Workflow recovery — notify owner, prompt for update, escalate if no response
- **Examples:** Task accepted but no `In Progress` within 1h; US in `Code Review` for >24h with no action

### Timeout Decision Table

| Scenario | Timeout Type | Default Action |
|----------|-------------|----------------|
| Execution runtime unresponsive | Execution | Retry execution |
| Task accepted, no work started | Workflow | Notify owner |
| Task in progress, no events for >N | Workflow | Notify owner; escalate if no response |
| Callback not received after completion | Delivery | Retry callback |
| Handoff not accepted within window | Workflow | Retry or reassign |

## Recovery Paths

### Retry

Used when:
- the failure is transient (network, runtime restart)
- idempotency is guaranteed
- the task has not reached a blocking state

Retry must use the original `dedup_key` to prevent duplicate side effects.

### Reassign

Used when:
- the original owner is unresponsive or unavailable
- the execution runtime failed and cannot be resumed
- explicit rejection has occurred

Reassignment requires a new acceptance handoff. The prior owner's task record is
explicitly closed.

### Escalate

Used when:
- retry and reassignment have been attempted and failed
- a quality or scope deadlock exists (loop limit exceeded)
- ownership cannot be determined
- side-effect state is uncertain

Escalation sends an `escalation-event` to James with full context: task reference,
failure reason, prior recovery attempts, and any partial artifacts.

### Mark Blocked

Used when:
- the failure requires human or external input before work can continue
- the recovery path is unclear but the task should not be cancelled

A `Blocked` task has an explicit reason and a designated recovery owner. It is not
a silent failure state.

## Compensation and Terminal States

Every failure path must reach a defined state. Terminal states are truly final;
near-terminal states require active recovery but have defined exit paths.

| State | Type | Meaning |
|-------|------|---------|
| `Done` | Terminal | Nominal completion; no further transitions |
| `Cancelled` | Terminal | Explicitly terminated; no further transitions |
| `Blocked` | Near-terminal | Cannot proceed; awaiting external resolution; exits to `In Progress` or `Escalated` |
| `Escalated` | Near-terminal | James is the active recovery owner; exits to `In Progress`, `Done`, or `Cancelled` |

`Blocked` is not a terminal state. A task in `Blocked` must have an explicit recovery
owner and a designated path to resolution. A `Blocked` task that does not receive
attention within a defined window should auto-escalate to `Escalated`.

A task must never be in an ambiguous non-terminal state indefinitely. The system
should be designed to force failed tasks toward a terminal state or into `Blocked`
with an explicit recovery action within a defined window.
