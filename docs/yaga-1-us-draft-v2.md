# YAGA-1 — User Story Draft v2

Status: draft v2
Source epic: `YAGA-1` — V1 Architecture Baseline and Boundaries
Intent: break the epic into planning-ready user stories that freeze blocking architecture decisions without drifting into later implementation design

## Epic intent recap

Freeze the blocking architecture decisions, scope boundaries, and non-goals before implementation starts encoding accidental architecture.

## Story design rule for YAGA-1

These are **decision/baseline stories**, not feature-delivery stories.
Each story must:
- freeze a concrete decision or boundary
- remove a real ambiguity that later epics would otherwise reinterpret
- produce one stable reference artifact for downstream work

If a story mainly creates packaging, templates, or editorial structure without freezing a real decision, it does not count as core architecture work.

## Story classes in this epic

There are two kinds of stories here:

- **Core decision stories** — these freeze real architecture choices
- **Baseline packaging/governance stories** — these package and publish the decision set so it can be referenced safely

The packaging stories are valid, but they are not the architectural center of gravity.

---

## Proposed User Stories

### US-01 — Establish the V1 Baseline Package Structure

**Class**
Packaging / baseline governance story

**Goal**
Create the canonical package structure that later frozen decisions will live in.

**Decision being frozen**
How the baseline decision set is organized, versioned, owned, and updated.

**Why this exists**
Without one canonical package, decisions will fragment across docs, code comments, chats, and later stories.

**How ambiguity is proven removed**
Later epic planning can point to one baseline package and one update path instead of inventing parallel sources.

**Acceptance criteria**
- the baseline package distinguishes clearly between:
  - frozen decisions
  - open questions
  - deferred/post-v1 items
  - explicit non-goals
  - owners of future updates
- there is a canonical decision-record format (ADR or equivalent)
- there is a single baseline index / entry point
- downstream stories have one obvious place to publish decisions

**Outputs**
- architecture baseline index
- decision-record template
- deferred-items register

**Out of scope**
- deciding the content of the architecture itself
- implementation work for later epics

---

### US-02 — Decide the Global Execution and Delivery Model

**Class**
Core decision story

**Goal**
Freeze the execution and delivery stance that all later runtime work must obey.

**Decision being frozen**
The v1 execution model: async-first vs sync-first posture, callback durability, retry/idempotency assumptions, and visibility rules.

**Why this exists**
If this is left fuzzy, later work on transport, recovery, observability, and runtime paths will quietly assume different worlds.

**How ambiguity is proven removed**
Later epics can point to one stable execution model instead of inventing transport/retry semantics locally.

**Decision areas**
- async-first vs synchronous-first
- durable state before callback
- at-least-once vs exactly-once assumptions
- idempotent handler requirement
- callback durability expectation
- terminal vs non-terminal visibility requirements

**Acceptance criteria**
- the execution/delivery stance is explicit
- the baseline contains a delivery guarantee statement
- retry boundary and idempotency expectations are explicit
- callback durability is explicit
- operator-visible implications are explicit
- a conflicting interpretation can be resolved from this story alone without reopening the debate

**Outputs**
- execution model ADR
- delivery semantics baseline note

**Out of scope**
- full A2A schema design
- detailed failure playbooks

---

### US-03 — Define the Supported V1 Scope Boundaries

**Class**
Core decision story

**Goal**
Name exactly what v1 supports and what it refuses to generalize.

**Decision being frozen**
The hard scope boundary for v1: supported loops, named failure classes, closed MVP execution paths, explicit non-goals, and anti-generalization rule.

**Why this exists**
If scope is not frozen early, every later decision story can expand “just a little” until the architecture goes soft again.

**How ambiguity is proven removed**
Any later request can be checked against supported loops, named failure classes, and closed path list without improvisation.

**Decision areas**
- supported success loops
- named failure classes
- closed MVP execution path list
- explicit non-goals
- anti-generalization rule

