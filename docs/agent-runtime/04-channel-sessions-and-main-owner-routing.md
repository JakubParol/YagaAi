# 04 — Channel Sessions and Main-Owner Routing

## Purpose
Define the mandatory routing topology for user-originated requests that enter through channel/session surfaces such as Discord, WhatsApp, Teams, or web chat.

This note exists to prevent a specific class of architectural drift:
- channel sessions accidentally becoming durable owners of logic,
- specialist work being delegated surface-to-surface,
- reply routing being inferred instead of stored,
- ownership, memory, and callback semantics fragmenting across transport surfaces,
- transport-specific sessions becoming accidental sources of truth,
- reply publication becoming an implicit side effect instead of an explicit tracked concern.

This document is intentionally opinionated.
It sets the default topology for surface-originated work in v1.

---

## Core Rule

> **Channel sessions are ingress/egress adapters, not durable owners of agent logic.**
>
> **Durable, delegated, or otherwise non-trivial user-originated work must be normalized through the owning agent’s `main` session.**
>
> **Specialist delegation happens main-to-main, never channel-to-channel, unless an explicit exception is designed, approved, and documented.**

Short version:

> **Inbound through channel. Durable coordination through main. Specialist delegation main-to-main. Final reply through stored reply-target metadata.**

**One-main-per-agent invariant:**

> An agent has exactly one `main` coordination context regardless of how many channel or
> surface adapters are active. WhatsApp, Discord, web, Teams — each is an adapter, not
> a separate agent session. A message arriving via WhatsApp and a message arriving via
> Discord both normalize into the same owner `main`. The channel that carries the inbound
> message does not determine which coordination context handles the work.

---

## Key Clarification: Agent Owner vs Main Session

This document uses `agent:<id>:main` as the canonical coordination endpoint for an agent.
That does **not** mean the durable owner is the session object itself.

### Durable owner
The durable owner remains the **agent**.

### Main session
`agent:<id>:main` is the agent’s:
- canonical owner-facing session key,
- default coordination endpoint,
- default mailbox for durable routing,
- default place where owner-level reasoning and cross-agent coordination occur.

### Logical-endpoint clarification
In v1, `agent:<id>:main` should be treated as a **logical coordination endpoint**.
It may be implemented by one or more runtime sessions/processes as long as ownership, ordering, and audit invariants remain stable.
It is not itself the durable state object.

In other words:
- **owner = agent**
- **owner-facing coordination endpoint = agent’s `main` session key**
- **durable state must live in durable records, not only in a live session instance**

This distinction matters.
It prevents the architecture from silently turning session identity into the true ownership model.

---

## What Object This Document Governs

This document governs the routing topology of a **user-originated request record**.

### Request record
A **request** in this document is the ingress-scoped durable record for a user-originated unit of work.
It carries:
- request identity,
- ownership/routing metadata,
- callback metadata,
- reply-target metadata,
- publication state sufficient for retry/recovery.

### What request is not
A request is **not** a replacement for:
- `task`,
- `flow`,
- `handoff`,
- `event`,
- `artifact`.

Instead:
- a request may **create** or **reference** tasks, flows, and handoffs,
- a request may become the ingress/root context from which later work emerges,
- request-level routing/publication state may live alongside task/flow state rather than replacing it.

This document therefore does **not** introduce a second orchestration model on purpose.
It defines the request-level routing and reply-publication topology around user-originated work.

---

## Definitions

### Channel session
A session bound to a transport surface or surface context.
Examples:
- `agent:main:discord:<thread-or-channel-context>`
- `agent:main:whatsapp:<chat-context>`
- `agent:main:web:<conversation-context>`

A channel session is transport-aware.
It may hold presentation context and local conversation context.
It is **not** the durable owner of important work.

### Main session
The canonical owner-facing coordination endpoint for an agent.
Examples:
- `agent:main:main`
- `agent:naomi:main`
- `agent:amos:main`
- `agent:alex:main`

### Strategic owner
The agent currently accountable for the user request as a whole.
For James-routed user work, this is typically James.

### Execution owner
The specialist agent currently accountable for delegated execution work.
For example Naomi for implementation, Amos for QA, Alex for research.

