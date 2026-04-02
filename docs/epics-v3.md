# yaga.ai — Epic Draft v3

Status: draft v3
Owner: James
Review basis: v2 + second review loop from Naomi, Amos, Alex
Scope: epics only, no stories/tasks yet
Intent: define a v1 plan that is operationally provable, architecturally coherent, and resistant to scope creep

## V1 success criterion

v1 is successful only if the system can support, debug, and recover the **explicitly supported** end-to-end loops below with clear ownership, visible state, and predictable callbacks:

1. **James -> Naomi -> Amos -> James**
2. **James -> Alex -> James**

Anything outside those supported loops and failure classes is not automatic proof of v1 success.

## Cross-epic contract rule

Every epic in this document must explicitly define:

- **source of truth**
- **core invariants**
- **failure modes covered**
- **operator-visible signals**
- **out of scope**
- **acceptance evidence**

If an epic cannot state those six things, it is still too fuzzy.

## Planning stance

- v1 is internal-first, not multi-tenant
- durable agents remain fixed: James, Naomi, Amos, Alex
- **agent != runtime**; runtime is execution tooling, not durable ownership
- Mission Control is the **first domain adapter for development flow**, not the hidden definition of the generic runtime
- this plan optimizes for **the shortest provable operational loops**, not for broad platform coverage

## Explicit v1 non-goals

- no general workflow DSL
- no broad cross-agent shared memory fabric
- no giant self-improvement framework
- no broad adapter marketplace
- no attempt at universal chatbot behavior
- no claims of general self-healing beyond explicitly supported failure classes

---

## EPIC-01 — V1 Architecture Baseline and Boundaries

**Goal**
Freeze the blocking architectural decisions, scope boundaries, and non-goals before implementation starts encoding accidental architecture.

**Scope**
- event transport decision
- agent deployment model decision
- James ingress/session model decision
- Naomi / Amos / Alex runtime interface decision
- Mission Control as library vs service in v1
- source-of-truth/query model decision
- minimum memory model decision
- explicit ADRs and deferred-items list

**Source of truth**
- ADRs / architecture decision records
- v1 scope and non-goals section in docs

**Core invariants**
- no implementation-critical subsystem is left as an implicit TBD
- deferred concerns are named and intentionally excluded
- v1 boundaries are explicit enough to reject scope creep

**Failure modes covered**
- accidental architectural divergence
- hidden assumptions made by different epics
- late discovery that two subsystems assumed incompatible models

**Operator-visible signals**
- documented decision list
- documented deferred items
- versioned architecture baseline

**Out of scope**
- detailed implementation stories
- database migrations and coding tasks

**Acceptance evidence**
- each blocking decision has a recorded answer
- each deferred item is explicitly tagged post-v1 or unresolved

---

## EPIC-02 — Runtime Persistence and State Backbone

**Goal**
Build the durable substrate for state, history, storage, dedup, and queryable projections.

**Scope**
- event store
- task store
- handoff store
- artifact store
- memory store
- dedup persistence
- state projections for owner, status, callback target, queue state
- rebuild/reprojection rules

**Source of truth**
- stores themselves, by type:
  - event history -> event store
  - current task/ownership state -> task/handoff state + projections
  - artifacts -> artifact store
  - memory -> memory store

**Core invariants**
- current operational state is queryable without reading transcripts
- history and current state are separated cleanly
- projections are rebuildable from durable records
- dedup state is durable enough for retry handling

**Failure modes covered**
- projection drift
- missing current owner/status visibility
- duplicate processing due to lost dedup state

**Operator-visible signals**
- queryable owner/status/callback view
- projection rebuild status
- event/history lookup by task and correlation id

**Out of scope**
- wire delivery semantics
- task lifecycle policy
- recovery policy beyond storage correctness

**Acceptance evidence**
- given a task or flow, operator can query current owner/status/callback target
- given a correlation id, operator can retrieve event history
- projections can be rebuilt without corrupting source records

---

## EPIC-03 — A2A Contract Layer and Delivery Semantics

**Goal**
Define and implement the wire contract for commands, events, statuses, artifacts, and callbacks.

**Scope**
- envelopes with `correlation_id`, `causation_id`, `dedup_key`, `version`
- routing and subscription rules
- callback delivery contract
- schema validation
- explicit semantics for:
  - at-least-once vs exactly-once expectations
  - ordering guarantees or lack of guarantees
  - dedup boundary
  - poison message / quarantine path
  - schema version behavior

**Source of truth**
- A2A contract schema and delivery policy docs
- runtime message handlers conforming to that contract

**Core invariants**
- duplicate-safe processing is defined, not guessed
- unsupported/malformed messages are quarantined, not silently ignored
- later epics cannot redefine delivery semantics ad hoc

