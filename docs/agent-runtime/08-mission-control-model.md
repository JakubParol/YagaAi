# 08 — Mission Control Model

## What Mission Control Is

Mission Control (MC) is the first domain implementation of the generic Agent Runtime model.
It is the privileged operational layer for the development workflow.
It is also a built-in management/admin/configuration surface through the runtime’s Web UI host, while remaining reachable through both API and CLI.

The core runtime defines universal primitives: agent, session, request, task, flow,
status, memory, event, and artifact. Mission Control specializes those primitives for
the concrete development workflow: user stories, tasks, code review, verify, and escalation.

MC is not an architectural exception. It is proof that the generic model works for a
real domain.

## Relation to the Runtime

| Aspect | Generic Runtime | Mission Control |
|--------|----------------|-----------------|
| User-originated ingress | request record | linked, but not owned by MC |
| Work unit | task | task + user story (US) |
| Flow | flow | US lifecycle |
| Artifact | artifact | PR, test report, review comments |
| Status | canonical task statuses | US-specific workflow statuses |
| Callback | callback event | assignment / status / terminal outcome events |
| Orchestration | event routing + owner coordination | active state machine for dev flow |
| Operator surface | runtime Web UI host | admin, management, planning, and runtime views |
| Programmatic interface | local API | first-class API and CLI contracts |

## Source-of-Truth Boundary

Mission Control is the source of truth for workflow state in the development flow.
It is **not** the source of truth for request routing, terminal strategic callback authority,
or human reply publication.

| What | Source of Truth in dev flow |
|------|----------------------------|
| Request routing + publication state | request record |
| Strategic callback destination for user-originated request outcomes | owner main path / request contract |
| US status | Mission Control |
| Task status under a US | Mission Control |
| Who owns the US / task | Mission Control |
| Review loop count | Mission Control |
| Verify outcome | Mission Control |
| Execution trace | event log |
| Agent knowledge | agent memory store |

MC and the request record must not compete as sources of truth for the same concern.

## Agent Ownership vs MC Orchestration

This boundary matters:

| Domain | Owner |
|--------|-------|
| What the agent decides to do | agent |
| Whether a workflow transition is allowed | Mission Control |
| Current US/task workflow state | Mission Control |
| Request routing / publication state | request record |
| Strategic callback authority for user-originated requests | delegating owner main path |
| Agent memory and knowledge | agent |

MC may reject a transition if it violates process rules. Agents do not bypass MC to update
workflow state directly.

### CLI and API stance

Mission Control must be usable through both:
- **API** — for UI, integrations, and external automation
- **CLI** — for agents and operators doing structured operational work

This is not a convenience detail. In practice, agents will often find CLI interaction simpler,
safer, and more robust than low-level API choreography.

## Generic → Mission Control Mapping

| Generic primitive | MC specialization |
|------------------|------------------|
| `request` | user-originated ingress linked to the dev flow |
| `flow` | User Story (US) lifecycle |
| `task` | MC task under a US |
| `artifact` | PR reference, test result, review comment set, evidence |
| `handoff` | Assignment event with owner, callback, and status intent |
| `status` | `In Progress`, `Code Review`, `Verify`, `Done`, `Blocked`, `Escalated` |
| `callback` | terminal or loop-return event back to Naomi / James |

## US Lifecycle

```text
Created → In Progress → Code Review → Verify → Done
                ↓              ↓          ↓
             Blocked      In Progress  In Progress
                ↓
           Escalated → (James resolves)
```

Key rules:
- a US moves to `Code Review` when Naomi submits it, assigned to Amos
- a US returns to `In Progress` when Amos has comments, reassigned to Naomi
- code review loop is capped: max 3 returns
- a US moves to `Verify` when Amos approves code review
- a US returns to `In Progress` from `Verify` if Amos finds a problem
- verify loop is capped: max 2 failures
- a US moves to `Done` only when Amos passes verify

## MC Task Lifecycle

Tasks are execution units under a US.

```text
Created → Accepted → In Progress → Done
               ↓
            Blocked → Escalated
```

Each task has:
- a parent US reference
- an owner
- a status
- optional artifacts

When all tasks under a US are `Done`, Naomi may submit the US to `Code Review`.

## James' Role in the Dev Flow

James delegates implementation to Naomi via a US assignment. After that:
- MC tracks workflow state
- Naomi owns execution
- Amos owns review / verify quality gates
- the request record still owns durable reply-routing/publication truth

### Terminal callback authority in the dev flow

Mission Control is **not** the strategic owner and is **not** the durable callback/publication authority for user-originated requests.

The authoritative v1 rule is:
- **terminal execution callback authority remains the delegating owner main path (`agent:main:main`)**
- MC may emit terminal workflow events (`Done`, escalation, transition results)
- those MC events may inform or trigger owner-side callback/publication handling
- but MC is not the durable callback target of record for the user-originated request

In short:
- MC is the authoritative writer of dev workflow state
- James main is the authoritative strategic callback destination for terminal dev-flow outcomes toward the request
- the built-in Web UI host is the main operator/admin/configuration surface over this state, not a separate source of truth

James is notified via explicit callback or event when:
- a US is submitted for code review (if configured)
- a US escalates
- a US completes (`Done`)

Those notifications inform James' reply decision, but do not themselves make publication truth authoritative.

## Transition Protocol

1. Agent emits an **intent event** (for example `review.submitted`, `verify.passed`)
2. MC validates the transition against process rules
3. If valid: MC updates the US/task state and emits status/flow events
4. If invalid: MC emits `transition.rejected` with a reason

Agents do not update workflow state directly.
MC is the only writer to US and task status in the dev flow.

MC may additionally expose index/memory health and project context views, but those remain read models over runtime-owned retrieval/indexing services rather than separate MC-owned storage authorities.

## Relation to Request Closure

A US reaching `Done` is an execution/workflow truth.
It may inform the final user-facing reply, but it does **not** mean the originating request
is closed. The request closes only when the intended human-visible publication succeeds,
is abandoned, or is superseded by authorized fallback.

A lost or late MC terminal event is therefore a workflow/callback recovery concern,
not a reason to treat MC as the durable owner of the request outcome.