### Reply target
The durable routing concept for the human-visible reply.
It is metadata, not transcript luck.
A reply target may resolve to a current publish-capable surface session, conversation, thread, or equivalent delivery endpoint.

### Reply session key
One concrete publish-capable endpoint that may currently satisfy the reply target.
It is a delivery mechanism, not the full durable routing concept.

### Callback target
The stored, explicit routing target for specialist completion or execution results.
This is usually the delegating owner’s `main` session.

### Surface session
A presentation-capable session that can publish to the original human-facing surface.
A reply target often resolves to a surface session, but the reply target is broader than a literal session key.

---

## Request Classification

Not all work needs the same routing treatment.
The system should classify requests explicitly.

### 1. Ephemeral / session-bound work
Work may remain surface-local only if it is all of the following:
- same-turn,
- non-delegated,
- does not create durable workflow obligations,
- does not require callback tracking,
- does not require audit/replay/recovery beyond ordinary transcript history,
- does not create or modify durable task / handoff / artifact / memory records.

Example:
- a trivial answer that can be produced immediately without delegation or durable workflow state.

### 2. Durable / delegated / non-trivial work
Work must normalize through the owner’s `main` session if any of the following is true:
- it may outlive the current interaction turn,
- it may require specialist delegation,
- it creates a task, handoff, or callback obligation,
- it may require retry, replay, recovery, or auditability,
- it may write durable memory or artifacts,
- it crosses agent boundaries,
- it may need follow-up after intermediate execution,
- it requires explicit reply routing beyond best-effort immediate response.

This is what this document means by **important work**.

---

## Main Rules

### Rule 1 — Channel sessions are surface adapters
A channel session exists to:
- receive inbound messages from a transport surface,
- collect transport and presentation metadata,
- create or forward a normalized request envelope,
- preserve reply-capable context,
- publish final or intermediate user-visible replies when instructed.

A channel session does **not** exist to:
- become the durable owner of strategic logic,
- become the authoritative source of ownership state,
- become the authoritative source of reply success state,
- delegate specialist work directly to another channel session as the primary pattern,
- become the canonical place where cross-agent coordination lives.

### Rule 2 — Durable coordination normalizes through `main`
For durable, delegated, or non-trivial user-originated work:
- the owning agent remains the durable owner,
- the agent’s `main` session key is the canonical coordination endpoint,
- the ingress channel session is not the durable owner.

For any owning agent, this means:
- user request enters through a channel/surface session for that agent,
- durable coordination normalizes into that agent’s `main` session key.

For example, the primary user-facing agent (`agent:main:main`) receives requests from
its WhatsApp, Discord, web, and other channel adapters — all into the same `main`.

### Rule 3 — Specialist delegation is owner-to-owner
When an owning agent delegates work to a specialist:
- delegation is from the strategic owner’s `main`,
- to the specialist agent’s `main`,
- not to channel/surface variants of those agents.

For example: strategic owner `main` → specialist `main` (implementation, QA, research, etc.)
Not: strategic owner Discord session → specialist Discord session.

### Rule 4 — Callback routing and human reply routing are separate
When specialist work completes:
- the result returns to the delegating owner,
- via the stored callback target,
- not directly to the human surface by default.

The owner then determines:
- whether to respond,
- what to say,
- whether to send an intermediate update,
- where the human-visible reply must be published,
- using stored reply-target metadata.

### Rule 5 — Reply routing must be explicit and durable enough for recovery
If the system may need to answer a human later, the reply target must be stored explicitly.
Do not rely on transcript luck, recent-message inference, or incidental session context.

---

## Canonical Mental Model

There are four separate concerns:

### 1. Strategic owner
The agent accountable for the request as a whole.

Example:
- any owning agent; in the primary user-facing flow this is the main user-facing agent (e.g., James)

### 2. Owner-facing coordination endpoint
The strategic owner’s canonical `main` session key.

Example:
- `agent:main:main`

### 3. Execution owner
The specialist agent accountable for delegated execution work.

Examples:
- Naomi
- Amos
- Alex

### 4. Presentation / reply surface
The session that can publish back to the human on the original transport surface.

Examples:
- `agent:main:discord:<thread-or-channel-context>`
- `agent:main:whatsapp:<chat-context>`
- `agent:main:web:<conversation-context>`

These must not be collapsed into one concept.

---

