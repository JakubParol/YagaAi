# 05 — Ownership, Lifecycle, and State

## Ownership Model

The runtime has to keep three ownership ideas distinct:

| Field / concept | Meaning | Authoritative source |
|-------|---------|----------------------|
| `strategic_owner_agent_id` | Agent accountable for the request as a whole | request record |
| task / US `owner` | Agent currently responsible for execution progress | task store / Mission Control |
| `callback_target` | Where execution results return operationally | handoff / task contract |
| `reply_target` | Where the human-visible reply should be published | request record |

Ownership must not be inferred from chat context. It is first-class, durable metadata.

## Final Accountability vs Execution Ownership

The system maintains a deliberate split:

| Type | Holder | Meaning |
|------|--------|---------|
| **Final accountability / strategic ownership** | James (usually) | Responsible for outcome toward the user |
| **Execution ownership** | Specialist agent | Responsible for delegated work within their domain |

In practice:
- **James** owns the strategic conversation, delegation, request continuity, and final human-facing outcome
- **Alex** owns research tasks
- **Naomi** owns implementation tasks and dev execution
- **Amos** owns review / verify quality gates

Delegation does not transfer final accountability from James. It transfers execution ownership
for a bounded scope of work.

## Callback Target vs Reply Target

These are different concepts and must stay different:

| Concept | Meaning |
|--------|---------|
| `callback_target` | Where specialist results return operationally |
| `reply_target` | Where the human-visible response should be published |

A task may be `Done` and callback may be successful while human reply publication is still:
- pending
- failed
- unknown
- awaiting fallback

That is expected. It is not an inconsistency.

## Canonical Task Lifecycle

```text
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
| `Done` | Execution work complete; callback obligations satisfied |
| `Blocked` | Progress impossible; explicit reason required |
| `Escalated` | Deadlock or repeated failure; escalated to senior owner |
| `Cancelled` | Explicitly terminated; artifacts may still exist |

### Important clarification

`Done` means the execution work reached its terminal success state.
It does **not** mean the intended human-visible reply has already been published.

## Request-Level Projection vs Task Status

Request/publication projection labels are not canonical task statuses.
They are a separate operational view over the request record.

A practical request-level projection may include labels such as:
- `normalized`
- `delegated`
- `awaiting_callback`
- `reply_publish_pending`
- `reply_published`
- `reply_publish_failed`
- `fallback_required`

These are useful operator-facing projections, not task lifecycle states.

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
| `Verify` | pass | `Done` | verifier | Execution work accepted |
| `Verify` | fail | `In Progress` | verifier | Reason and comments required |
| `Blocked` | unblock | `In Progress` | owner or James | |
| `Blocked` | escalate | `Escalated` | owner or James | After threshold |
| `Escalated` | resolve | `In Progress` or `Done` | James | |
| `Any` | cancel | `Cancelled` | requester or James | |

## Acceptance Semantics

A task is not execution-owned until explicitly accepted. Between dispatch and acceptance:
- the requester retains accountability
- the assignee has no obligation to begin work
- timeout on acceptance triggers retry or reassignment (see [10-failure-recovery-and-timeouts.md](10-failure-recovery-and-timeouts.md))

An accepted task must produce an explicit acceptance event and status change.

## Request Closure Rule

A **durable request** is not operationally closed until one of the following is true:
1. the intended human-visible publication succeeded,
2. the request was explicitly abandoned,
3. an authorized fallback outcome superseded the primary publish path.

This closure rule lives above task `Done`.

## Escalation Rules

Escalation is not automatic retry. Escalation means a deadlock, repeated failure,
or quality/scope conflict that cannot be resolved at the specialist level.

Escalation triggers include:
- code review loop exceeded 3 returns (`review_loop.limit_reached`)
- verify loop exceeded 2 failures (`verify_loop.limit_reached`)
- blocked task with no resolution path for a defined period
- ownership conflict between agents
- definition-of-done disagreement not resolvable between owner and reviewer
- unresolved publish failure or fallback requirement on a user-visible request

On escalation:
- James receives the escalation context
- the task/US status moves to `Escalated` when applicable
- the request may remain operationally open until publication or abandonment is resolved

## Rejection Loop Policy

An assignee may reject a handoff. This reverts execution ownership to the requester.

| Rejection count | Action |
|----------------|--------|
| 1st rejection | Requester may retry with revised goal or different assignee |
| 2nd rejection | Requester must escalate to James |
| James rejected | James escalates to human operator |

A rejected handoff requires an explicit reason. The requester must address the reason
before retrying.

## Concurrent Work and Capacity

Agents process tasks sequentially by default. If an agent already owns an active task
in `In Progress`, new work is queued pending completion or explicit override.

For Amos: `Verify` takes priority over `Code Review` to prevent Done-blocking.

James must not dispatch multiple high-priority US assignments to Naomi simultaneously
without acknowledging the queue.

## Execution Timeout vs Workflow Timeout

These are distinct concepts:

| Type | Meaning | Handler |
|------|---------|---------|
| **Execution timeout** | Runtime or worker has not responded within expected execution time | Runtime recovery: retry, reassign executor |
| **Workflow timeout** | Expected progress in the process has not occurred | Workflow recovery: escalate, reassign owner, block |
| **Publication timeout / ambiguity** | Human-visible publication did not complete or outcome is unknown | Request/publication recovery: retry, reconcile, fallback, escalate |

An execution timeout at the runtime level does not automatically become a workflow timeout.
A task may be done while publication remains unresolved.

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
| Change reply target | strategic owner / approved runtime path |
| Declare request abandoned | strategic owner / operator |
| Override status | James only |

Specialists do not become owners of human-visible reply routing by default.