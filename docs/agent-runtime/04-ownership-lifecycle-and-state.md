# 04 — Ownership, Lifecycle, and State

## Ownership Model

Every task and flow explicitly stores:

| Field | Meaning |
|-------|---------|
| `owner` | Agent currently responsible for progress |
| `requester` | Agent or user who initiated the work |
| `executor` | Optional runtime or worker performing execution |
| `callback_target` | Where the result must be returned |
| `status` | Canonical current state |

Ownership must not be inferred from chat context. It is a first-class field.

## Final Accountability vs Execution Ownership

The system maintains a deliberate split:

| Type | Holder | Meaning |
|------|--------|---------|
| **Final accountability** | James | Responsible for outcome toward the user |
| **Execution ownership** | Specialist agent | Responsible within their domain |

In practice:
- **James** owns the strategic conversation, delegation, and final outcome toward the user
- **Alex** owns research tasks
- **Naomi** owns implementation tasks and the execution plan in the dev flow
- **Amos** owns quality, review, and verify

Delegation does not transfer final accountability from James. It transfers execution ownership
to the specialist for the scope of that task.

## Canonical Task Lifecycle

```
Created → Accepted → In Progress → Review → Verify → Done
                                                    ↓
                                             Blocked | Escalated | Cancelled
```

| Status | Meaning |
|--------|---------|
| `Created` | Task exists, not yet assigned or acknowledged |
| `Accepted` | Receiving agent has explicitly taken ownership |
| `In Progress` | Active work is underway |
| `Review` | Work submitted for review (code review, peer check) |
| `Verify` | Work submitted for functional verification |
| `Done` | Work complete, accepted, callback sent |
| `Blocked` | Progress impossible; explicit reason required |
| `Escalated` | Deadlock or repeated failure; escalated to senior owner |
| `Cancelled` | Explicitly terminated; artifacts may still exist |

## Status Transition Table

| Current Status | Action | Next Status | Allowed Actor | Notes |
|---------------|--------|-------------|---------------|-------|
| `Created` | assign | `Created` (pending acceptance) | requester | Handoff dispatched |
| `Created` | accept | `Accepted` | owner | Explicit acknowledgment |
| `Created` | reject | `Created` (returned) | assignee | Reason required; ownership reverts |
| `Accepted` | begin work | `In Progress` | owner | |
| `In Progress` | submit for review | `Review` | owner | Artifact required |
| `In Progress` | block | `Blocked` | owner | Reason required |
| `Review` | approve | `Verify` or `Done` | reviewer | Depends on flow type |
| `Review` | return with comments | `In Progress` | reviewer | Reason and comments required |
| `Verify` | pass | `Done` | verifier | Callback sent |
| `Verify` | fail | `In Progress` | verifier | Reason and comments required |
| `Blocked` | unblock | `In Progress` | owner or James | |
| `Blocked` | escalate | `Escalated` | owner or James | After defined threshold |
| `Escalated` | resolve | `In Progress` or `Done` | James | |
| `Any` | cancel | `Cancelled` | requester or James | |

## Acceptance Semantics

A task is not owned until explicitly accepted. Between dispatch and acceptance:
- the requester retains accountability
- the assignee has no obligation to begin work
- timeout on acceptance triggers a retry or reassignment (see [08-failure-recovery-and-timeouts.md](08-failure-recovery-and-timeouts.md))

An agent that accepts a task must:
- emit an `accepted` event with a timestamp
- set the task status to `Accepted`
- optionally confirm the definition of done and deadline

## Escalation Rules

Escalation is not automatic retry. Escalation means a deadlock, repeated failure,
or quality/scope conflict that cannot be resolved at the specialist level.

Escalation triggers:
- code review loop exceeded 3 returns (`review_loop.limit_reached`)
- verify loop exceeded 2 failures (`verify_loop.limit_reached`)
- blocked task with no resolution path for a defined period
- ownership conflict between agents
- definition-of-done disagreement not resolvable between owner and reviewer

On escalation:
- James receives an `escalation-event` with full context: task reference, failure reason,
  prior recovery attempts, partial artifacts, and loop history
- The task status moves to `Escalated`
- James decides: scope change, priority change, cancellation, or direct resolution
- James must emit a resolution event; the task must not remain in `Escalated` indefinitely

## Rejection Loop Policy

An assignee may reject a handoff. This reverts ownership to the requester.

| Rejection count | Action |
|----------------|--------|
| 1st rejection | Requester may retry with revised goal or different assignee |
| 2nd rejection | Requester must escalate to James |
| James rejected | James escalates to human operator |

A rejected handoff requires an explicit reason. The requester must address the reason
before retrying; retrying with an identical handoff after rejection is not allowed.

## Concurrent Work and Capacity

Agents process tasks sequentially by default. If an agent already owns an active task
in `In Progress`, a new handoff is queued pending completion or explicit override.

For Amos: `Verify` takes priority over `Code Review` to prevent Done-blocking.

James must not dispatch multiple high-priority US assignments to Naomi simultaneously
without acknowledging the queue. If Naomi's queue is non-empty, James should receive
a capacity signal before dispatching additional work.

## Execution Timeout vs Workflow Timeout

These are distinct concepts:

| Type | Meaning | Handler |
|------|---------|---------|
| **Execution timeout** | Runtime or worker has not responded within expected execution time | Runtime recovery: retry, reassign executor |
| **Workflow timeout** | Expected progress in the process has not occurred | Workflow recovery: escalate, reassign owner, block |

An execution timeout at the Claude Code level does not automatically become a workflow
timeout. The runtime may retry the execution. Only if the task has not advanced after
a defined number of retries or a workflow-level deadline does it escalate to James.

## Who Can Change What

| Action | Allowed Actor |
|--------|--------------|
| Assign task | requester, James |
| Accept task | designated owner |
| Reject task | designated owner |
| Begin work | owner |
| Submit for review | owner |
| Approve review | Amos |
| Return with comments | Amos |
| Submit for verify | Amos (after review) |
| Pass verify | Amos |
| Fail verify | Amos |
| Block task | owner |
| Escalate | owner, James |
| Resolve escalation | James |
| Cancel task | requester, James |
| Override status | James only |
