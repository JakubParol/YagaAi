# 06 — Mission Control Model

## What Mission Control Is

Mission Control (MC) is the first domain implementation of the generic Agent Runtime model.
It is a privileged operational layer for the development workflow.

The core runtime defines universal primitives: agent, session, task, flow, status, memory,
event, and artifact. Mission Control is the first specialization of those primitives for
the concrete development workflow: user stories, tasks, code review, verify, and escalation.

MC is not an architectural exception. It is proof that the generic model works for a
real domain.

## Relation to the Runtime

| Aspect | Generic Runtime | Mission Control |
|--------|----------------|-----------------|
| Work unit | task | task + user story (US) |
| Flow | flow | US lifecycle |
| Artifact | artifact | PR, test report, review comments |
| Status | canonical statuses | US-specific statuses |
| Callback | callback event | assignment / status event |
| Orchestration | event routing | active state machine for dev flow |

MC acts as the active orchestrator and state machine for status transitions within the
development workflow. It enforces process rules (review loop limits, escalation thresholds)
that would otherwise require James to monitor manually.

## Generic → Mission Control Mapping

| Generic primitive | MC specialization |
|------------------|------------------|
| `flow` | User Story (US) lifecycle |
| `task` | MC task under a US |
| `artifact` | PR reference, test result, review comment set, evidence |
| `handoff` | Assignment event with owner, status, and callback |
| `status` | `In Progress`, `Code Review`, `Verify`, `Done`, `Blocked`, `Escalated` |
| `callback` | Assignment or status-change event to James or Naomi |

## Source of Truth

Mission Control is the source of truth for workflow state in the development flow.

| What | Source of Truth in dev flow |
|------|----------------------------|
| US status | Mission Control |
| Task status under a US | Mission Control |
| Who owns the US | Mission Control |
| Review loop count | Mission Control |
| Verify outcome | Mission Control |
| Execution trace | Event log |
| Agent knowledge | Agent memory store |

Agents do not maintain their own copy of US state. They query Mission Control for
current ownership and status, and emit events when they produce outcomes.

## Agent Ownership vs MC Orchestration

This boundary matters:

| Domain | Owner |
|--------|-------|
| What the agent decides to do | Agent |
| Whether the agent is allowed to make a transition | Mission Control |
| The current state of the US | Mission Control |
| Memory and knowledge of the agent | Agent |

MC may reject a transition if it violates process rules (e.g., moving to Done without
a passed verify). Agents do not bypass MC to update workflow state directly.

## US Lifecycle

```
Created → In Progress → Code Review → Verify → Done
                ↓              ↓          ↓
             Blocked      In Progress  In Progress
                              (Amos → Naomi)  (Amos → Naomi)
                ↓
           Escalated → (James resolves)
```

Key rules:
- A US moves to `Code Review` when Naomi submits it, assigned to Amos
- A US returns to `In Progress` when Amos has comments, reassigned to Naomi
- Code review loop is capped: max 3 returns (`review_loop.limit_reached` → escalate)
- A US moves to `Verify` when Amos approves code review
- A US returns to `In Progress` from `Verify` if Amos finds a problem
- Verify loop is capped: max 2 failures (`verify_loop.limit_reached` → escalate)
- A US moves to `Done` only when Amos passes verify

## MC Task Lifecycle

Tasks are execution units under a US. They are created by Naomi as part of the
implementation plan.

```
Created → In Progress → Done
               ↓
            Blocked → Escalated
```

Each task has:
- a parent US reference
- an owner (Naomi by default during implementation)
- a status
- optional artifacts

When all tasks under a US are `Done`, Naomi may submit the US to `Code Review`.
If any task is `Blocked` without a resolution path, the US may be moved to `Blocked`.

## James' Role in the Dev Flow

James delegates implementation to Naomi via a US assignment. After that:
- MC tracks state
- Naomi owns execution
- Amos owns quality gates

James is notified via explicit callback or event when:
- a US is submitted for code review (by Naomi)
- a US escalates (review loop exceeded, verify deadlock, blocking issue)
- a US completes (Done)

James does not need to poll MC state. Events and callbacks are the notification mechanism.

## Transition Protocol

This is the authoritative answer to "who changes status — agent or MC?":

1. Agent emits an **intent event** (e.g., `task.completed`, `review.submitted`, `verify.passed`)
2. MC validates the transition against process rules
3. If valid: MC updates the US/task state, emits a `status.changed` event
4. If invalid: MC emits `transition.rejected` with a reason; the agent receives it and
   must not assume the transition occurred

Agents do not update workflow state directly. MC is the only writer to US and task status.
Agents are the source of intent; MC is the authority on whether that intent is allowed.

This means:
- "Naomi submits to Code Review" = Naomi emits `review.submitted` → MC validates → MC sets status
- "Amos approves" = Amos emits `review.approved` → MC validates → MC sets status to Verify
- "Amos passes verify" = Amos emits `verify.passed` → MC validates → MC sets status to Done + emits callback