**Failure modes covered**
- duplicate delivery
- malformed message
- schema mismatch
- unprocessable message needing quarantine
- callback routing mismatch

**Operator-visible signals**
- message accepted/rejected/quarantined state
- callback delivery status
- duplicate/quarantine counters and event traces

**Out of scope**
- task ownership rules
- lifecycle transitions
- storage internals already covered by EPIC-02

**Acceptance evidence**
- same dedup key does not create repeated intended side effects in idempotent handlers
- malformed messages are visible in quarantine with reason
- delivery semantics are precise enough to support recovery tests later

---

## EPIC-04 — Agent Core: Ownership, Sessions, Tasks, Handoffs, and Callbacks

**Goal**
Make owner-first runtime behavior explicit in the data model and lifecycle rules.

**Scope**
- durable agent identity model
- session vs agent separation
- task model with owner, requester, optional executor, callback target, strategic callback, status
- handoff lifecycle: dispatched, accepted, rejected
- queue/capacity awareness
- task and callback lifecycle rules
- terminal vs near-terminal state semantics
- ownership edge cases:
  - duplicate acceptance
  - callback after cancel
  - callback after reassignment
  - unreachable owner
  - unreachable requester/callback target
  - orphaned accepted task

**Source of truth**
- task/handoff lifecycle model
- task state and ownership records in state backbone

**Core invariants**
- every task has at most one active owner
- ownership is never inferred from chat context
- terminal states are immutable except explicit operator override with audit trail
- callback target is always explicit for detached work

**Failure modes covered**
- ownership conflict
- orphaned task
- stale callback destination
- invalid post-terminal callback

**Operator-visible signals**
- active owner
- queue state
- current lifecycle state
- callback destination and callback failure visibility

**Out of scope**
- flow-level loops across multiple tasks
- delivery transport behavior already defined in EPIC-03

**Acceptance evidence**
- operator can answer who owns this / what state is it in / where does result go
- edge cases above produce explicit, testable outcomes

---

## EPIC-05 — Artifact Model, Validation Contracts, and Lineage

**Goal**
Define what work products are, how they are validated, and how they move through the system.

**Scope**
- artifact schema
- artifact lifecycle: draft, produced, validated, superseded
- lineage: produced_by, derived_from, referenced_by
- shape/completeness contracts for artifact types
- validation rules for key artifact classes
- artifact references in handoffs and callbacks

**Source of truth**
- artifact store and artifact validation contracts

**Core invariants**
- downstream tasks consume artifacts by reference, not improvised inline blobs
- incomplete artifacts can be rejected explicitly
- lineage is traceable across at least one full flow

**Failure modes covered**
- incomplete artifact
- invalid artifact shape
- artifact consumed without validation
- missing artifact reference in callback/handoff

**Operator-visible signals**
- artifact status
- validation outcome
- lineage trail
- superseded/current version visibility

**Out of scope**
- run-level observability and timeline UI
- memory promotion from artifact content

**Acceptance evidence**
- review comments, verify evidence, and implementation artifacts each have minimum valid shape
- downstream stage can reject incomplete artifact using contract, not human intuition alone

---

## EPIC-06 — Observability, Audit, and Debug Path

**Goal**
Make the runtime inspectable early, using the state and artifact contracts already defined.

**Scope**
- structured event logs
- correlation and causation lineage
- per-run timeline
- tool-call ledger
- memory-read/write ledger where impactful
- status history
- artifact-aware debug views
- prompt/context snapshots at key decision points
- redaction, retention, and access rules for logs/snapshots
- basic replay/debug path by correlation id

**Source of truth**
- event history for what happened
- task/state projections for current status
- artifact store for work products
- memory store for memory state at recorded versions

**Core invariants**
- what happened and what is true now are distinguishable
- observability does not silently leak secrets by design
- debugging does not require transcript archaeology for supported flows

**Failure modes covered**
- invisible failure point
- missing context at decision point
- over-logging sensitive data
- mismatch between state view and event history

**Operator-visible signals**
- timeline by run/correlation id
- last known good state
- first visible failure point
- snapshot redaction status

**Out of scope**
- full forensic replay of arbitrary unsupported flows
- unrestricted transcript capture

**Acceptance evidence**
- for supported loops, operator can identify last good event and first failing event
- snapshot/log policies explicitly govern redaction, retention, and access

---

## EPIC-07 — Runtime Execution Paths (MVP Only)

**Goal**
Implement only the execution paths needed to prove the two supported v1 loops.

**Scope**
- James user-ingress/session path
- Naomi implementation execution path
- Amos review/verify execution path
- Alex research execution path
- execution start/finish/timeout events
- explicit classification per path:
  - resumable
  - restartable
  - re-drivable
  - forbidden to auto-replay
