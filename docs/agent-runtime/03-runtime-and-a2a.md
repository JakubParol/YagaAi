# 03 — Runtime and Agent-to-Agent Communication

## Communication Model

The runtime uses four primitive message types:

| Type | Meaning | Initiator | Example |
|------|---------|-----------|---------|
| **command** | Intent to perform an action, addressed to an Aggregate. May be rejected — rejection always produces a `command.rejected` Domain Event | agent / adapter | `assign-task`, `request-review`, `publish-reply` |
| **event** | Immutable Domain Event fact that something happened; cannot be undone | agent / runtime / adapter | `handoff.accepted`, `reply.published` |
| **status** | Canonical snapshot of task or work-item state | task store / MC | `task:in-progress`, `us:code-review` |
| **artifact** | Result or reference to a result | producing agent | report, PR reference, test result |

Commands express intent. Events express facts. Status is derived state. Artifacts are outputs.
These must not be conflated.

The Command → Aggregate → Domain Event chain is the fundamental unit of state change. No
state change occurs without a Domain Event. A rejected Command produces a `command.rejected`
Domain Event. There are no silent operations.

The runtime must expose these semantics consistently across:
- built-in Web UI host
- CLI
- API
- adapter surfaces

For user-originated durable work, the runtime now exposes **two related but distinct contracts**:
1. **Ingress normalization contract** — surface adapter → owner main
2. **Owner-to-owner A2A / handoff contract** — owner main → specialist main

They are related, but they are not the same contract.

In all cases below, the authoritative durable object for user-originated routing/publication
state is the **request record**.

---

## Request Context Fields

For user-originated durable work, the following concepts must be carried explicitly and not
reconstructed from transcript luck:

| Field | Meaning |
|------|---------|
| `request_id` | Durable identity of the user-originated request |
| `correlation_id` | Execution lineage for the logical run / event tree |
| `origin_session_key` | Where the human-originated message first arrived |
| `request_class` | Request classification: `session-bound` or `durable` |
| `callback_target` | Where specialist completion returns operationally |
| `strategic_callback` | Terminal strategic notification target when distinct |
| `reply_target` | Durable human reply destination concept |
| `reply_session_key` | Current concrete publish-capable endpoint |
| `reply_publish_status` | Durable publication state |
| `publish_dedup_key` | Idempotency key for publication intent |

`request_id` and `correlation_id` are always distinct in v1.

---

## Ingress Normalization Contract

The ingress normalization contract — governing how surface/channel sessions write into
the request record and owner-main path — is defined in full in
[04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md).

Short version: a surface adapter receives the user message, creates the durable `request_id`,
persists reply-target metadata, and normalizes the work into the strategic owner’s `main`
endpoint. Normalization is accepted only when the request record exists durably and the
owner-main path has acknowledged it. Retries must be idempotent.

---

## Owner-to-Owner A2A / Handoff Contract

This contract governs durable delegation between owning agents.

### Handoff Contract

Every durable handoff must include at least:

| Field | Required | Notes |
|-------|----------|-------|
| `owner` | Yes | Agent taking execution ownership |
| `requester` | Yes | Agent requesting the work |
| `goal` | Yes | What needs to be accomplished |
| `definition_of_done` | Yes | Explicit acceptance criteria |
| `callback_target` | Yes | Operational result-routing destination |
| `priority` | Yes | Relative priority |
| `execution_mode` | Yes | `session-bound` or `detached` |
| `request_id` | For user-originated durable work | Durable request identity |
| `request_class` | If applicable | `session-bound` / `durable` |
| `input_artifacts` / `input_context` | If applicable | Work context |

See the canonical schema in [reference/handoff-contract.md](reference/handoff-contract.md).

### Relationship rules

The contract must preserve these distinctions:

- `callback_target` = where loop returns go operationally
- `strategic_callback` = where terminal strategic outcomes go when distinct
- `reply_target` = durable human reply destination concept
- `reply_session_key` = current concrete endpoint for publication

