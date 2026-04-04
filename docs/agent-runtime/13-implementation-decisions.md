# 13 — Implementation Decisions

This document records the implementation decisions that must be made before
architecture prose turns into code.

For the channel session routing integration (see `04-channel-sessions-and-main-owner-routing`),
the most important rule is simple:

> **If a decision affects `02`, `03`, `10`, or `11`, it must be explicit here first.**

Leaving a decision open does not keep the system flexible. It guarantees that the code
or downstream docs will make the choice implicitly.

---

## Phase 0 Gating Decisions for Request / Routing / Publication

These are the blocking v1 decisions for integrating the channel session routing model
(see [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md)).

### Decision 1 — `request_id` vs `correlation_id`

**Chosen v1 stance:** They are **always distinct**.

- `request_id` identifies the user-originated request record.
- `correlation_id` groups the execution/event tree for one logical run.
- In v1, a durable user-originated request creates one primary correlation scope when it
  is normalized into the owner-facing path.
- Subsequent events for the same delegated work normally reuse that correlation scope.
- If a future sub-flow needs a separate correlation scope, it must still retain the
  originating `request_id` link.

**Why:**
- Operators need a stable request identity even if execution splits, retries, or fans out.
- `request_id` is the human/request routing identity.
- `correlation_id` is the execution lineage identity.

**Implication for docs:**
- `09` must expose both.
- `03` must stop treating `correlation_id` as a sufficient stand-in for request identity.

---

### Decision 2 — Request-state shape

**Chosen v1 stance:** Use a **first-class persisted request record**.

The request record is the durable source of truth for:
- request identity,
- origin session metadata,
- reply target metadata,
- publication state,
- strategic owner pointer,
- links to execution state.

It is not a replacement for tasks, flows, or events.

**Why:**
- It gives one durable home for routing and publication truth.
- It avoids reconstructing routing state from transcripts.
- It keeps request/publication concerns out of Mission Control, memory, and artifacts.

**Implication for docs:**
- `02` can now use the concrete term **request record**, not only “equivalent durable projection”.

---

### Decision 3 — Publication-state owner / writer

**Chosen v1 stance:** The **request-state writer on the owner-side runtime path** is the
canonical writer of `reply_publish_status`.

Concretely:
- the channel/surface adapter performs the concrete publish operation,
- the adapter emits publish result events,
- the owner-side request-state path records the durable publication state.

Channel adapters are therefore execution actors for publication, but **not** the
authoritative store of publication truth.

**Why:**
- It keeps channel sessions thin.
- It prevents transport-local state from becoming the real source of truth.
- It supports restart/recovery without depending on a live adapter process.

---

### Decision 4 — Publication-state vocabulary

**Chosen v1 stance:** The v1 publication-state vocabulary is:
- `pending`
- `attempted`
- `published`
- `failed`
- `unknown`
- `fallback_required`
- `abandoned`

**Interpretation:**
- `pending` = publish intent exists, not yet attempted
- `attempted` = at least one concrete publish attempt has been made, no terminal outcome yet
- `published` = intended human-visible reply confirmed published
- `failed` = publish attempt ended in a known failure state
- `unknown` = publish outcome is ambiguous and must be reconciled
- `fallback_required` = primary route is no longer valid/safe; owner or operator action needed
- `abandoned` = reply will no longer be attempted by design/policy

**Why:**
- `08`, `09`, and request-level observability need concrete states, not vague prose.

---

### Decision 5 — Publish retry authority

**Chosen v1 stance:** Retry authority is split.

#### Mechanical retry
The publish-capable runtime/adapter path may perform a **bounded mechanical retry**
without re-entering owner reasoning only when all of the following are true:
- the reply content is unchanged,
- the reply target is unchanged,
- the same `publish_dedup_key` is reused,
- the retry is transport-safe and idempotent,
- no fallback or semantic routing decision is required.

#### Strategic retry / fallback
Owner reasoning is required when:
- the reply target must change,
- fallback must be invoked,
- the content should change,
- the prior outcome is ambiguous in a way that could duplicate a human-visible message,
- policy or operator approval is required.

**Why:**
- This keeps the common retry case cheap without letting adapters make strategic routing decisions.

---

### Decision 6 — Reply-metadata carriage model in handoffs

**Chosen v1 stance:** Use a **mixed model**.

For user-originated durable work:
- handoffs must carry `request_id` inline,
- may carry `request_class` inline,
- may carry a read-only routing snapshot if useful,
- but the authoritative reply-routing truth remains in the request record.

Default v1 rule:
- specialists receive **pointer-first** routing context,
- `reply_session_key` may be present as an advisory/read-only snapshot,
- specialists must not mutate reply routing directly.

**Why:**
- Inline `request_id` keeps joins easy.
- Pointer-first routing avoids bloating handoffs with mutable routing baggage.

---

### Decision 7 — Authoritative vs derived ownership in request state

**Chosen v1 stance:** `current_owner_agent_id` in request state is **derived/mirrored**, not authoritative.

The authoritative split is:
- `strategic_owner_agent_id` in the request record = authoritative for request-level accountability
- task/flow/MC ownership = authoritative for execution ownership and current work state
- `current_owner_agent_id` in request state = convenience projection for request-level observability

**Why:**
- This avoids a second ownership authority competing with task/flow systems.

---

### Decision 8 — `reply_target` vs `reply_session_key`

**Chosen v1 stance:**
- `reply_target` is the durable routing concept.
- `reply_session_key` is the current concrete publish-capable endpoint that satisfies that target.

The target may remain stable while the session key rotates.