- adapter rule: runtime adapters stay dumb and observable; ownership/retry/escalation policy lives outside them

**Source of truth**
- execution contracts per supported path
- execution events emitted into observability stack

**Core invariants**
- v1 supports only the paths required for the two named loops
- adapters do not smuggle orchestration policy inside themselves
- each supported path has a declared recovery class

**Failure modes covered**
- runtime timeout
- interrupted execution
- illegal automatic replay of unsafe path
- invisible adapter behavior

**Operator-visible signals**
- current execution path and runtime
- recovery class for path
- timeout/interruption status

**Out of scope**
- broad adapter family
- plugin ecosystem
- runtime generalization beyond supported loops

**Acceptance evidence**
- one implementation path, one QA path, and one research path run under explicit execution contracts
- unsupported paths are visibly unsupported, not implied

---

## EPIC-08 — Generic Runtime Flow Model (Minimal V1)

**Goal**
Implement the smallest generic flow model needed for research, implementation, QA, and callbacks — not a general workflow platform.

**Scope**
- minimal flow model spanning tasks, handoffs, artifacts, statuses, and callbacks
- research flow contract
- implementation flow contract
- QA flow contract
- operational vs strategic callback semantics
- loop/escalation semantics required by supported flows

**Source of truth**
- generic runtime flow definitions and flow state

**Core invariants**
- one active owner per task at a time
- callback target is always resolvable for detached supported work
- loop counters are monotonic where defined
- terminal states stay terminal unless explicit override occurs

**Failure modes covered**
- unresolved callback target
- invalid loop transition
- escalation dead end
- flow state that cannot map to current owner/status

**Operator-visible signals**
- flow state
- active owner
- callback route
- loop count and escalation state

**Out of scope**
- workflow DSL
- arbitrary user-defined flows
- general-purpose BPM engine behavior

**Acceptance evidence**
- generic model can express James -> Alex -> James and James -> Naomi -> Amos -> James cleanly
- QA and research are first-class supported flows, not dev-only footnotes

---

## EPIC-09 — Mission Control Domain Adapter and Dev-Flow Mapping

**Goal**
Map generic runtime state to Mission Control’s development workflow without letting MC redefine the generic runtime.

**Scope**
- mapping runtime state <-> MC user stories/tasks
- Mission Control as source of truth for dev workflow state
- intent-event -> MC validation -> status change pattern
- code review loop
- verify loop
- dev-flow escalation routing
- assignment and queue semantics for development work

**Source of truth**
- Mission Control for development workflow state
- generic runtime for generic task/flow semantics outside MC-specific state

**Core invariants**
- MC adapter maps runtime/dev-flow concepts; it does not become the runtime’s universal truth layer
- invalid dev transitions are explicitly rejected
- review and verify semantics remain visible and bounded

**Failure modes covered**
- transition rejected by MC
- MC/runtime state mismatch in dev flow
- review/verify loop overflow
- dev assignment ambiguity

**Operator-visible signals**
- MC state vs runtime state mapping view
- rejected transition reason
- review/verify loop counters

**Out of scope**
- research flow ownership
- generic flow logic already defined in EPIC-08

**Acceptance evidence**
- dev-flow state is authoritative in MC and still understandable in runtime terms
- review and verify loops follow defined caps and explicit escalation behavior

---

## EPIC-10 — Memory V1 (Minimal, Per-Agent, Non-Shared by Default)

**Goal**
Provide useful memory continuity without letting memory become fake workflow state or a cross-agent swamp.

**Scope**
- per-agent boundaries
- minimum v1 memory layers:
  - working
  - episodic/semantic with controlled promotion
  - limited procedural where explicitly validated
- selective load policy
- justified write policy
- correction/retraction model
- memory-read provenance for material decisions
- explicit rule: memory is advisory, not source of truth

**Source of truth**
- memory store for memory entries
- task/state stores for operational truth

**Core invariants**
- memory does not own workflow state
- memory is not shared broadly across agents by default
- corrected/retracted memory can be detected and handled

**Failure modes covered**
- stale memory steering decisions
- retracted memory still influencing behavior
- accidental drift into memory-driven workflow state

**Operator-visible signals**
- memory read/write provenance for important decisions
- correction/retraction visibility
- evidence that a decision used memory vs current task state

**Out of scope**
- broad shared-facts governance framework
- memory-driven automation loops
- cross-agent shared memory as default pattern

**Acceptance evidence**
- supported loops can use useful memory without confusing it for workflow truth
- memory reads that materially influence behavior are inspectable

---

## EPIC-11 — Recovery Guarantees and Escalation Ownership

