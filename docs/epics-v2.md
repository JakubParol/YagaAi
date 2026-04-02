# yaga.ai — Epic Draft v2

Status: draft v2
Owner: James
Review input merged from: Naomi, Amos, Alex
Scope: epics only, no stories/tasks yet
Intent: replace the first draft with a more operational, spine-first v1 plan

## What changed vs v1 draft

This version intentionally changes direction in a few places:

- adds an explicit **runtime persistence/state backbone** epic
- splits **generic runtime flow** from **Mission Control dev-flow adapter**
- moves **observability/audit/debug** much earlier
- narrows **runtime adapters** to MVP-critical execution paths
- moves **memory** later and makes it more v1-minimal
- trims **failure/recovery** to practical v1 semantics instead of broad compensation ambition
- shrinks **governance** to minimal v1 policy gates
- treats **operator controls** as a hard requirement, not a nice-to-have admin layer
- requires **acceptance/evidence/invariants** per epic so we can verify the system, not just describe it

## Planning stance

- v1 is internal-first, not multi-tenant
- durable agents remain fixed: James, Naomi, Amos, Alex
- **agent != runtime**; runtime is a tool/executor, not the durable owner
- explicit ownership, handoffs, callbacks, artifacts, and auditability are core requirements
- Mission Control is the **first domain implementation**, not the definition of the generic runtime
- the plan should prove the **first operational loop** works end-to-end, not just accumulate platform pieces

---

## EPIC-01 — V1 Architecture Baseline and Boundaries

**Goal**
Freeze the implementation-critical decisions and v1 boundaries before the codebase hardcodes them by accident.

**Scope**
- decide event transport for v1
- decide agent deployment model
- decide James ingress/session model
- decide Naomi / Amos / Alex runtime interface model
- decide whether Mission Control is library or service in v1
- decide state/query source-of-truth model
- decide minimum memory storage model for v1
- record ADRs / explicit non-goals / deferred items

**Acceptance / evidence**
- every blocking architectural choice has a written decision and owner
- no major runtime subsystem is left in “TBD by implementation” state
- deferred items are explicitly marked as post-v1, not silently omitted

---

## EPIC-02 — Runtime Persistence and State Backbone

**Goal**
Create the durable substrate the runtime will stand on: state, history, storage, dedup, and projections.

**Scope**
- event store
- task store
- handoff store
- artifact store
- memory store
- dedup persistence
- state projections / query model for owner, status, callback visibility
- source-of-truth rules between store types

**Acceptance / evidence**
- given a task or flow, we can query current owner, status, and callback target without reading chat transcripts
- given an event id / correlation id, we can find the persisted event history
- projections can be rebuilt from stored data without corrupting current operational state

---

## EPIC-03 — A2A Contract Layer and Delivery Semantics

**Goal**
Build the internal communication layer for commands, events, statuses, and artifact references.

**Scope**
- event/command envelope with `correlation_id`, `causation_id`, `dedup_key`, `version`
- per-agent routing and subscription model
- durable delivery semantics
- command/event schema validation
- callback delivery semantics
- dedup handling
- explicit policy for:
  - at-least-once vs exactly-once expectations
  - ordering guarantees or lack of guarantees
  - poison-message / quarantine path
  - schema versioning policy

**Acceptance / evidence**
- duplicate delivery produces no duplicated side effects for idempotent handlers
- unsupported or malformed messages are quarantined, not silently dropped
- delivery semantics are documented strongly enough that later epics cannot make contradictory assumptions

---

## EPIC-04 — Agent Core: Ownership, Sessions, Tasks, Handoffs, and Callbacks

**Goal**
Implement the owner-first runtime model as a real contract, not a prompt convention.

**Scope**
- durable agent identity model
- session model separated from durable agent identity
- task model with owner, requester, optional executor, callback target, strategic callback, status
- handoff lifecycle: dispatched, accepted, rejected
- canonical status semantics and terminal vs near-terminal rules
- capacity / queue awareness per agent
- explicit rules for edge cases:
  - duplicate acceptance
  - callback after cancel
  - callback after reassignment
  - unreachable owner
  - unreachable requester / callback target
  - orphaned accepted task