## Canonical Flow Example

### Example: Discord user asks the strategic owner agent for implementation help

This example uses agent IDs from the v1 setup (James as strategic owner, Naomi as
implementation specialist), but the topology applies to any owning agent pair.

#### Step 1 — Inbound via Discord channel session
`agent:<strategic-owner-id>:discord:...`
- receives the user message,
- captures transport metadata,
- creates a normalized request envelope,
- persists or emits enough routing metadata for recovery,
- dispatches the request to the strategic owner's `main`.

Minimum metadata should include:
- `request_id`
- `correlation_id`
- `causation_id` where applicable
- `dedup_key`
- `request_class`
- `origin_session_key`
- `reply_target`
- `reply_session_key`
- `origin_surface`
- `origin_conversation_id`
- `origin_message_id` where available
- `requester_agent_id`
- initial payload / user intent
- `contract_version`

#### Step 2 — Strategic owner `main` becomes the coordination endpoint
`agent:<strategic-owner-id>:main`
- accepts the normalized request,
- becomes the canonical coordination endpoint for the strategic owner,
- decides what to do,
- may answer directly or delegate.

If the task requires specialist work, the strategic owner sends a handoff to the
relevant specialist's `main` (e.g., `agent:<specialist-id>:main`).

The handoff should include:
- `goal`
- `definition_of_done`
- `request_id`
- `correlation_id`
- `causation_id`
- `callback_target = agent:<strategic-owner-id>:main`
- reply metadata needed for final routing, including:
  - `reply_target`
  - `reply_session_key`
  - `origin_surface`
  - `origin_conversation_id`
  - `origin_message_id` where available
  - `reply_target_version`

#### Step 3 — Specialist `main` owns specialist execution
`agent:<specialist-id>:main`
- accepts specialist ownership,
- performs work directly or spawns workers/sub-sessions,
- worker results return to this specialist's `main` (never directly to the strategic owner),
- returns the final result to the strategic owner's `main`.

The specialist does **not** send the default final user-facing reply directly to Discord.
The specialist does **not** route completion to a Discord channel session as the primary pattern.
The specialist answers the delegating owner.

#### Step 4 — Strategic owner `main` resolves final routing
`agent:<strategic-owner-id>:main`
- receives the result from the specialist,
- checks the stored request and reply metadata,
- determines where the user-visible reply must go,
- may issue an intermediate status update if needed,
- routes the publish instruction to the correct channel adapter.

#### Step 5 — Discord channel adapter publishes the reply
`agent:<strategic-owner-id>:discord:...`
- publishes the user-visible reply to the human on Discord,
- reports publish success or failure back to the owner-facing state path if required.

---

### Example: User sends via WhatsApp, reply goes back via WhatsApp

This example demonstrates the one-main invariant in action: the channel of origin does
not determine which coordination context handles the work — but the reply target is
captured at ingest and defaults to the originating channel.

#### Step 1 — WhatsApp channel adapter receives the message
`agent:<id>:whatsapp:...`
- receives the user message,
- captures transport metadata,
- creates a normalized request envelope,
- persists reply metadata pointing back to the originating channel:
  - `origin_surface = whatsapp`
  - `reply_target = whatsapp`
  - `reply_session_key = agent:<id>:whatsapp:<chat-context>`
- dispatches the normalized request to `agent:<id>:main`.

#### Step 2 — Main becomes the coordination endpoint
`agent:<id>:main`
- accepts the normalized request,
- receives the stored reply metadata,
- decides what to do: answer directly or delegate.

If work is delegated, the reply metadata travels with the handoff so it is available
when the result comes back.

#### Step 3 — Work is done, main decides the response
`agent:<id>:main`
- receives result (directly or via specialist callback),
- checks stored reply metadata: reply target is the WhatsApp channel,
- routes the publish instruction to the WhatsApp channel adapter.

#### Step 4 — WhatsApp channel adapter publishes
`agent:<id>:whatsapp:...`
- publishes the reply to the user on WhatsApp,
- reports publish success or failure back.

The WhatsApp adapter was never the coordination owner. The same `main` session handled
all coordination. The channel was only responsible for ingest and final delivery.

