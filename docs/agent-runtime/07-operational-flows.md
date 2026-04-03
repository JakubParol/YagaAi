# 07 — Operational Flows

## Common Invariants

These apply to all durable flows:

- Surface/channel sessions are ingress/egress adapters, not durable owners
- Durable user-originated work normalizes through the strategic owner’s `main` endpoint
- Every task has an explicit owner, requester, and callback target before work begins
- Handoffs are not complete until accepted or rejected
- Artifacts are the mechanism for passing work results between agents
- Callbacks are mandatory for detached tasks
- Task completion and human reply publication are separate observable steps
- Escalation to James is the terminal path when a loop does not converge

---

## Research Flow (User-Originated)

**Goal:** Produce a research artifact answering a user's question or hypothesis.

**Trigger:** User asks James for research through a surface/channel session.

**Participants:** User, James surface session, James main, Alex main

**Source of truth:**
- request routing/publication state → request record
- execution state → task store

### Main steps
1. User sends research request on a surface session.
2. The surface adapter creates/updates the request record and normalizes the request into `agent:main:main`.
3. James main decides the work is durable and delegates to `agent:alex:main`.
4. Alex accepts the handoff and performs research.
5. Alex produces a result artifact (report, synthesis, references).
6. Alex sends a callback to `agent:main:main` with the artifact reference.
7. James main reviews the artifact and decides the user-facing answer.
8. James main instructs the original surface path to publish the reply using the stored reply target.
9. The surface adapter publishes the reply and reports the outcome back to request state.

### State shape

```text
request: received → normalized → delegated → awaiting_callback → reply_publish_pending → reply_published

task: Created → Accepted (Alex) → In Progress → Done
```

### Callback path
Alex main → James main

### Human reply path
James main → stored reply target → publish-capable surface session

### Escalation path
If Alex is blocked, Alex sends a blocked event to James main.
If publication fails after research succeeds, the request remains operationally open until retry,
fallback, or abandonment is resolved.

---

## Implementation Flow (User-Originated)

**Goal:** Implement a development task or user story and return a human-visible outcome.

**Trigger:** User asks James for implementation help through a surface/channel session.

**Participants:** User, James surface session, James main, Naomi main, Amos main, Mission Control

**Source of truth:**
- request routing/publication state → request record
- US/task execution state → Mission Control

### Main steps
1. User sends implementation request on a surface session.
2. The surface adapter creates/updates the request record and normalizes the work into `agent:main:main`.
3. James main creates or identifies the relevant US and delegates implementation to `agent:naomi:main`.
4. Naomi accepts, plans, and executes the work.
5. Naomi drives task execution through Mission Control and code-execution runtime(s).
6. When implementation reaches the review point, Naomi submits to Code Review / Verify flow.
7. Terminal execution callbacks return to James main (directly or through MC-triggered terminal events).
8. James main decides the human-visible response.
9. James main instructs the original surface path to publish the response using the stored reply target.
10. Publish outcome is written back into request state.

### State shape

```text
request: received → normalized → delegated → awaiting_callback → reply_publish_pending → reply_published

US: Created → In Progress → Code Review → Verify → Done
Tasks: Created → Accepted → In Progress → Done (or Blocked / Escalated)
```

### Callback path
- Naomi / MC terminal events → James main
- Amos / MC escalation events → James main

### Human reply path
James main → stored reply target → publish-capable surface session

### Escalation path
- Naomi blocked → James main notified
- review / verify loop exceeded → James main notified
- publish failure after successful implementation → request remains open until resolved

---

## QA Flow (Nested Inside Implementation)

**Goal:** Review and verify work produced by Naomi before the implementation flow is treated as execution-complete.

**Trigger:** Naomi submits a US to Code Review.

**Participants:** Naomi main, Amos main, Mission Control, James main (on terminal events)

**Source of truth:** Mission Control for US/task workflow state

### Code Review loop
1. Amos receives the US in `Code Review`.
2. Amos reviews against definition of done.
3. If approved: Amos / MC move the US to `Verify`.
4. If comments: Amos returns it to `In Progress`; Naomi receives loop-return callback.
5. Loop repeats up to the configured limit.
6. If the loop limit is exceeded: escalate to James main.

### Verify loop
1. Amos receives the US in `Verify`.
2. Amos performs functional verification.
3. If passed: MC moves the US to `Done` and terminal completion becomes visible to James main.
4. If failed: MC returns the US to `In Progress`; Naomi receives loop-return callback.
5. If verify does not converge: escalate to James main.

### Dual callback pattern
- Amos / MC → Naomi: loop returns with comments / failures
- Amos / MC → James: terminal `Done` or escalation

This is execution callback routing. Human reply publication still happens later through the request record.

---

## Development Flow Through Mission Control (Integrated View)

```text
surface session receives user request
  ↓
request normalized into James main
  ↓
James assigns US to Naomi main
  ↓
Naomi: In Progress
  ↓
Naomi submits to Code Review
  ↓
Amos: Code Review
  ↓
Amos: Verify
  ↓
US: Done / Escalated
  ↓
James main decides human-visible response
  ↓
publish via stored reply target
```

At any point:
- review may cycle
- verify may cycle
- the request may remain open after execution completion if publication is unresolved

---

## Flow Format Summary

Each flow above follows this structure:
- **Goal** — what the flow is trying to achieve
- **Trigger** — what initiates it
- **Participants** — which sessions/agents are involved
- **Source of truth** — where state is authoritative
- **Main steps** — the nominal path
- **State shape** — request and execution state views
- **Callback path** — how execution results return
- **Human reply path** — how final/intermediate answers get published
- **Escalation path** — what happens when the nominal path fails