**Acceptance / evidence**
- ownership never has to be inferred from chat context
- terminal and near-terminal states are enforced consistently
- edge cases above have explicit, testable outcomes rather than “best effort” behavior

---

## EPIC-05 — Observability, Audit, and Debug Path

**Goal**
Make the runtime inspectable early enough that later work is not built blind.

**Scope**
- structured event logging
- correlation and causation lineage
- per-run timeline view
- tool-call ledger
- memory-write ledger
- status history view
- artifact lineage view
- prompt/context snapshots at key decision points
- redaction, retention, and access rules for snapshots/logs
- basic replay/debug path by `correlation_id`

**Acceptance / evidence**
- for any failed run, we can identify last known good state and first visible failure point
- prompt/context snapshots do not blindly log secrets
- an operator can inspect the main decision trail without reading raw session transcripts

---

## EPIC-06 — Artifact Model, Validation, and Lineage

**Goal**
Treat work products as durable first-class artifacts, not inline blobs in chat.

**Scope**
- artifact schema and storage
- artifact lifecycle: draft, produced, validated, superseded
- lineage: produced_by, derived_from, referenced_by
- artifact shape contracts for core types
- validation of completeness, not just existence
- handoff integration via artifact references

**Examples of required shape validation**
- review comments should not be considered complete without fields like severity, anchor/context, and reason
- verify evidence should contain verdict + supporting evidence
- implementation artifact should clearly point to diff/PR/change set

**Acceptance / evidence**
- downstream agents can reject incomplete artifacts using explicit validation rules
- artifact lineage can be followed across at least one multi-agent flow

---

## EPIC-07 — Runtime Execution Adapters (MVP Set)

**Goal**
Connect durable agents to real execution runtimes without hiding orchestration policy inside adapters.

**Scope**
- James user-ingress / session handling path
- Naomi implementation runtime path
- Amos review/verify runtime path
- Alex research runtime path
- runtime invocation contract
- execution start/finish/timeout events
- explicit v1 rules for what is:
  - resumable
  - restartable
  - failed-and-re-drivable
- adapter contract: adapters must stay relatively dumb and observable; retry/escalation/ownership policy lives outside them

**Acceptance / evidence**
- adapters emit enough execution telemetry to support debugging
- retry / escalation policy is not hidden inside adapter code
- at least one implementation path and one QA/research path can execute end-to-end under the same runtime rules

---

## EPIC-08 — Generic Runtime Flow Model

**Goal**
Implement the generic flow layer for research, implementation, QA, and callback-driven work before binding it to Mission Control.

**Scope**
- generic flow model spanning tasks, events, artifacts, statuses, and callbacks
- research flow contract
- implementation flow contract
- QA flow contract
- explicit operational vs strategic callback handling
- loop and escalation semantics at generic-runtime level
- requirements for QA and research outputs, not just dev flow

**Acceptance / evidence**
- the generic runtime can express:
  - James -> Alex -> James research flow
  - James -> Naomi -> Amos -> James delivery flow
- QA and research are represented as first-class flows, not side notes to development

---

## EPIC-09 — Mission Control Domain Adapter and Dev-Flow Integration

**Goal**
Bind the generic runtime model to the privileged Mission Control development workflow without collapsing the generic layer into MC-specific assumptions.

**Scope**
- mapping between generic runtime primitives and MC user stories/tasks
- Mission Control as source of truth for dev workflow state
- intent-event -> MC validation -> status change pattern
- Naomi -> Amos code review loop
- verify loop
- escalation triggers and callback routing to James
- assignment and queue semantics for development work

**Acceptance / evidence**
- dev workflow state is authoritative in MC, not duplicated ad hoc elsewhere
- MC can reject invalid transitions explicitly
- review and verify loops follow defined caps and escalation behavior

---

## EPIC-10 — Memory V1

**Goal**
Deliver useful per-agent memory for v1 without letting memory sprawl outrun runtime reliability.

**Scope**
- per-agent memory boundaries
- minimum usable layers for v1:
  - working memory
  - episodic/semantic memory with controlled promotion
  - limited procedural memory only where validated and approved
