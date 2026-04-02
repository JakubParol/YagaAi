# 05 — Memory Model

## Memory Is Per-Agent

Memory is not shared by default. Each agent has its own memory store. This is a
deliberate architectural choice: it gives each agent a coherent, stable context
it can rely on, and prevents uncontrolled cross-agent contamination.

A shared-facts layer may exist as a governed exception (see below). It is not
the default interaction model.

## Memory Layers

| Layer | Meaning | Written by | Retention |
|-------|---------|-----------|-----------|
| **Working memory** | Current operational context; what the agent knows right now in this session | agent during session | session-scoped; may be promoted |
| **Episodic memory** | History of completed tasks and their outcomes | agent after task completion | durable, prunable |
| **Semantic / long-term memory** | Durable knowledge, decisions, preferences, and patterns | agent, with justification | durable, correctable |
| **Procedural memory / skills** | Validated ways of operating; effective patterns | agent or operator via improvement loop | durable, versioned |

These are conceptual layers. They may share underlying storage, but reads and writes
must respect the semantics of each layer.

## Event History Is Not Memory

The event log is the authoritative record of what happened during execution. Memory is
what an agent carries forward to inform future decisions.

They serve different purposes:

| | Event History | Memory |
|-|--------------|--------|
| Purpose | Execution trace, audit, replay | Inform future agent behavior |
| Mutability | Immutable (append-only) | Correctable |
| Source of truth for | What happened | Agent knowledge and preferences |
| Queried by | Operators, debuggers, replay | Agents during task execution |

Memory must never be the source of truth for task status or workflow state.
Operational state lives in the task store, not in memory.

## Write Policy

Not every event belongs in long-term memory. Durable memory writes should be justified.

Write to **episodic memory** when:
- a task completes with a notable outcome
- an approach failed and the reason is worth retaining
- a delegation produced an unexpected result

Write to **semantic memory** when:
- a decision was made that will affect future similar situations
- a preference, constraint, or fact about the domain is confirmed
- an operator explicitly promotes a fact

Write to **procedural memory** when:
- a sequence of steps proved effective and should be reused
- a pattern has been validated across multiple instances
- an improvement has passed review (see self-improvement loop)

Do **not** write to memory:
- every tool call
- every intermediate step of a task
- raw execution logs (those belong in event history)

## Read Policy

Agents should read memory selectively, not exhaustively. At the start of a task,
an agent may load:
- relevant working memory from prior sessions
- episodic memory related to the task type or domain
- procedural memory related to the expected execution approach

Memory reads should not substitute for reading current task state from the task store.
If there is a conflict between what memory says and what the task store says, the
task store wins.

## Correction and Retraction

Memory entries must be correctable and retractable:
- an agent may propose a correction to its own memory
- an operator may override or retract any memory entry
- retracted entries are marked as retracted, not deleted, for auditability
- corrections are versioned

Incorrect memory that affects behavior is a class of bug. The system must make
it possible to find and fix such entries without a full memory wipe.

## Shared Facts Layer

A shared-facts layer may be defined as a governed extension. If it exists:

| Aspect | Rule |
|--------|------|
| Who can propose | Any agent, with justification |
| Who can approve | James or a designated operator |
| Lifecycle | Versioned; retractable |
| When agents may rely on them | Only after promotion; not from proposal state |
| Conflicts | Resolved by James or operator, not automatically |

Shared facts are not a shortcut for lazy cross-agent communication. They are for
stable, validated, domain-level knowledge that multiple agents genuinely need.

## Self-Improvement and Memory

The self-improvement loop (see [10-governance-and-v1-boundaries.md](10-governance-and-v1-boundaries.md))
produces candidates for procedural memory and semantic memory updates.

Candidates go through review before promotion. An agent may not autonomously write
to its own procedural memory or overwrite semantic facts without approval.

Local working notes and heuristics (working memory) do not require review. Behavior
changes that affect routing, prompting, or skill execution do.

## Context Budget and Overflow Policy

Memory must be loaded into agent context selectively. Loading all memory is not viable
at scale and degrades model quality ("lost in the middle" effect).

**Context budget guidance per agent session:**

| Layer | Load policy | v1 limit (guideline) |
|-------|------------|----------------------|
| Working memory | All non-retracted entries for current session | Full |
| Procedural memory | All non-retracted entries for agent's domain | Full (small set) |
| Episodic memory | Most recent N entries matching task type | N = 3–5 |
| Semantic memory | Entries matching task domain keywords | Top-K relevant |

**Overflow policy:** If loading the full relevant memory set would exceed a practical
context budget, preference order is: procedural → working → episodic (recent) →
semantic (most specific). Never silently truncate without logging a `memory.context_overflow`
event.

**Session start:** At task start, the agent logs what memory was loaded and from which
layers. This is part of the prompt/context snapshot required for observability.

## Memory Integrity

Memory is a potential attack surface. Writes from external sources must be validated
before promotion to durable layers.

**Write source validation:**
- Content derived from user input (direct or via artifact) must not be promoted to
  semantic or procedural memory without explicit agent or operator confirmation
- Artifact content (e.g., text in a research report) is not trusted as a fact
  until an agent explicitly validates and promotes it
- Corrections proposed by the agent based on external content require the same review
  process as self-improvement candidates

**Retraction integrity:**
- Retracted entries carry: `retracted_by`, `retraction_reason`, `retracted_at`
- Retracted entries are never deleted; they remain in the store as audit records
- An agent that relies on a retracted entry (due to stale cache or bug) produces a
  `memory.stale_read` event — this is a bug, not a silent degradation

**Memory write failure policy:**
- A failed memory write does NOT block task completion
- The failure is logged as a `memory.write_failed` event
- The task moves to `Done` (or appropriate status); the write failure is surfaced to
  the operator independently
- The agent may retry the memory write independently of task status