**Note on cross-channel replies:** Cross-channel delivery is only permitted when
explicitly commanded — for example, a user instruction such as "send the response to
agent X on channel Y." Even then, the instruction must be processed by `main` first:
`main` updates the stored `reply_target` and then routes the publish instruction to
the target channel adapter. There is no path where a channel adapter routes to another
channel adapter directly. `main` is always in the middle. The default remains: reply
via the channel that originated the request.

---

## Source-of-Truth Model

This rule requires a clear source-of-truth model.

### Authoritative records
For durable or delegated work, the following should be durable and queryable:
- request identity,
- strategic owner,
- execution owner if any,
- callback target,
- reply target,
- reply publication state,
- relevant event chronology.

### Practical mapping
At the architectural level, the intended split is:
- **request routing + reply publication state** -> durable request record or equivalent durable projection,
- **task / flow work state** -> task/flow system of record,
- **chronological evidence** -> event log / structured audit stream,
- **surface transcripts** -> non-authoritative presentation trace.

This document does not force one storage implementation, but it does require that the split above be explicit.

### Non-authoritative by default
The following are not sufficient as sources of truth for durable routing:
- channel transcripts,
- incidental session context,
- recent message scanning,
- surface-local memory only,
- human inference from conversation logs.

### Practical implication
The system should be able to recover routing decisions after restart or retry without depending on transcript reconstruction.

---

## Ingress Normalization Contract

Normalization from a channel session into `main` is not just an informal forward.
It is a contract boundary.

### Minimum expectations
1. The channel adapter captures enough metadata to identify and route the request durably.
2. The normalized request is persisted or otherwise made recoverable before the system treats it as safely handed off.
3. Acceptance by the owner-facing `main` endpoint should be explicit enough for retry and observability.
4. Duplicate inbound deliveries should coalesce by `dedup_key` or equivalent identity.
5. Until the request is durably accepted by the owner-facing path, the ingress side retains retry responsibility.

This document does not fully define the wire protocol or full state machine, but it does require explicit acceptance semantics.

---

## Metadata Requirements

At minimum, durable normalized requests should carry enough information to answer four separate questions.

### Required v1 fields
These should be treated as required for durable/delegated requests in v1:
- `request_id`
- `correlation_id`
- `dedup_key`
- `request_class`
- `contract_version`
- `strategic_owner_agent_id`
- `callback_target`
- `reply_target`
- `reply_publish_status`

### A. What request is this?
Identity fields:
- `request_id`
- `correlation_id`
- `causation_id` where applicable
- `dedup_key`
- `contract_version`
- `request_class`

### B. Who owns the work now?
Operational ownership fields:
- `requester_agent_id`
- `strategic_owner_agent_id`
- `current_owner_agent_id`
- `callback_target`

### C. Where should the human-visible reply go?
Reply-routing fields:
- `origin_session_key`
- `reply_target`
- `reply_session_key`
- `origin_surface`
- `origin_conversation_id`
- `origin_message_id` where available
- `reply_mode` if applicable
- `reply_target_version`
- `fallback_reply_target` if applicable

### D. What is the state of publishing?
Publication fields:
- `reply_publish_status`
- `reply_publish_attempt_count`
- `publish_dedup_key`
- `last_publish_attempt_at` if applicable
- `last_publish_error` if applicable

### Important note
`origin_session_key` and `reply_session_key` may often be the same, but they must not be treated as permanently identical.
Future scenarios may require them to differ.

`reply_target` and `reply_session_key` are also not identical:
- `reply_target` is the durable routing concept,
- `reply_session_key` is one current concrete delivery endpoint.

---

## Lifecycle and Canonical Events/Statuses

This document does **not** define a separate shadow state machine.
The request-level lifecycle described here must map onto the runtime’s canonical events and statuses defined elsewhere.

The labels in this document are therefore:
- routing-oriented projection labels,
- not permission to invent an unrelated parallel workflow engine.

### Practical request-level projection labels
A practical v1 projection may include:
- `inbound_received`
- `normalized`
- `owner_accepted`
- `delegated`
- `result_received`
- `reply_publish_pending`
- `reply_published`
- `reply_publish_failed`
- `fallback_required`
- `closed`

### Minimum required event hooks
The system should emit structured events for at least:
- request normalization attempted,
- request normalization accepted/rejected,
- owner handoff dispatched/accepted,
- reply target changed,
- reply publication attempted,
- reply publication succeeded/failed,
- fallback invoked.

