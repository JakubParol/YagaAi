# 12 — Channel Sessions and Main-Owner Routing

## Status
Draft architectural rule for v1 baseline.

## Purpose
Define the mandatory routing model for user-originated requests that enter through channel/session surfaces such as Discord, WhatsApp, Teams, or web chat.

This note exists to prevent a specific class of architectural drift:
- channel sessions accidentally becoming durable owners of logic,
- specialist work being delegated surface-to-surface,
- reply routing being inferred instead of stored,
- ownership, memory, and callback semantics fragmenting across transport surfaces.

The core rule is simple:

> **Channel sessions are ingress/egress adapters, not durable owners of agent logic.**
>
> **All important work is normalized into the owning agent’s main session.**
>
> **Specialist delegation happens main-to-main, never channel-to-channel.**

---

## Core Rule

### 1. Channel session is a surface adapter
A channel session exists to:
- receive inbound messages from a transport surface,
- preserve surface context needed for replying,
- publish normalized requests into the owning agent’s main session,
- deliver final user-visible replies back to the original surface.

A channel session does **not** exist to:
- become the durable owner of strategic logic,
- hold the authoritative lifecycle state of important work,
- delegate specialist work directly to another channel session,
- become the canonical place where cross-agent coordination lives.

### 2. Durable ownership lives in the agent’s main session
For any important user-originated request:
- the durable owner is the owning agent’s `main` session,
- not the channel/session-specific ingress surface.

For James, this means a user request that arrives through Discord, WhatsApp, Teams, or web chat must be normalized into `agent:main:main`.

### 3. Specialist delegation is owner-to-owner through main sessions
If James delegates implementation, QA, or research:
- James delegates from `agent:main:main`,
- to `agent:naomi:main`, `agent:amos:main`, or `agent:alex:main`,
- not to Discord/WhatsApp/web variants of those agents.

### 4. Final reply is routed back through stored reply metadata
When specialist work completes, the result returns to the owner that requested it.
That owner then uses stored reply-target metadata to send the final user-visible reply back through the original channel session.

This means callback routing and user-facing reply routing are related, but not the same thing.

---

## Canonical Mental Model

There are three separate concerns:

### 1. Strategic owner
The durable owner of the user request.

Example:
- `agent:main:main`

### 2. Execution owner
The durable specialist owner of delegated work.

Examples:
- `agent:naomi:main`
- `agent:amos:main`
- `agent:alex:main`

### 3. Presentation / reply surface
The session that can publish back to the human on the original transport surface.

Examples:
- `agent:main:discord:<thread-or-channel-context>`
- `agent:main:whatsapp:<chat-context>`
- `agent:main:web:<conversation-context>`

These must not be collapsed into one concept.

---

## Canonical Flow Example

### Example: Discord user asks James for implementation help

#### Step 1 — Inbound via Discord James session
`agent:main:discord:...`
- receives the user message,
- creates or forwards a normalized request envelope,
- assigns/propagates identifiers and reply metadata,
- forwards the request to `agent:main:main`.

Minimum carried metadata should include:
- `request_id`
- `correlation_id`
- `origin_session_key`
- `reply_session_key`
- `origin_surface`
- `origin_conversation_id`
- `origin_message_id` where available
- `requester_agent_id`
- initial payload / user intent

#### Step 2 — Main James becomes strategic owner
`agent:main:main`
- becomes the strategic owner of the request,
- decides what to do,
- may answer directly or delegate.

If the task is implementation work, James sends a handoff to `agent:naomi:main`.

The handoff should include:
- `goal`
- `definition_of_done`
- `correlation_id`
- `request_id`
- `callback_target = agent:main:main`
- reply metadata needed later by James, including:
  - `origin_session_key`
  - `reply_session_key`
  - `origin_surface`
  - `origin_conversation_id`

#### Step 3 — Main Naomi owns specialist execution
`agent:naomi:main`
- accepts specialist ownership,
- performs work directly or spawns a worker/runtime,
- returns the result to `agent:main:main`.

Naomi does **not** send the final user-facing reply directly to Discord.
Naomi does **not** route completion to a Discord Naomi session.
Naomi answers the owner that delegated the work.

#### Step 4 — Main James resolves final routing
`agent:main:main`
- receives the result from Naomi,
- checks the stored request/reply metadata,
- determines where the user-visible reply must go,
- routes the user-facing response to the original Discord James session.

#### Step 5 — Discord James session publishes the reply
`agent:main:discord:...`
- sends the final reply to the user on Discord.

---

## Required Routing Rule

### Mandatory rule

> **Do not route specialist work channel-to-channel.**

Disallowed examples:
- Discord James -> Discord Naomi
- WhatsApp James -> WhatsApp Naomi
- Discord Naomi -> Discord James as the specialist callback path
- any surface-to-surface specialist routing used as the primary ownership path

Required pattern:
- channel/session ingress -> owner main
- owner main -> specialist main
- specialist main -> owner main
- owner main -> original channel/session reply target

In short:

> **Inbound through channel. Ownership in main. Delegation through main. Reply through stored surface target.**

---

## Why This Rule Exists

### 1. Prevent ownership fragmentation
If channel sessions become owners, then the same agent starts having multiple accidental centers of truth.
That breaks predictability.

### 2. Preserve coherent memory
Durable memory should accumulate around durable owners.
If important work is handled in surface-specific sessions, memory and context fragment across Discord, WhatsApp, web, and other entry points.

