# 07 — Operational Flows

## Common Invariants

These apply to all flows:

- Every task has an explicit owner, requester, and callback target before work begins
- Handoffs are not complete until accepted, rejected, or claimed
- Artifacts are the mechanism for passing work results between agents
- Callbacks are mandatory for detached tasks; fire-and-forget is not acceptable
- Status transitions are explicit and event-driven
- Escalation to James is the terminal path when a loop does not converge

---

## Research Flow

**Goal:** Produce a research artifact answering a user's question or hypothesis.

**Trigger:** User asks James for research.

**Participants:** User, James, Alex

**Source of truth:** Task store (task owned by Alex)

**Main steps:**
1. User sends research request to James
2. James creates a task and sends a handoff to Alex
3. Alex accepts the task
4. Alex performs research, stores relevant findings in memory
5. Alex produces a result artifact (report, synthesis, references)
6. Alex sends a callback to James with the artifact reference
7. James reviews the artifact
8. James may send a clarification handoff back to Alex (additional research sub-task)
9. James returns the final answer to the user

**State transitions:**
```
task: Created → Accepted (Alex) → In Progress → Done
```

**Artifacts:** Research report or synthesis document

**Callback path:** Alex → James (callback event with artifact reference)

**Escalation path:** If Alex is blocked (source unavailable, ambiguous scope), Alex
sends a blocked event to James with a reason. James clarifies scope or cancels.

---

## Implementation Flow

**Goal:** Implement a development task or user story.

**Trigger:** User asks James for a development task, or James assigns a US to Naomi.

**Participants:** User, James, Naomi, Amos (via QA flow)

**Source of truth:** Mission Control (for US and task state)

**Main steps:**
1. User requests a development task from James
2. James creates or identifies a US in Mission Control
3. James assigns the US to Naomi via handoff
4. Naomi accepts the US and sets it to `In Progress`
5. Naomi analyzes the US, creates a plan, stores tasks in MC
6. Naomi works through tasks using an execution runtime (Claude Code, Codex, ACP)
7. Naomi records execution trail and strengthens memory around her specialization
8. When all tasks are done, Naomi submits the US to `Code Review` and assigns Amos
9. James is notified via callback event

**State transitions:**
```
US: Created → In Progress (Naomi) → Code Review (Amos assigned) → [QA flow]
Tasks: Created → In Progress → Done (per task)
```

**Artifacts:** Code changes (PR or diff reference), execution log, implementation notes

**Callback path:** Naomi → James (after submission to Code Review)

**Escalation path:** If Naomi is blocked, she sets the task to `Blocked` with a reason.
James is notified. James resolves or changes scope.

---

## QA Flow

**Goal:** Review and verify work produced by Naomi before it is accepted as Done.

**Trigger:** Naomi submits a US to Code Review, assigned to Amos.

**Participants:** Naomi, Amos, James (on escalation)

**Source of truth:** Mission Control

**Main steps:**

### Code Review Loop

1. Amos receives the US in `Code Review` state
2. Amos performs code review against the definition of done
3. If approved: Amos moves the US to `Verify`
4. If comments: Amos adds comments, moves US back to `In Progress`, reassigns Naomi
5. Naomi fixes comments and resubmits to `Code Review`
6. Loop repeats up to **3 cycles**
7. If not resolved after 3 cycles: escalate to James

### Verify Loop

1. Amos receives the US in `Verify` state
2. Amos performs functional verification
3. If passed: Amos moves the US to `Done`; callback sent to James
4. If failed: Amos records comments, moves US back to `In Progress`, reassigns Naomi
5. Naomi fixes the issues and returns to review or verify as appropriate
6. If the verify loop does not converge: escalate to James

**State transitions:**
```
Code Review loop:
  Code Review (Amos) → In Progress (Naomi) → Code Review (Amos) [max 3x]
  Code Review (Amos) → Verify (Amos) [on approval]

Verify loop:
  Verify (Amos) → In Progress (Naomi) → Review/Verify (Amos) [until resolved]
  Verify (Amos) → Done [on pass]
```

**Artifacts:** Review comments, verify evidence, approval record

**Callback path (dual callback pattern):**
- Amos → Naomi: when returning with comments (`In Progress`, reassign Naomi)
- Amos → James: when the US reaches `Done` OR when escalation is triggered

These are two distinct callbacks. Naomi is the operational callback target for
loop returns. James is the strategic callback target for terminal outcomes.

**Escalation path:** After 3 code review cycles (`review_loop.limit_reached`) or
after 2 verify failures (`verify_loop.limit_reached`), MC emits an escalation event.
James receives it and decides: scope change, cancellation, or direct resolution.

---

## Development Flow Through Mission Control (Integrated View)

**Goal:** End-to-end view of a US moving from assignment to Done.

```
James assigns US to Naomi
  ↓
Naomi: In Progress
  ↓ (creates tasks, works through them)
Naomi: submits to Code Review → assigns Amos
  ↓
Amos: Code Review
  ↓ (approved)
Amos: Verify
  ↓ (passed)
US: Done → callback to James
  ↓
James: notifies user
```

At any point, the loop may cycle (Code Review → In Progress → Code Review) or escalate
(→ Escalated → James).

---

## Flow Format Summary

Each flow above follows this structure:
- **Goal** — what the flow is trying to achieve
- **Trigger** — what initiates it
- **Participants** — which agents are involved
- **Source of truth** — where state is authoritative
- **Main steps** — the nominal path
- **State transitions** — canonical status changes
- **Artifacts** — what is produced
- **Callback path** — how results return
- **Escalation path** — what happens when the nominal path fails