### Required distinction
A successful specialist callback is **not** the same thing as a successful human-visible reply publication.

If specialist work succeeds but publish fails:
- the request is not fully resolved,
- the system must retain enough state to retry, escalate, or fall back,
- publication failure must remain observable as a first-class concern.

---

## Reply Publication Rules

### Publish dedup invariant
The same reply intent must not be published more than once without an explicit idempotency or `publish_dedup_key` rule.

### Publication state ownership
Channel adapters may perform the concrete publish operation, but publication success/failure must be reported back into durable request-level state or an equivalent durable projection.

### Closed-state expectation
A request should not be treated as fully closed merely because specialist work completed.
If the intended human-visible publish did not succeed, the request remains operationally unresolved until the publication concern is resolved or explicitly abandoned.

---

## Reply Target Mutation Rules

Reply routing is not immutable forever, but it must not be casually mutated.

### Default rule
Reply target metadata may be updated only by:
- the strategic owner,
- or a channel adapter acting on explicit strategic-owner instruction.

### Scope of mutation
By default, a reply target mutation applies to the current request only.
If the intent is to change the destination for a broader conversation or thread, that should be treated as an explicit conversation transfer rather than an implicit request-local mutation.

### Not allowed by default
Specialist agents should not mutate human reply routing metadata as part of normal execution.

### Audit expectation
If reply target changes, the system should preserve enough history to explain:
- previous target,
- new target,
- who changed it,
- why it changed.

---

## Fallback Policy

Fallback must not be a vague escape hatch.

### Default hierarchy
If primary reply publication fails:
1. retry against the intended reply target when safe,
2. use an explicit `fallback_reply_target` only if policy allows it,
3. if no valid fallback target exists, escalate to the strategic owner or operator path.

### Approval rule
Fallback should be governed by strategic-owner intent or platform policy, not by specialist discretion.

### Audit rule
When fallback is used, the system should preserve:
- the failed primary target,
- the fallback target used,
- why fallback was invoked,
- who or what authorized it.

---

## Failure Modes and Edge Cases

This document is about routing topology, but the topology must survive common failure modes.
At minimum, implementations must account for:

### Inbound / normalization failures
- duplicate inbound delivery,
- partial normalization,
- main endpoint unavailable,
- adapter restart after inbound receipt but before durable acceptance.

### Ownership / delegation failures
- callback arrives after cancel,
- callback arrives after reassignment,
- owner restart during in-flight delegated work,
- duplicate specialist completion.

### Reply routing failures
- reply target no longer exists,
- original thread/channel/chat archived or deleted,
- reply target rotated or remapped,
- publish succeeds late after retry ambiguity,
- publish fails after specialist success.

### Conversation continuity edge cases
- user sends follow-up while delegated work is still in flight,
- user continues same matter on another surface,
- origin session disappears but conversation remains logically recoverable,
- human-visible reply destination changes due to explicit conversation transfer.

### Minimum expectation
This document does not specify every recovery algorithm, but implementations must not assume ideal delivery, ideal sequencing, or transcript-based recovery.

---

## Continuity and Follow-Up Rules

The topology does not require global serialization across all work.
However, it does require request-level and conversation-level clarity.

### Default continuity rules
- A new follow-up message should create a new request unless the strategic owner explicitly merges it into an existing one.
- Cross-surface continuation should not silently mutate an existing reply target; it should create an explicit link or transfer decision.
- Multiple durable requests may exist within one broader conversation scope, but each must remain uniquely identifiable and auditable.

These defaults prevent ambiguous ownership and accidental cross-request mutation.

---

## Controlled Exceptions

The default rule is strong on purpose, but it is not meant to force hidden exceptions.
If an exception exists, it must be explicit.

Possible controlled exceptions may include:
- explicit conversation transfer,
- specialist-owned native surface designed as a first-class pattern,
- admin/debug lane,
- purely synchronous non-delegated surface-local handling.

### Exception rule
If a flow bypasses the default topology, it must be:
- intentional,
- documented,
- bounded,
- auditable,
- and preserve explicit owner, callback, reply-target, and recovery semantics.