**Why:**
- Durable routing should not depend on one literal session key staying valid forever.

---

### Decision 9 — Persistence and restart recovery

**Chosen v1 stance:** After restart, the system must be able to reconstruct request
routing/publication state from:
- the request record,
- the event log,
- task/flow state,
without depending on transcript reconstruction.

Transcripts may help debugging, but they are not the recovery mechanism.

---

## Summary Table — Phase 0 Decisions

| Decision | Chosen v1 stance |
|---|---|
| `request_id` vs `correlation_id` | Always distinct |
| Request-state shape | First-class persisted request record |
| Publication-state writer | Owner-side request-state writer; adapters emit result events |
| Publication-state vocabulary | `pending`, `attempted`, `published`, `failed`, `unknown`, `fallback_required`, `abandoned` |
| Publish retry authority | Mechanical retry allowed in bounded/idempotent cases; fallback/semantic retry requires owner reasoning |
| Handoff routing carriage | Mixed model: inline `request_id`, pointer-first routing truth |
| `current_owner_agent_id` in request state | Derived/mirrored, not authoritative |
| `reply_target` vs `reply_session_key` | Durable concept vs current concrete endpoint |
| Restart recovery | Request record + event log + task state; no transcript dependency |
| Event transport | SQLite-first durable event log + job tables |
| Mission Control shape | Integrated runtime module with API + CLI |
| Memory/retrieval model | See `07-memory-model-and-vectorization` |
| Vectorization storage | See `07-memory-model-and-vectorization` |
| Web UI host | Mandatory built-in runtime surface |

---

## Additional Implementation Decisions

The following pre-existing implementation decisions remain relevant to the runtime
beyond the channel session routing integration.

### Decision 10 — Event transport

**Chosen v1 stance:** SQLite-first durable event log + job tables inside the local runtime.

Use a durable event log / job queue backed by the runtime’s local store with:
- append-only event records
- dedup via `dedup_key`
- replay via table scan
- scheduled jobs for retries, watchdogs, and timeout handling

Default v1 storage shape should be lightweight and local-first.
PostgreSQL may exist later as an advanced deployment mode, but it is not the default architectural center.

---

### Decision 11 — Agent deployment model

**Chosen v1 stance:** Long-running agent processes or one host process with
stable per-agent workers.

The system should not assume serverless per-task cold starts for v1. Durable owners
need stable coordination endpoints and predictable event consumption.

---

### Decision 12 — Agent ↔ execution runtime interface

**Chosen v1 stance:** All named agents in v1 (James, Naomi, Amos, Alex) are normal durable
agents with the same architectural standing. Their differences are responsibility-domain
differences, not architectural-species differences.

Any agent may use worker/sub sessions and harnesses/backends when appropriate for
their domain:
- James: user-facing coordination; orchestration and delegation work
- Naomi: implementation domain; commonly uses code-execution backends (ACP, Claude Code,
  Codex, acpx, etc.) via worker sessions
- Amos: review/verify domain; uses analytical and read/review tools
- Alex: research domain; uses search, read, and synthesis tools

Harness/backend choice is an internal execution concern of the owning agent. Execution
runtimes and worker sessions are subordinate to the owning agent and are not durable
owners. Changing execution backend does not require changing the ownership model, the
A2A contract layer, or Mission Control records.

---

### Decision 13 — Mission Control as component

**Chosen v1 stance:** Mission Control remains the authoritative workflow state component
for the development flow, but in the target product shape it should be integrated as a runtime module rather than a mandatory heavy multi-service stack.

The critical architectural constraint is not deployment shape. It is that MC remains the
source of truth for US/task workflow state in the dev flow.

Mission Control must be reachable through both:
- API
- CLI

The built-in Web UI host is the primary operator/admin/configuration surface over Mission Control and runtime state.

---

### Decision 14 — Memory, retrieval, and vectorization

See [07-memory-model-and-vectorization.md](07-memory-model-and-vectorization.md) for the full
memory model, retrieval planes, vectorization stack, index freshness, and failure/recovery model.

Summary: memory is layered and per-agent; retrieval operates on four separate planes; the default
stack is SQLite + FTS5 + sqlite-vec; vectors are an index, not the source of truth.

### Decision 15 — Web UI host

**Chosen v1 stance:** The Web UI host is mandatory.

It is a built-in runtime surface for:
- management
- administration
- configuration
- Mission Control operator workflows
- memory/index diagnostics
- repair/recovery actions

It must stay simple and must not force the runtime back into a heavy split-service web platform by default.

## What v1 Explicitly Does Not Do

| Feature | Decision | Notes |
|---------|----------|-------|
| Request inferred from transcript only | Not allowed | Durable routing/publication needs a request record |
| Channel session as durable owner | Not allowed | Channel sessions are surface adapters |
| Specialist mutation of reply routing | Not allowed by default | Owner path controls routing changes |
| Request lifecycle as task status set | Not allowed | Request projection != canonical task statuses |
| Generic second workflow engine | Not in v1 | Request layer is routing/publication, not orchestration replacement |
| Transcript-based restart recovery | Not in v1 | Recovery must work from durable records |
| Automatic cross-surface retargeting | Not in v1 by default | Requires explicit transfer or fallback decision |
| Unlimited autonomous publish retry | Not in v1 | Retry authority is bounded and policy-driven |
| Docker/Redis/Dapr mandatory local install | Not in v1 default | Baseline Linux/macOS install must stay lightweight |
| External vector DB as default | Not in v1 default | Local-first retrieval/indexing is the baseline |