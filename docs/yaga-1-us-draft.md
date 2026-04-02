# YAGA-1 — User Story Draft

Status: draft v1
Source epic: `YAGA-1` — V1 Architecture Baseline and Boundaries
Intent: break the epic into concrete planning-ready user stories before creating them in Mission Control

## Epic intent recap

Freeze the blocking architectural decisions, scope boundaries, and non-goals before implementation starts encoding accidental architecture.

## Planning principle

These stories are **decision and baseline stories**, not delivery-feature stories.
Their output is primarily:
- explicit decisions
- ADRs / baseline docs
- source-of-truth boundaries
- supported-loop boundaries
- non-goals and deferred items

If a story cannot end with a clear architectural decision or baseline artifact, it probably does not belong in `YAGA-1`.

---

## Proposed User Stories

### US-01 — Establish the V1 Architecture Baseline Package

**Goal**
Create the baseline package structure for architecture decisions, assumptions, and deferred items so later decisions have one home.

**Why**
Without a single baseline package, decisions will leak into random docs, code comments, and chat history.

**Acceptance criteria**
- a canonical baseline package structure exists in docs
- there is an ADR template or equivalent decision format
- there is a deferred-items / post-v1 section
- there is an owner and update rule for the baseline package

**Outputs**
- architecture baseline index
- decision record template
- deferred-items register

**Suggested dependency**
- none; this should be first

---

### US-02 — Decide the Global Execution and Delivery Model

**Goal**
Freeze the core execution stance for v1 so later runtime work does not assume contradictory behavior.

**Decision areas**
- async-first vs synchronous-first
- durable state before callback
- at-least-once vs exactly-once assumptions
- idempotent handler requirement
- terminal vs non-terminal visibility requirements

**Acceptance criteria**
- the execution/delivery stance is written explicitly
- retry/idempotency assumptions are not left implicit
- callback durability expectation is stated
- later epics can reference one stable execution model

**Outputs**
- execution model ADR
- delivery semantics baseline note

**Suggested dependency**
- after US-01

---

### US-03 — Decide the Agent Runtime and Deployment Model

**Goal**
Choose how agents live and how they interact with runtimes, so implementation does not accidentally mix incompatible models.

**Decision areas**
- agent deployment model
- session model for James
- runtime interface model for Naomi / Amos / Alex
- whether supported execution paths are symmetrical or intentionally role-specific

**Acceptance criteria**
- deployment model is explicit
- James ingress/session model is explicit
- specialist runtime interface models are explicit
- non-symmetry across roles is either accepted or rejected intentionally

**Outputs**
- deployment/runtime ADR
- agent/runtime interface note

**Suggested dependency**
- after US-02

---

### US-04 — Define the Canonical Source-of-Truth Matrix

**Goal**
Lock down where truth lives for state, history, artifacts, memory, and Mission Control dev-flow state.

**Decision areas**
- event history authority
- task ownership/lifecycle authority
- artifact authority
- memory authority and limits
- Mission Control authority in dev flow
- conflict rules between runtime state and MC state

**Acceptance criteria**
- one compact source-of-truth matrix exists
- conflict handling is defined for runtime vs MC in dev flow
- observability is explicitly derived, not a new truth store
- memory is explicitly non-authoritative for workflow transitions

**Outputs**
- source-of-truth matrix
- MC/runtime divergence rule

**Suggested dependency**
- after US-02, parallel with US-03 if needed

---

### US-05 — Define the Supported V1 Scope Boundaries

**Goal**
Name exactly what v1 supports so implementation and later planning stay inside the intended box.

**Decision areas**
- supported success loops
- named failure classes
- closed MVP execution path list
- explicit non-goals
- anti-generalization rule for v1

**Acceptance criteria**
- the two supported loops are named and documented
- named failure classes are documented
- closed execution path list is documented
- explicit non-goals are documented
- there is a rule against generalizing beyond the loops/failure classes without an explicit scope change

**Outputs**
- v1 scope boundary note
- supported loops and failure-class baseline

**Suggested dependency**
- after US-02 and US-03

---

### US-06 — Decide the Mission Control Boundary and Adapter Stance

**Goal**
Define exactly how Mission Control fits into v1 without allowing it to silently become the runtime itself.

**Decision areas**
- MC as library vs service in v1
- MC as dev-flow source of truth only
- anti-corruption boundary wording
- what fields/states MC owns vs does not own

**Acceptance criteria**
- MC role in v1 is explicit
- anti-corruption boundary is explicit
- MC does not own runtime internals by accident
- dev-flow authority is clearly scoped to MC-owned fields

**Outputs**
- MC boundary ADR
- MC adapter scope note

**Suggested dependency**
- after US-04 and US-05

---

### US-07 — Decide the Minimal Memory Model for V1

**Goal**
Choose the smallest usable memory model that supports the two v1 loops without turning memory into fake workflow state.

**Decision areas**
- minimal layers for v1
- named decision points where memory may be read
- prohibition on memory-authorized transitions
- non-shared-by-default stance
- deferred memory governance concerns

**Acceptance criteria**
- minimal memory model is explicit
- named allowed read points are explicit
- memory cannot authorize transitions
- broad shared memory is explicitly excluded from v1

**Outputs**
- memory-v1 baseline note
- deferred memory concerns list

**Suggested dependency**
- after US-04 and US-05

---

### US-08 — Publish the Baseline-Ready V1 Architecture Decision Set

**Goal**
Close `YAGA-1` with a baseline package that later epics can safely build on.

**Why**
Architecture work only counts if later implementation can reference one stable baseline instead of reverse-engineering decisions from scattered drafts.

**Acceptance criteria**
- decisions from US-01..US-07 are consolidated into the baseline package
- unresolved items are explicitly marked deferred or blocked
- the baseline package is stable enough to reference from later epic planning
- the package is reviewable by operators/agents without re-reading all earlier drafts

**Outputs**
- consolidated v1 baseline doc set
- explicit deferred-items list
- baseline-ready signoff note

**Suggested dependency**
- after all prior US

---

## Suggested implementation order

1. US-01 — Establish the V1 Architecture Baseline Package
2. US-02 — Decide the Global Execution and Delivery Model
3. US-03 — Decide the Agent Runtime and Deployment Model
4. US-04 — Define the Canonical Source-of-Truth Matrix
5. US-05 — Define the Supported V1 Scope Boundaries
6. US-06 — Decide the Mission Control Boundary and Adapter Stance
7. US-07 — Decide the Minimal Memory Model for V1
8. US-08 — Publish the Baseline-Ready V1 Architecture Decision Set

## Notes / open review questions

These are the things I want challenged in review:

- Is `YAGA-1` split at the right granularity, or should some stories merge?
- Is there too much documentation packaging work in `US-01` and `US-08`?
- Should the MC boundary be decided earlier than the current order?
- Is the memory story still too early for this epic?
- Are any of these stories really implementation stories disguised as decision stories?