### v1 baseline rule
In v1, exceptions should be rare and platform-level, not ad hoc per feature.
Ordinary feature work should not invent its own alternate routing topology.

Ad hoc surface-to-surface specialist routing is not an acceptable substitute for explicit exception design.

---

## Required Routing Rule

### Mandatory default rule

> **Do not route specialist work channel-to-channel as the default ownership path.**

Disallowed examples (surface-to-surface specialist routing):
- `agent:A:discord` → `agent:B:discord` (channel-to-channel delegation)
- `agent:A:whatsapp` → `agent:B:whatsapp` (same anti-pattern, different surface)
- `agent:B:discord` → `agent:A:discord` as the primary specialist callback path
- any surface-to-surface specialist routing used as the primary durable coordination pattern

Required default pattern:
- channel/session ingress -> owner main
- owner main -> specialist main
- specialist main -> owner main
- owner main -> original channel/session reply target

In short:

> **Inbound through channel. Durable coordination through main. Specialist delegation through main. Reply through stored surface target.**

---

## Why This Rule Exists

### The anti-pattern: per-surface session fragmentation

The alternative to this topology — where each channel or surface maintains its own session
with its own ownership, memory, and routing state — is called **per-surface session
fragmentation**.

In a fragmented model:
- the WhatsApp session owns WhatsApp requests
- the Discord session owns Discord requests
- memory fragments across surfaces
- callback routing fragments across surfaces
- the "same agent" becomes multiple disconnected centers of truth
- a user who switches surface mid-task loses context or gets inconsistent responses

This is the pattern this rule explicitly prevents. One agent, one `main`, many adapters.

### 1. Prevent ownership fragmentation
If channel sessions become owners, then the same agent starts having multiple accidental centers of truth.
That breaks predictability.

### 2. Preserve coherent memory and auditability
Durable memory and durable audit history should accumulate around durable ownership paths.
If important work is handled in surface-specific sessions, memory and traceability fragment across Discord, WhatsApp, web, and other entry points.

### 3. Keep callback semantics explicit
The specialist callback should return to the owner that requested the work, not to an incidental surface session that happened to carry the message.

### 4. Support multi-surface operation cleanly
One strategic owner should be able to serve multiple surfaces coherently.
That only remains stable if all durable work normalizes into the same owner-facing coordination path.

### 5. Keep channel adapters thin
Surface sessions should stay transport-aware, not orchestration-heavy.
Otherwise every new surface grows its own half-runtime and duplicates logic.

### 6. Make retries and recovery tractable
Stored routing metadata plus durable coordination paths are easier to recover than transcript inference or surface-local ownership hacks.

---

## Guardrails

### Guardrail 1 — Channel sessions are never the authoritative source of durable ownership state
A channel session may cache conversational context, but it must not become the authoritative owner/state store for durable work.

### Guardrail 2 — Channel transcripts are not a recovery mechanism
Never rely on “we can probably figure it out from recent messages.”
Transcript scanning is not a valid substitute for explicit routing metadata.

### Guardrail 3 — Specialist callbacks return to the delegating owner by default
The specialist result goes back to the owner that requested the work.
The owner decides the final user-facing reply.

### Guardrail 4 — Human reply routing and callback routing are separate concepts
A callback may target the owner’s `main` session key.
A human reply may target a surface session or another publish-capable target.
These are not interchangeable.

### Guardrail 5 — Surface variants of specialist agents are not the primary delegation topology
Even if channel-specific specialist sessions exist for some reason, they are not the canonical owner-to-owner routing path.

### Guardrail 6 — New channels must plug into the same topology
Adding a new surface must not create a new ownership model.
It should only add a new ingress/egress adapter.

### Guardrail 7 — Publish success is not implied by work success
The system must track reply publication separately from specialist completion.

### Guardrail 8 — `main` must not become a god-object
`main` owns coordination decisions and durable routing intent.
Low-level adapter publish execution and transport-specific delivery mechanics belong to channel/runtime layers and must report back via durable events/records.

---

## Minimal Implementation Shape

A practical v1 shape can be:

### Channel adapter responsibilities
- receive inbound message,
- collect transport metadata,
- classify request,
- create normalized request envelope,
- preserve reply-capable context,
- send to owning main session,
- publish final or intermediate reply when instructed,
- report publish result when required.