**Acceptance criteria**
- the two supported loops are documented and named
- named failure classes are documented
- the closed MVP execution path list is documented
- explicit non-goals are documented
- the baseline makes clear that unsupported loop/path/failure-class additions are not silently treated as v1-supported
- later epics can reject scope creep by citing this story alone

**Outputs**
- v1 scope boundary note
- supported loops / failure-class baseline

**Out of scope**
- implementing the loops
- creating detailed operator/test matrixes for later epics

---

### US-04 — Decide the V1 Runtime Placement and Agent-Runtime Interface Model

**Class**
Core decision story

**Goal**
Choose how agents live and how they interface with runtimes, but only as needed for the two supported v1 loops.

**Decision being frozen**
The v1 runtime placement and interface model for James, Naomi, Amos, and Alex.

**Why this exists**
This is the narrowest version of the deployment/runtime question that still blocks later implementation work.

**How ambiguity is proven removed**
Later epics no longer need to guess whether they are building around long-lived agents, per-task invocations, role-symmetry, or role-specific execution paths.

**Decision areas**
- v1 runtime placement / agent living model
- James ingress/session model
- specialist runtime interface models
- whether supported execution paths are symmetrical or intentionally role-specific
- rejected alternatives and tradeoffs

**Acceptance criteria**
- the v1 runtime placement model is explicit
- James ingress/session model is explicit
- specialist runtime interface models are explicit
- non-symmetry across roles is intentionally accepted or intentionally rejected
- the decision records tradeoffs and rejected alternatives
- the decision is scoped to v1 loops, not expanded into full ops-topology design

**Outputs**
- runtime placement / interface ADR
- agent/runtime interface note

**Out of scope**
- full deployment topology for future scale
- adapter implementation details from later epics

---

### US-05 — Decide the Mission Control Boundary and Adapter Stance

**Class**
Core decision story

**Goal**
Define exactly how Mission Control fits into v1 without becoming the runtime itself.

**Decision being frozen**
MC’s v1 role as dev-flow domain adapter and source of truth only for the fields it truly owns.

**Why this exists**
MC is the easiest place for architectural slippage: if left vague, it starts eating transport, orchestration, or runtime-internal truth.

**How ambiguity is proven removed**
Later epics can tell exactly what MC owns, what it maps, and what it must never become.

**Decision areas**
- MC as library vs service in v1
- MC as dev-flow source of truth only
- anti-corruption boundary wording
- owned vs non-owned fields/states
- explicit MC non-goals

**Acceptance criteria**
- MC role in v1 is explicit
- the anti-corruption boundary is explicit
- there is a table of fields/states MC owns vs does not own
- MC is explicitly not transport, orchestration, or internal runtime truth
- dev-flow authority is clearly scoped to MC-owned fields
- a later epic can resolve MC/runtime disputes from this story without reopening the model

**Outputs**
- MC boundary ADR
- MC adapter scope note
- owned-vs-non-owned fields table

**Out of scope**
- implementation of the MC adapter
- dev-flow task breakdown for later epics

---

### US-06 — Define the Canonical Source-of-Truth Matrix

**Class**
Core decision story

**Goal**
Lock down where truth lives for state, history, artifacts, memory, and MC dev-flow state.

**Decision being frozen**
The canonical source-of-truth matrix and divergence-resolution rules.

**Why this exists**
This is the central anti-chaos story. If this stays soft, every other epic will invent its own authority model.

**How ambiguity is proven removed**
For every truth domain, there is exactly one authority, one divergence path, and one operator-visible signal.

**Decision areas**
- event history authority
- task ownership/lifecycle authority
- artifact authority
- memory authority and limits
- Mission Control authority in dev flow
- conflict rules between runtime state and MC state
- observability as derived view only