For user-originated durable work:
- `callback_target` normally points to the delegating owner’s `main` endpoint
- specialists may receive `request_id` inline and optionally a read-only routing snapshot from the request record
- specialists must **not** mutate reply routing directly by default
- authoritative reply-routing truth remains on the request record

### Acceptance semantics

A handoff is not complete at dispatch. It transitions through Domain Events:

```text
handoff.dispatched → pending → handoff.accepted | handoff.rejected → in-progress → done | failed | escalated
```

- **pending**: delivered, waiting for acknowledgment
- **accepted**: receiving agent takes formal ownership; corresponding task moves to `Accepted`
- **rejected**: receiving agent declines; ownership reverts to requester

`claimed` is not a v1 state. Use `accepted` for all ownership transfers.

### Callback model

Every non-trivial detached task has an explicit callback target. A callback is not optional.
When work completes, the owner sends a result event to the callback target with:
- the task reference
- the outcome status
- a reference to output artifacts
- a brief summary or reason if partial/failed
- the originating `request_id` when applicable

A callback returning to the owner does **not** imply that the human-visible reply has been published.
Those are separate concerns.

---

## Request Identity and Follow-Up Rules

### Default rule

A new follow-up human message creates a **new `request_id`** by default.

### Merge rule

The strategic owner may explicitly merge a follow-up into an existing request when:
- it is clearly the same in-flight work item,
- doing so improves continuity more than it harms audit clarity,
- the merge is recorded explicitly.

### Audit rule

When requests are merged, transferred, or continued cross-surface, the system must preserve:
- the original `request_id`
- the new/linked `request_id`
- who made the decision
- why it was done

Cross-surface continuation must not silently mutate an existing reply target without a recorded decision.

---

## Intermediate Publications

The runtime must distinguish final completion from intermediate user-visible updates under the same request.

**Chosen v1 stance:**
- intermediate status/progress updates are separate **publish attempts / reply intents** under the same `request_id`
- each publish attempt has its own `publish_dedup_key`
- the request record keeps the durable current publication summary
- publish-intent history lives in publication records / projections, not in one scalar field on `request`

This allows the owner to send progress updates without collapsing them into the final callback/completion semantics.

---

## Correlation, Causation, and Dedup

All structured messages must carry:

| Field | Purpose |
|-------|---------|
| `correlation_id` | Groups all events in one logical execution lineage |
| `causation_id` | Points to the event that caused this event |
| `dedup_key` | Enables idempotent processing; safe to redeliver |
| `version` | Contract version |

For user-originated durable work, the runtime must also preserve the `request_id` link.

### ID generation rules

| Field | Generated by | Notes |
|-------|-------------|-------|
| `request_id` | Ingress/owner normalization path | Durable identity for user-originated request |
| `correlation_id` | Strategic owner at normalization time | Logical execution lineage |
| `causation_id` | Sender | Triggering event ID |
| `dedup_key` | Sender | Stable across safe retry of the same intent |
| `publish_dedup_key` | Publisher / owner publish intent | Stable across mechanical retry of the same publish intent |
| `version` | Hardcoded | `v1` |

---

## Idempotency Domains

Idempotency is not one generic thing. The runtime must keep these domains distinct:

| Domain | Protected by |
|-------|---------------|
| inbound request normalization | request-level dedup key |
| handoff / callback processing | message `dedup_key` |
| reply publication | `publish_dedup_key` |

Receiving the same message twice in the same domain must produce the same outcome as receiving it once.

### Dedup Key Lifecycle

Dedup keys are not forever. The runtime must define a retention policy per domain:

| Domain | Key type | Minimum retention |
|--------|----------|-------------------|
| inbound normalization | request-level dedup key | until request is closed + replay window |
| handoff / callback | message `dedup_key` | until message is processed + replay window |
| reply publication | `publish_dedup_key` | until publication is terminal + replay window |

A "replay window" is a configurable grace period (e.g., 24h–7d) after terminal state during which
the system can safely reject redeliveries.

After the window expires, a replayed message should be treated as a **new event** and logged as an
anomaly, not silently deduplicated.

---

## Message Ordering Guarantees

