# 11 — Implementation Decisions

This document records the architectural decisions that must be made before
implementation can begin. Each decision is a choice between concrete options —
leaving it open means the code will make it implicitly, which is worse.

This document is separate from the architecture docs because its content is
time-bound: once decisions are made, they become constraints visible in the code
and this document becomes a record of why, not what.

---

## Decision 1: Event Transport

**Question:** Through what mechanism do agents exchange events and commands?

**Options:**
- A: PostgreSQL table + LISTEN/NOTIFY — simple, no new infra, works well for 4 agents
- B: Redis Streams — durable, fast, but requires Redis
- C: In-process event bus — simplest for v1 if all agents run in one process
- D: NATS / RabbitMQ — full broker, overkill for v1

**Recommendation for v1:** Option A (PostgreSQL). MissionControl already uses PostgreSQL.
An `event_queue` table with LISTEN/NOTIFY per-agent channel gives durable delivery,
dedup via `dedup_key` lookup, and replay via table scan — all without new infrastructure.

**What this determines:** Implementation of retry, out-of-order handling, dedup storage,
and all event subscription code.

**Decision required before:** Any code touching `emit()`, `subscribe()`, or event consumers.

---

## Decision 2: Agent Deployment Model

**Question:** How does each agent "live" — is it always-on, event-driven, or on-demand?

**Options:**
- A: Each agent is a long-running process, always listening for events on its channel
- B: Each agent is invoked per-task (serverless-style) — started when there's work, exits when done
- C: One process hosts all agents as separate coroutines / threads

**Recommendation for v1:** Option A (long-running processes) or C (single process with
coroutine-per-agent). Option B requires a job runner and complicates memory continuity
(agent memory must be fully durable, nothing in-process). For 4 agents on one machine,
A or C is simpler.

**What this determines:** How "agent accepts handoff" is implemented — HTTP call to a
running process (A), job queue entry polled at startup (B), or in-process message (C).
Also determines session lifecycle: when does a session start and end.

**Decision required before:** Any scaffolding code for agents.

---

## Decision 3: Agent ↔ Execution Runtime Interface

**Question:** How does Naomi "use" Claude Code? How does James "talk to" the user?

This is the most critical missing decision. The entire failure/retry model depends on
the answer.

### James

James is the user-facing agent. Options:
- A: James runs as a CLI session — user types, James processes, responds
- B: James runs as a persistent process with an HTTP API — user messages come as requests
- C: James is triggered per-message (stateless, with memory loaded from store each time)

**What this determines:** Whether "James is unavailable" is even a possible state,
how the user interacts while Naomi works async, and what "session" means for James.

### Naomi

Naomi implements tasks using an execution runtime. Options:
- A: Naomi is a Claude API agent with a tool `run_claude_code(prompt, context) → result`
  — Claude Code is a synchronous tool call
- B: Naomi is a Claude API agent that spawns a Claude Code process async and polls for result
- C: Naomi is a thin orchestrator (Python) that builds prompts and calls Claude Code CLI directly,
  with no LLM of her own

**What this determines:** How execution timeout is detected (exception vs heartbeat),
how partial results are recovered, and what Naomi's "decision-making" looks like.

**Recommendation:** Option A for Naomi — Claude API agent where Claude Code is a tool.
This makes execution timeout = tool call timeout, recovery = retry the tool call,
and Naomi's reasoning is the LLM layer above.

### Amos

Amos reviews code and verifies functionality. Options:
- A: Amos is a Claude API agent with read-only tools: read artifact, read PR diff, write review
- B: Amos has no execution runtime — review is done by Claude reasoning over artifact content

Amos does NOT need a code execution runtime. Review and verify are analytical, not execution-based.
Amos may need: `read_artifact(ref)`, `read_pr_diff(ref)`, `write_review_comments(us_ref, comments)`.

### Alex

Alex does research. Options:
- A: Claude API agent with tools: `web_search(query)`, `read_document(url)`, `write_report()`
- B: Claude API agent using MCP tools for search and document access

**Decision required before:** Any agent implementation.

---

## Decision 4: Mission Control as Component

**Question:** Is MC a separate service or a library?

**Options:**
- A: MC is a library — agents import it and call `mc.transition(us_id, from, to, actor)`
- B: MC is a separate HTTP service — agents call it via API
- C: MC logic lives in the database as stored procedures / triggers

**Recommendation for v1:** Option A (library). One process, one deployment, no network
calls for state validation. Evolve to service (B) when there's a reason to deploy MC
independently (e.g., web UI needs direct MC access).

**What this determines:** Where process rules live (in-process vs over the wire),
how `transition.rejected` is surfaced (exception vs HTTP error), and how easy it is
to test MC rules in isolation.

**Decision required before:** Any MC state machine code.

---

## Decision 5: Memory Storage Schema

**Question:** What is the physical structure of agent memory?

**Recommended minimum schema (v1):**

```sql
CREATE TABLE agent_memory (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id    TEXT NOT NULL,
  layer       TEXT NOT NULL CHECK (layer IN ('working', 'episodic', 'semantic', 'procedural')),
  key         TEXT NOT NULL,
  value       JSONB NOT NULL,
  justification TEXT,
  version     INT  NOT NULL DEFAULT 1,
  replaces_id UUID REFERENCES agent_memory(id),
  retracted   BOOLEAN NOT NULL DEFAULT FALSE,
  retracted_by TEXT,
  retraction_reason TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by  TEXT NOT NULL
);

CREATE INDEX ON agent_memory (agent_id, layer, retracted);
CREATE INDEX ON agent_memory (agent_id, layer, key);
```

**Layer enforcement in v1:** The `layer` field is metadata for audit and context loading
heuristics. The code does not enforce different storage backends per layer. All layers
use the same table.

**Context loading in v1 (no vector search):**
- `working`: all non-retracted entries for agent where `session_id` matches
- `episodic`: last 5 non-retracted entries for agent ordered by `created_at DESC`
- `procedural`: all non-retracted entries for agent's domain
- `semantic`: all non-retracted entries for agent

Vector similarity for episodic/semantic retrieval is a v2 concern.

**Decision required before:** Any memory read/write code.

---

## v1 Decisions: What Is NOT in Scope

These choices are explicit to prevent scope creep:

| Feature | Decision | Notes |
|---------|----------|-------|
| `claimed` handoff state | Removed from v1 | Use `accepted` only |
| Out-of-order event buffering | Not in v1 | Log and discard; add if needed empirically |
| Contract version migration | Not in v1 | Hardcode `"v1"` everywhere |
| Shared facts governance code | Not in v1 | Keep the field, skip governance layer |
| Vector similarity memory retrieval | Not in v1 | Recency + domain tag lookup |
| Google A2A / MCP wire compatibility | Not in v1 | Internal protocol only |
| Multi-tenancy | Not in v1 | Internal use only |
| OpenTelemetry export | Not in v1, but design for compatibility | Use structured events that can be mapped to OTel spans later |
