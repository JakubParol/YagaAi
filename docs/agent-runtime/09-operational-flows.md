# 09 — Operational Flows

## Common Invariants

These apply to all durable flows:

- surface/channel sessions are ingress/egress adapters, not durable owners
- durable user-originated work normalizes through the strategic owner's `main`
- handoffs complete on `accepted` or `rejected`
- tasks carry execution lifecycle
- callbacks return execution results
- publication is a separate concern from task completion
- retries, watchdogs, and stale-work recovery belong to the runtime
- planning systems may trigger or reflect work, but runtime execution semantics remain runtime-owned

---

## Research Flow (User-Originated)

**Goal:** Produce a research artifact answering a user's question or hypothesis.

**Trigger:** User asks James for research through a surface/channel session.

**Participants:** User, James surface session, James main, Alex main

**Source of truth:**
- request routing/publication state → request record
- execution state → runtime task/handoff/callback path

### Main steps
1. User sends research request on a surface session.
2. The surface adapter creates/updates the request record and normalizes the request into `agent:main:main`.
3. James main decides the work is durable and delegates to `agent:alex:main`.
4. Alex accepts the handoff.
5. Alex performs research and produces result artifacts.
6. Alex sends a callback to `agent:main:main`.
7. James main reviews the result and decides the user-facing answer.
8. James main creates a publish intent and routes publication through the stored reply target.
9. The surface adapter publishes and reports the outcome.

### State shape

```text
request: received → normalized → delegated → awaiting_callback → reply_pending → reply_published → closed

handoff: dispatched → accepted | rejected

task: Created → Accepted → In Progress → Done
```

### Escalation path
- Alex blocked → callback / escalation to James
- publish failure after research success → runtime retry / fallback / escalate path

---

## Development Flow (Runtime Core)

**Goal:** Carry a development work item from assignment into implementation, review, verify, and terminal outcome.

**Trigger:** James starts development work directly, or a planning integration emits a start/assignment intent.

**Participants:** James main, Naomi main, Amos main, optional planning system

**Source of truth:**
- runtime execution semantics → runtime
- planning/work-item state → planning integration when present
- request/publication state → request record when user-originated

### Main steps
1. James decides a development flow should start.
2. If a planning system exists, the relevant work item is already visible there or is created there.
3. James assigns or delegates the work to Naomi.
4. Naomi explicitly accepts the work.
5. Naomi loads the work item, parent context such as epic when available, and repository context.
6. Naomi updates `main`, creates a branch, and plans the work.
7. If a planning system exists, Naomi records the plan as tasks there.
8. Naomi executes tasks sequentially.
9. If blocked, Naomi escalates to James.
10. After implementation tasks are complete, Naomi hands the work into code review.
11. Amos performs code review.
12. If review comments exist, work returns to Naomi for fixes.
13. Review loop limit is 3; on the 3rd return the work escalates.
14. If review passes, Amos performs verify.
15. If verify fails, work returns to Naomi for fixes.
16. Verify loop limit is 2 failures; on the 2nd failure the work escalates.
17. If verify passes, the work reaches terminal success (`Done`).

### State shape

```text
handoff: dispatched → accepted | rejected

task: Created → Accepted → In Progress → Review → Verify → Done

planning work item when present:
  TODO → IN_PROGRESS → CODE_REVIEW → VERIFY → DONE
  with loop-back to IN_PROGRESS and escalation on limits
```

### Notes
- Runtime and planning state are related but not identical.
- Planning status does not replace runtime watchdog/retry state.
- Runtime must still be able to execute this flow without any planning system present.

---

## Development Flow Through Mission Control

This is the first serious integrated version of the development flow, not the only possible one.

```text
story exists in MC and is eligible to be worked
  ↓
James assigns story to Naomi through mc cli
  ↓
runtime receives assignment/start intent
  ↓
Naomi accepts and loads story + epic context + repo context
  ↓
Naomi updates main, creates branch, and records tasks through mc cli
  ↓
Naomi executes tasks sequentially and updates task state through mc cli
  ↓
if blocked: escalate to James
  ↓
Naomi moves story to CODE_REVIEW
  ↓
Amos reviews
  ↓
loop back to Naomi for fixes, max 3 returns
  ↓
Amos verifies
  ↓
loop back for fixes, max 2 verify failures
  ↓
DONE or Escalated
```

What MC adds here:
- work-item visibility,
- backlog / sprint context,
- manual flow start and assignment surfaces,
- operator-facing control-plane visibility.

What runtime still owns:
- acceptance semantics,
- retries,
- watchdogs,
- stale-work detection,
- callback handling,
- execution truth.

---

## QA Loop Detail

### Code Review loop
1. Naomi submits the work to code review.
2. Amos reviews.
3. If approved, the work moves to verify.
4. If changes are required, the work returns to Naomi.
5. On the 3rd review return, emit `review_loop.limit_reached` and escalate.

### Verify loop
1. Amos verifies the reviewed work.
2. If passed, the work becomes `Done`.
3. If failed, the work returns to Naomi.
4. On the 2nd verify failure, emit `verify_loop.limit_reached` and escalate.

---

## Flow Format Summary

Each flow above separates:
- routing/publication truth,
- execution truth,
- optional planning-system state,
- and operator-facing visibility.

That separation is deliberate and must remain intact in implementation.