- selective load policy
- justified write policy
- correction/retraction model
- memory read provenance for higher-impact decisions
- enforce “memory is advisory, not source of truth” in runtime behavior

**Acceptance / evidence**
- agents can persist and reuse useful context without treating memory as workflow state
- retracted/corrected memory entries do not silently continue steering decisions
- memory reads/writes are auditable where they materially influence behavior

---

## EPIC-11 — Failure Recovery and Timeout Policy

**Goal**
Define the practical v1 recovery model for the failures we already expect.

**Scope**
- execution timeout vs workflow timeout semantics
- retry policy with idempotency requirements
- callback retry and callback-failure behavior
- orphan detection
- stale ownership handling
- blocked vs escalated recovery paths
- explicit split between:
  - what the system recovers automatically
  - what it only detects and surfaces
  - what always requires James/operator action
- focused recovery playbooks for:
  - orphaned task
  - duplicate callback
  - invalid terminal transition
  - partial artifact persisted but callback missing
  - runtime timeout with uncertain side effects

**Acceptance / evidence**
- each named failure mode has a default owner and default recovery path
- timeout semantics are unambiguous enough to test
- recovery language stays realistic; no fake “self-healing” claims without proof

---

## EPIC-12 — Governance and Policy Gates (Minimal V1)

**Goal**
Add only the minimum policy controls needed so v1 does not become unsafe or unreviewable.

**Scope**
- minimal behavior/improvement candidate model
- approval gates for behavioral and platform-affecting changes
- rollback requirement for approved changes
- policy/version lineage
- minimal shared-facts/promotion gate if needed

**Explicit non-goal for now**
- do not build a giant autonomous self-improvement framework in v1

**Acceptance / evidence**
- behavior-affecting changes cannot go live without a visible review path
- rollback path exists for approved changes
- governance stays small enough not to block core runtime delivery

---

## EPIC-13 — Operator Controls, Delivery-Loop Validation, and V1 Hardening

**Goal**
Prove the system is operable by humans and that the first real workflow loop works end-to-end.

**Scope**
- minimum operator controls:
  - pause/resume
  - cancel with reason
  - force reassign
  - replay eligibility / debug view
  - quarantine event/artifact
  - audited override trail
- visibility of all non-terminal tasks/flows with owner, age, last event
- contract-style edge-case test suite
- runbooks for common failure modes
- first operational-loop validation:
  - James -> Naomi -> Amos -> James callback
  - James -> Alex -> James callback
- deployment readiness checklist for internal use

**Acceptance / evidence**
- operator can intervene safely without corrupting auditability
- the first dev loop and first research loop are both proven end-to-end
- v1 hardening is evidenced by tests and runbooks, not just optimism

---

## Proposed implementation order

1. EPIC-01 — V1 Architecture Baseline and Boundaries
2. EPIC-02 — Runtime Persistence and State Backbone
3. EPIC-03 — A2A Contract Layer and Delivery Semantics
4. EPIC-04 — Agent Core: Ownership, Sessions, Tasks, Handoffs, and Callbacks
5. EPIC-05 — Observability, Audit, and Debug Path
6. EPIC-06 — Artifact Model, Validation, and Lineage
7. EPIC-07 — Runtime Execution Adapters (MVP Set)
8. EPIC-08 — Generic Runtime Flow Model
9. EPIC-09 — Mission Control Domain Adapter and Dev-Flow Integration
10. EPIC-10 — Memory V1
11. EPIC-11 — Failure Recovery and Timeout Policy
12. EPIC-12 — Governance and Policy Gates (Minimal V1)
13. EPIC-13 — Operator Controls, Delivery-Loop Validation, and V1 Hardening

## Notes on intent

This version is deliberately less romantic and more operational.

The job of v1 is not to look like a complete agent platform on paper.
The job of v1 is to make these statements true with evidence:
- ownership is explicit
- state is queryable
- handoffs and callbacks are predictable
- QA and research are first-class, not afterthoughts
- Mission Control is a domain adapter, not the hidden definition of the whole runtime
- operators can debug and intervene without spelunking through session chaos
- the first end-to-end loops actually work