**Goal**
Define the supported recovery model realistically and align it with delivery semantics from EPIC-03.

**Scope**
- execution timeout vs workflow timeout
- retry rules aligned with delivery semantics and dedup model
- callback failure handling
- orphan detection
- stale ownership handling
- blocked vs escalated semantics
- explicit split between:
  - auto-recover
  - detect-and-surface only
  - operator/James-required recovery
- focused recovery playbooks for supported failure classes

**Source of truth**
- recovery policy docs + lifecycle/state model + delivery semantics

**Core invariants**
- recovery promises never exceed what delivery semantics support
- each supported failure mode has a named recovery owner
- escalation is explicit, not silent timeout drift

**Failure modes covered**
- orphaned task
- duplicate callback
- callback missing after partial progress
- timeout with uncertain side effects
- stale owner / blocked dead end

**Operator-visible signals**
- recovery path chosen
- who owns recovery now
- whether situation is auto-recoverable or operator-required

**Out of scope**
- broad self-healing claims
- unsupported failure classes beyond named v1 scope

**Acceptance evidence**
- each named failure mode has default recovery action and escalation owner
- recovery rules are testable against delivery semantics already defined

---

## EPIC-12 — Governance and Policy Gates (Minimal V1)

**Goal**
Keep v1 governable without turning governance into a platform of its own.

**Scope**
- minimal behavior-change gates
- minimal platform-change approval gates
- rollback requirement for approved changes
- version/policy lineage
- minimal shared-fact promotion gate only if required

**Source of truth**
- policy records and approval history

**Core invariants**
- behavior-affecting changes do not go live invisibly
- rollback path exists for approved changes
- governance remains intentionally small in v1

**Failure modes covered**
- unreviewed behavior drift
- unknown active policy version
- inability to rollback approved change

**Operator-visible signals**
- current policy/version
- approval history
- rollback availability

**Out of scope**
- large autonomous self-improvement loop
- rich governance marketplace/process engine

**Acceptance evidence**
- policy-affecting changes are visible, attributable, and reversible

---

## EPIC-13 — Operator Surfaces, Loop Validation, and V1 Hardening

**Goal**
Provide the minimum operator-facing controls and prove the two supported loops work under the supported failure classes.

**Scope**
- operator surfaces for:
  - pause/resume
  - cancel with reason
  - force reassign
  - quarantine event/artifact
  - replay/debug eligibility view
  - audited override trail
- visibility of all non-terminal supported work
- validation suite for supported loops and named failure classes
- runbooks for supported recovery cases
- end-to-end validation of:
  - James -> Naomi -> Amos -> James
  - James -> Alex -> James

**Source of truth**
- operator surfaces over runtime state, event history, and recovery policy

**Core invariants**
- operator intervention is visible and auditable
- supported loops are validated end-to-end, not assumed from component existence
- hardening scope stays tied to supported loops, not a giant QA program

**Failure modes covered**
- operator cannot intervene safely
- supported loop works nominally but fails under named recovery cases
- overrides happen without audit trail

**Operator-visible signals**
- all supported non-terminal work
- intervention history
- validation status of supported loops and failure classes

**Out of scope**
- exhaustive QA for all hypothetical future flows
- broad admin product surface beyond v1 needs

**Acceptance evidence**
- operator can intervene safely in supported scenarios
- both supported loops are proven end-to-end under nominal and named failure conditions

---

## Proposed implementation order

1. EPIC-01 — V1 Architecture Baseline and Boundaries
2. EPIC-02 — Runtime Persistence and State Backbone
3. EPIC-03 — A2A Contract Layer and Delivery Semantics
4. EPIC-04 — Agent Core: Ownership, Sessions, Tasks, Handoffs, and Callbacks
5. EPIC-05 — Artifact Model, Validation Contracts, and Lineage
6. EPIC-06 — Observability, Audit, and Debug Path
7. EPIC-07 — Runtime Execution Paths (MVP Only)
8. EPIC-08 — Generic Runtime Flow Model (Minimal V1)
9. EPIC-09 — Mission Control Domain Adapter and Dev-Flow Mapping
10. EPIC-10 — Memory V1 (Minimal, Per-Agent, Non-Shared by Default)
11. EPIC-11 — Recovery Guarantees and Escalation Ownership
12. EPIC-12 — Governance and Policy Gates (Minimal V1)
13. EPIC-13 — Operator Surfaces, Loop Validation, and V1 Hardening

## Final note

This version is intentionally stricter than v2.

The point is not to describe everything the platform might one day become.
The point is to prove, with evidence, that a small owner-first runtime can run its two core loops with:
- explicit ownership
- clear source-of-truth boundaries
- predictable callbacks
- visible failures
- bounded recovery behavior
- auditable operator intervention
