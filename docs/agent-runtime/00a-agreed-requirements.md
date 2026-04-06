# Agent Runtime — Agreed Requirements Baseline

## Purpose

This document captures the agreed product requirements and architectural constraints for the
Agent Runtime before further documentation refinement.

Its job is simple:
- freeze the core intent,
- prevent repeated re-opening of already-settled fundamentals,
- and give later architecture, contract, and schema docs one clear baseline.

If a later document conflicts with this file, this file wins unless it is explicitly updated.

---

## 1. Product Goal

The goal is to automate Kuba's software-development workflow through a team of durable AI agents.

The expected operating model is:
- Kuba primarily talks to James,
- James orchestrates the other agents,
- agent work is durable, observable, retryable, and recoverable,
- and the system can carry work to completion without depending on transcript luck.

This is not a general chatbot platform.
This is not a planning tool with some AI features bolted on.
This is a runtime for real agent work.

---

## 2. Runtime-First Rule

The Agent Runtime must be able to operate **without Mission Control**.

Mission Control is an optional planning/control-plane integration, not a hard architectural dependency.
In the future, other planning systems may be used instead (for example Jira through MCP or another adapter path).

Therefore:
- all critical execution truth must live in the runtime,
- retry, watchdog, recovery, and ownership semantics must live in the runtime,
- the runtime must not depend on Mission Control-specific assumptions in its core model,
- planning/work-item systems are integrations around the runtime, not the foundation underneath it.

---

## 3. James Is the Front Door

James is the primary user-facing agent and strategic owner for normal user-originated work.

James is responsible for:
- user interaction,
- delegation,
- continuity,
- escalation,
- and final accountability for the outcome toward the human.

Specialist agents are internal crew by default:
- Naomi — implementation
- Amos — review and verify
- Alex — research

Specialists report back into the runtime and to James. They are not the normal user-facing entry point.

---

## 4. Core Runtime Invariants

The following are fixed requirements:

1. Ownership must stay explicit.
2. Handoffs must be durable and observable.
3. A handoff completes only when it is `accepted` or `rejected`.
4. Task execution, callback delivery, and human-visible publication are separate concerns.
5. Runtime events are first-class and durable.
6. Retries, watchdogs, and stale-work detection are runtime responsibilities.
7. The system must be able to explain what happened from durable records.
8. Transcript reconstruction is not an acceptable recovery strategy.

---

## 5. Core Object Responsibilities

### Request

`request` is the durable runtime record for user-originated work.

It owns:
- request identity,
- strategic owner,
- reply routing intent,
- publication state,
- links to execution state.

It does not replace task, handoff, flow, or planning work items.

### Handoff

`handoff` is a transfer of execution responsibility between agents.

It is only about:
- dispatch,
- acceptance,
- rejection,
- and routing metadata needed for the transfer.

It is **not** the container for execution completion.

### Task

`task` is the execution unit.

It owns:
- execution lifecycle,
- active work status,
- blockers,
- completion state,
- and produced artifacts.

### Callback

`callback` is the operational return path from execution owner to delegating owner.

It is how results come back to James or another delegating owner.

### Publication

Publication is a separate runtime concern.

The fact that work is done does not mean the human got the answer.

---

## 6. Multi-Publish Rule

One `request` may produce multiple human-visible publish intents.

Examples:
- a progress update,
- an intermediate status reply,
- a final answer,
- a fallback publication after the primary publish path fails.

Therefore:
- publish intent history must be modeled independently from the request row itself,
- each publish intent has its own idempotency identity,
- request state may carry current publication summary,
- but the full publication history must support more than one intent per request.

---

## 7. Development Flow Baseline

For development work, the baseline path is:

1. James receives or initiates work.
2. James decides the work should enter development execution.
3. Naomi is assigned the development work and must explicitly take it up.
4. Naomi loads context:
   - the work item,
   - parent context such as epic when available,
   - repository context.
5. Naomi ensures the repository is current, updates `main`, and creates a branch.
6. Naomi creates an execution plan and records it as tasks in the planning/work-item system when such a system is present.
7. Naomi executes tasks sequentially.
8. If blocked, Naomi escalates to James.
9. When all tasks are complete, Naomi moves the work to code review.
10. Amos performs code review.
11. Review loops back to Naomi for fixes when needed.
12. Review loop limit is 3; after that the work escalates.
13. Amos performs verify after review passes.
14. Verify may loop back for fixes.
15. Verify loop limit is 2 failures; after that the work escalates.
16. Terminal successful outcome becomes `Done`.

This flow may be integrated with Mission Control, Jira, or another planning system, but the runtime semantics remain the same.

---

## 8. Planning-System Integration Rule

Mission Control is a valid first-class integration target, but it is still an integration.

Planning systems may provide:
- epics,
- user stories,
- tasks,
- backlog/sprint context,
- assignment intent,
- operator-facing planning UI,
- and control-plane visibility.

The runtime must support this model:
- a planning system emits assignment or start intent,
- the runtime turns that into agent work,
- the runtime tracks retries, watchdogs, and execution progress,
- and the planning system reflects or consumes the resulting state through integration contracts.

This same integration model must remain possible for future non-MC providers.

---

## 9. Mission Control Position

Mission Control is **not** the foundation of the runtime.

It is the first serious planning/control-plane integration and may serve as:
- work-item UI,
- work-item CLI,
- operator-facing control-plane visibility,
- a place to start development flows,
- a place to observe changing work-item state.

But even when Mission Control exists:
- runtime execution semantics remain runtime-owned,
- runtime retries and watchdogs remain runtime-owned,
- runtime ownership and callback semantics remain runtime-owned.

If Mission Control disappeared, the runtime would still need to function.

---

## 10. Immediate Documentation Consequences

The documentation set must be aligned to these requirements:

1. Remove any dependency on Mission Control from the runtime core model.
2. Treat Mission Control as an integration and optional first-class companion, not a prerequisite.
3. Keep `handoff`, `task`, `callback`, and `publication` sharply separated.
4. Support multiple publish intents per request.
5. Make development-flow descriptions match the actual James -> Naomi -> Amos loop agreed above.
6. Keep retry/watchdog/recovery responsibility in the runtime.