### 3. Keep callback semantics explicit
The specialist callback should return to the owner that requested the work, not to some incidental surface session that happened to carry the message.

### 4. Support multi-surface operation cleanly
One strategic James should be able to serve multiple surfaces:
- Discord
- WhatsApp
- Teams
- web chat

That only remains coherent if all of them normalize into the same durable owner.

### 5. Keep channel sessions thin
Surface sessions should stay transport-aware, not orchestration-heavy.
Otherwise every new surface grows its own half-runtime and duplicates logic.

---

## Data / Metadata Requirements

At minimum, any important normalized request should carry enough information to answer two separate questions:

### A. Who owns the work now?
Operational ownership fields:
- `request_id`
- `correlation_id`
- `requester_agent_id`
- `current_owner_agent_id`
- `callback_target`

### B. Where should the human-visible reply go?
Reply-routing fields:
- `origin_session_key`
- `reply_session_key`
- `origin_surface`
- `origin_conversation_id`
- `origin_message_id` where available

### Important note
`origin_session_key` and `reply_session_key` may often be the same, but they must not be treated as permanently identical.

The system should allow them to differ in future scenarios.

---

## Boundaries

### What this rule covers
This rule covers:
- user-originated requests entering through channel/surface sessions,
- normalization into owner sessions,
- owner-to-owner delegation,
- reply-target preservation,
- the prohibition on surface-to-surface specialist routing.

### What this rule does not cover
This note does **not** define:
- the full transport/wire protocol,
- the full task state machine,
- retry semantics,
- artifact schema,
- general workflow DSL,
- every possible system-originated event.

It only fixes the ownership/routing topology for surface-originated work.

---

## Guardrails

### Guardrail 1 — Channel sessions are never the authoritative source of ownership state
A channel session may cache conversational context, but it must not become the authoritative owner/state store for important work.

### Guardrail 2 — Specialist callbacks return to the delegating owner, not directly to the user surface
The specialist result goes back to the owner that requested it.
The owner decides the final user-facing reply.

### Guardrail 3 — Reply routing must be stored, not inferred later from transcript luck
If the system needs to answer a human, the reply target must be carried explicitly in metadata.
Never rely on “we can probably figure it out later from chat context.”

### Guardrail 4 — Surface variants of specialist agents are not the primary delegation topology
Even if channel-specific specialist sessions exist for some reason, they are not the canonical owner-to-owner routing path.

### Guardrail 5 — Callback routing and human reply routing are separate concepts
A callback may target the owner session.
A human reply may target a channel session.
These are not interchangeable.

### Guardrail 6 — New channels must plug into the same topology
Adding a new surface must not create a new ownership model.
It should only add a new ingress/egress adapter.

---

## Anti-Patterns / Explicitly Disallowed

### Anti-pattern A — Discord-to-Discord specialist delegation
Example:
- `agent:main:discord:*` -> `agent:naomi:discord:*`

Why it is wrong:
- it bypasses durable owner routing,
- fragments memory,
- makes callback ownership ambiguous,
- encourages surface-local orchestration drift.

### Anti-pattern B — Specialist replying directly to the human surface when James owns the request
Example:
- Naomi completes work and pushes directly to Discord user context.

Why it is wrong:
- bypasses strategic owner review,
- breaks the owner-first model,
- makes it unclear who is accountable for the final answer.

### Anti-pattern C — Inferring reply destination from incidental session context
Example:
- James gets a result and tries to guess where to post it by scanning recent transcripts.

Why it is wrong:
- brittle,
- hard to debug,
- unsafe under retries, replays, and multi-surface concurrency.

---

## Minimal Implementation Shape

A practical v1 shape can be:

### Channel adapter responsibilities
- receive inbound message
- collect transport metadata
- create normalized request envelope
- send to owning main session
- publish final reply when instructed

### Main owner responsibilities
- own the request
- decide route / specialist
- preserve callback and reply metadata
- receive specialist result
- produce final user-facing response
- instruct the correct channel session to publish it

### Specialist main responsibilities
- accept delegated work
- perform or further delegate execution
- return result to delegating owner
- avoid direct user-surface reply unless explicitly designed otherwise

---

## Recommended Invariants

The system should preserve these invariants:

1. **Every important request has one durable strategic owner.**
2. **Channel sessions are adapters, not durable strategic owners.**
3. **Specialist delegation is main-to-main.**
4. **Specialist completion returns to the delegating owner.**
5. **Reply target metadata is explicit and durable enough for retries/recovery.**
6. **Operational ownership and user-visible reply routing are tracked separately.**
7. **Adding a new transport surface does not create a new ownership model.**

---

## Short Rule for Reuse Elsewhere

If a shorter wording is needed in other docs, use this:

> **Inbound user requests may enter through channel sessions, but important work must be normalized into the owning agent’s main session. Specialist delegation is main-to-main. Final user-visible replies are routed back through stored reply-target metadata to the original surface session. Channel-to-channel specialist routing is not an allowed primary pattern.**

---

## Bottom Line

If a human message enters through Discord, WhatsApp, Teams, or web chat:
- it may enter through a channel session,
- but ownership must move into the owning agent’s main session,
- specialist work must flow through specialist main sessions,
- and the final reply must be routed back through explicit stored reply metadata.

Not Discord-to-Discord.
Not surface-to-surface.
Not “we’ll infer it later.”

**Through main. Always.**