**Acceptance criteria**
- one compact source-of-truth matrix exists
- each truth domain has exactly one authority
- each truth domain has an owner of future changes
- divergence resolution is defined for runtime vs MC
- operator-visible divergence signal is defined
- observability is explicitly derived only
- memory is explicitly non-authoritative for state transitions
- conflicting interpretations can be resolved from the matrix without a new architecture debate

**Outputs**
- source-of-truth matrix
- divergence-resolution rule

**Out of scope**
- detailed observability implementation
- detailed state-machine implementation

---

### US-07 — Decide the Minimal Memory Model for V1

**Class**
Core decision story

**Goal**
Choose the smallest usable memory model that supports the two loops without turning memory into fake workflow state.

**Decision being frozen**
The minimal v1 memory boundary: what layers exist, where reads are allowed, and what memory may never do.

**Why this exists**
Memory architecture is a classic scope leak. This story exists to keep it deliberately small and subordinate to workflow truth.

**How ambiguity is proven removed**
Later epics know exactly where memory is allowed, where it is forbidden, and what concerns are explicitly deferred.

**Decision areas**
- minimal layers for v1
- named decision points where memory may be read
- prohibition on memory-authorized transitions
- non-shared-by-default stance
- artifact history vs memory boundary
- deferred memory governance concerns

**Acceptance criteria**
- the minimal memory model is explicit
- named allowed read points are explicit
- memory cannot authorize transitions
- memory cannot be sole authority for ownership or status
- broad shared memory is explicitly excluded from v1
- artifact lineage/history is explicitly not memory
- deferred memory governance concerns are listed
- downstream epics can cite this story to reject memory scope creep

**Outputs**
- memory-v1 baseline note
- deferred memory concerns list

**Out of scope**
- memory implementation work
- broad shared-facts governance
- memory-driven automation

---

### US-08 — Publish the Baseline-Ready V1 Architecture Decision Set

**Class**
Packaging / baseline governance story

**Goal**
Close `YAGA-1` with a referenceable baseline package that later epics can safely build on.

**Decision being frozen**
That the YAGA-1 decision set is now the active architecture baseline unless later explicitly changed.

**Why this exists**
Architecture work does not count until later epics can reference one stable baseline instead of re-reading old drafts and chat fragments.

**How ambiguity is proven removed**
Later epics can start from the published baseline without reopening already-frozen decisions.

**Acceptance criteria**
- decisions from US-01..US-07 are consolidated into one baseline package
- unresolved items are explicitly marked deferred or blocked
- there is no unresolved blocker left in the baseline set except explicitly deferred items
- the package is stable enough to reference from later epic planning
- the package passes a review checklist for:
  - ambiguity
  - conflict between decisions
  - missing authority
  - unsupported claims
- later epics can reference the package without reopening blocked architecture decisions

**Outputs**
- consolidated v1 baseline doc set
- explicit deferred-items list
- baseline-ready signoff note

**Out of scope**
- implementation of later epics
- broad architecture redesign after signoff

---

## Suggested implementation order

### Core decision order
1. US-02 — Decide the Global Execution and Delivery Model
2. US-03 — Define the Supported V1 Scope Boundaries
3. US-04 — Decide the V1 Runtime Placement and Agent-Runtime Interface Model
4. US-05 — Decide the Mission Control Boundary and Adapter Stance
5. US-06 — Define the Canonical Source-of-Truth Matrix
6. US-07 — Decide the Minimal Memory Model for V1

### Packaging / baseline governance layer
7. US-01 — Establish the V1 Baseline Package Structure
8. US-08 — Publish the Baseline-Ready V1 Architecture Decision Set

## Notes / open review questions

These are the things I want challenged in review:

- Is this now the right granularity, or should some core decision stories still merge?
- Should US-01 remain a real story or just become epic-level DoD/supporting tasking?
- Is US-04 still too broad, or now narrow enough for v1 loops only?
- Should US-05 and US-06 be swapped, or is the current order now stable enough?
- Is US-07 minimal enough, or still too close to later epic design?