### Main owner responsibilities
- act as the canonical coordination endpoint for the strategic owner,
- own durable routing decisions,
- decide whether to answer directly or delegate,
- preserve callback and reply metadata,
- receive specialist result,
- decide final or intermediate user-facing response,
- instruct the correct channel session to publish it,
- handle retry / fallback escalation when publish fails.

### Specialist main responsibilities
- accept delegated work,
- perform or further delegate execution,
- return result to the delegating owner,
- avoid mutating human reply routing metadata,
- avoid direct user-surface reply unless an explicit exception model says otherwise.

---

## Relation to Mission Control

This document governs:
- request ingress,
- owner routing,
- callback routing,
- reply-target handling,
- reply publication state.

Mission Control or other workflow/task systems may govern:
- implementation workflow state,
- task decomposition,
- QA workflow,
- development execution history.

The intended split is:
- **request-level routing/publication state** remains governed by this topology,
- **work execution state** may be governed by Mission Control or task/flow systems.

The two must not compete to be the source of truth for the same concern.

---

## Recommended Invariants

The system should preserve these invariants:

1. **Every durable or delegated request has one strategic owner agent.**
2. **The owner agent’s `main` session key is the canonical coordination endpoint for that work.**
3. **Channel sessions are adapters, not durable strategic owners.**
3a. **An agent has exactly one `main` coordination context regardless of how many channel adapters are active. Adding a channel adds an adapter, not a new session.**
4. **Specialist delegation is main-to-main by default.**
5. **Specialist completion returns to the delegating owner by default.**
6. **Operational ownership and human reply routing are tracked separately.**
7. **Reply target metadata is explicit and durable enough for retry/recovery.**
8. **Successful callback completion does not imply successful reply publication.**
9. **Transcript inference is not a valid routing recovery strategy.**
10. **Adding a new transport surface does not create a new ownership model.**
11. **Exceptions to the default topology must be explicit, documented, bounded, and auditable.**
12. **The durable owner remains the agent, not the session object.**
13. **This document’s lifecycle labels must map to canonical events/statuses rather than create a shadow workflow engine.**
14. **The same reply intent must not publish twice without an explicit idempotency rule.**
15. **Follow-ups create new requests unless explicitly merged by the strategic owner.**

---

## Boundaries

### What this rule covers
This rule covers:
- user-originated requests entering through channel/surface sessions,
- request classification for surface-local vs durable work,
- normalization into owner-facing `main` sessions,
- owner-to-owner delegation,
- callback target and reply-target preservation,
- reply publication state and fallback expectations,
- the prohibition on default surface-to-surface specialist routing.

### What this rule does not fully define
This note does **not** fully define:
- the complete transport/wire protocol,
- the full task/workflow state machine,
- every retry algorithm,
- full artifact schema,
- the general workflow DSL,
- every system-originated event type,
- every storage implementation detail.

However, it **does** require:
- explicit durable routing metadata,
- explicit acceptance semantics for normalization,
- explicit separation between completion and publication,
- explicit source-of-truth boundaries,
- explicit ownership topology,
- and mapping to canonical runtime events/statuses.

### Important non-goals
This document does not authorize:
- surface-local orchestration shortcuts for durable work,
- transcript-based routing recovery,
- specialist-controlled reply-target mutation,
- ad hoc per-feature alternate routing models.

---

## Short Rule for Reuse Elsewhere

If a shorter wording is needed in other docs, use this:

> **User requests may enter through channel sessions, but any durable, delegated, or otherwise non-trivial work must normalize through the owning agent’s `main` session key. The durable owner remains the agent; `main` is the canonical coordination endpoint. Specialist delegation is main-to-main. Final user-visible replies are routed back through explicit stored reply-target metadata to the appropriate publish-capable surface endpoint. Channel-to-channel specialist routing is not an allowed default pattern.**

---

## Bottom Line

If a human message enters through Discord, WhatsApp, Teams, or web chat:
- it may enter through a channel session,
- but durable coordination must move into the owning agent’s `main` coordination path,
- specialist work must flow through specialist `main` paths by default,
- and the final reply must be routed back through explicit stored reply metadata.

Not Discord-to-Discord.
Not surface-to-surface.
Not “we’ll infer it later.”

**If the work matters, ownership stays coherent through `main`.**