The system does **not** guarantee global ordering across all agents or requests.
What it does guarantee per domain:

| Scope | Ordering guarantee |
|-------|--------------------|
| Within a single aggregate stream | Events are appended in stream order and replay preserves that stream order |
| Within a single `request_id` lifecycle | Publication state transitions are monotonic (no rollback to prior state) |
| Cross-agent A2A messages | No global ordering guarantee; each message is independently deduplicated |

`correlation_id` is for linkage and replay traversal, not a promise of one total ordering across all aggregates.
Replay should reconstruct best-effort causal order from aggregate-stream order, timestamps, and causation links.

**Out-of-order delivery handling:**
If a callback or event arrives after the state it references has already advanced, the system must:
- check whether the arriving event is still valid given current state,
- apply it if idempotent and consistent (e.g., a second "accepted" on an already-accepted task),
- discard with an audit log entry if it would violate state monotonicity,
- never silently apply an out-of-order event that could alter routing or publication state.

---

## Runtime-facing operational surfaces

Mission Control, future planning/control-plane integrations, and other runtime consumers should be able to interact through both:
- **API** — for UI, integrations, and external automation
- **CLI** — for agents and operators doing structured operational work

The Web UI host is a mandatory built-in runtime surface, but it should remain a consumer of the same stable runtime contracts rather than a separate orchestration authority.

## Owner-to-Owner Delegation vs Owner-to-Worker Execution

A2A contracts operate strictly at the **owning-agent layer**. Two things that look similar
are architecturally distinct:

**Owner-to-owner delegation** — an A2A handoff with an explicit contract:
- James main → Naomi main (implementation handoff with goal, definition of done, callback target)
- Naomi main → Amos main (handoff for code review / verify)

**Owner-to-worker execution** — an internal decision of the receiving owner, invisible to A2A:
- any owning agent may spawn one or more worker/sub sessions (for example: an
  implementation agent may spawn coding workers; a QA agent may spawn analysis workers)
- those workers may use any harness or backend (ACP, Claude Code, Codex, acpx)
- results always return to the spawning agent's `main`, never directly to the delegating
  agent above, Mission Control, or a channel adapter

This applies universally: the return path is always worker → spawning agent's `main`.
If agent A delegated to agent B, and B spawned workers, those workers report to B's `main`
— not to A. Agent B then reports back to A through the normal A2A callback path.

Worker spawning and harness choice do not produce A2A handoffs and do not transfer
ownership. Changing execution backend does not alter the ownership graph. The owner
remains accountable for the work regardless of which harness performed the execution.

---

## Detached vs Session-Bound Execution

The system supports two execution modes:

### Session-bound (synchronous short-turn)
- quick clarification or answer
- result returned within the same interaction context
- no durable specialist callback required

### Detached (async durable)
- background or non-trivial work
- explicit callback contract
- retry and recovery semantics apply
- request routing/publication state may outlive the current surface session turn

Detached runs are first-class. For important work, detached with a callback contract is the correct default.

---

## Example Flows

### Research request

```text
surface session receives user message
  → request normalized into agent:main:main
  → James delegates to agent:alex:main
  → Alex returns callback to agent:main:main
  → James decides final answer
  → surface adapter publishes via stored reply target
```

### Implementation request

```text
surface session receives user message
  → request normalized into agent:main:main
  → James delegates to agent:naomi:main
  → Naomi may delegate review/verify loop via Amos through MC
  → project/code/doc retrieval may be consulted through runtime indexing services
  → terminal callback returns to agent:main:main
  → James decides final or intermediate human-visible reply
  → surface adapter publishes via stored reply target
```

---

## Protocol Stance: Google A2A and MCP

The yaga.ai A2A protocol (commands / events / statuses / artifacts plus explicit request
routing/publication semantics) is an internal protocol.

**Current stance:**
- no Google A2A wire compatibility in v1
- no MCP endpoint compatibility in v1
- internal semantics prioritize explicit ownership, callback contracts, request routing,
  and replay/audit clarity over external protocol alignment

If external interoperability becomes necessary, translation should happen at the boundary,
not by distorting the internal model.
