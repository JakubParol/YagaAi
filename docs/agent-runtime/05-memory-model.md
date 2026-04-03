# 05 — Memory Model

## Memory Is Per-Agent

Memory is not shared by default. Each agent has its own memory store. This is a
deliberate architectural choice: it gives each agent a coherent, stable context
it can rely on, and prevents uncontrolled cross-agent contamination.

A shared-facts layer may exist as a governed exception. It is not the default interaction model.

## Memory Is Not the Same as Retrieval

Yaga needs retrieval on multiple planes, and they must not be collapsed into one giant blob.

The runtime should distinguish at least:
- **agent memory** — durable facts, preferences, decisions, lessons, procedures
- **project code index** — source code, symbols, AST-aware chunks, repo map
- **project knowledge/docs index** — architecture docs, ADRs, READMEs, specs
- **session/transcript search** — raw history for replay/debugging/fallback recall

These may share infrastructure, but they are not the same thing semantically.
Vectors are an index over these materials, not the source of truth.

## Memory Layers

| Layer | Meaning | Written by | Retention |
|-------|---------|-----------|-----------|
| **Working memory** | Current operational context within a session | agent during session | session-scoped; may be promoted |
| **Episodic memory** | History of completed tasks and notable outcomes | agent after task completion | durable, prunable |
| **Semantic / long-term memory** | Durable knowledge, decisions, preferences, patterns | agent, with justification | durable, correctable |
| **Procedural memory / skills** | Validated ways of operating | agent or operator via improvement loop | durable, versioned |

These are conceptual layers. They may share storage, but reads/writes must respect
layer semantics.

### Typed-memory direction

Long-term memory should trend toward **typed records**, not only free-form transcript fragments.
Useful memory categories include:
- fact
- preference
- decision
- lesson
- todo/reminder
- open_question
- project_note
- relationship/context

## Event History Is Not Memory

The event log is the authoritative record of what happened during execution.
Memory is what an agent carries forward to inform future decisions.

| | Event History | Memory |
|-|--------------|--------|
| Purpose | Execution trace, audit, replay | Inform future agent behavior |
| Mutability | Immutable (append-only) | Correctable |
| Source of truth for | What happened | Agent knowledge / preferences |
| Queried by | Operators, debuggers, replay | Agents during execution |

Memory must never be the source of truth for:
- task status
- workflow state
- request routing
- reply target
- reply publication state

Those belong in task stores, Mission Control, or the request record.

## Write Policy

Durable memory writes should be justified.

Write to **episodic memory** when:
- a task completes with a notable outcome
- an approach failed and the reason is worth retaining
- a delegation produced an unexpected result

Write to **semantic memory** when:
- a decision will affect future similar situations
- a preference, constraint, or domain fact is confirmed
- an operator explicitly promotes a fact

Write to **procedural memory** when:
- a sequence of steps proved effective and should be reused
- a pattern has been validated across multiple instances
- an improvement has passed review

Do **not** write to memory:
- every tool call
- every intermediate execution step
- raw execution logs
- reply-target or publish-status truth

## Read Policy

Agents should read memory selectively, not exhaustively.
At task start, an agent may load:
- relevant working memory from current context
- episodic memory related to the task type or domain
- procedural memory related to the expected approach

Memory reads do not substitute for reading current task/request state from the proper durable store.
If memory conflicts with task/request state, the durable operational store wins.

### Retrieval policy across planes

For code and project knowledge retrieval, the runtime should prefer a hybrid approach:
- lexical search (FTS/BM25)
- semantic search (embeddings)
- metadata/path filters
- repo-map / symbol awareness for code
- exact grep/symbol fallback when needed

Code retrieval should not rely on vectors alone.

## Correction and Retraction

Memory entries must be correctable and retractable:
- an agent may propose a correction to its own memory
- an operator may override or retract any memory entry
- retracted entries are marked as retracted, not deleted
- corrections are versioned

Incorrect memory that affects behavior is a class of bug.

## Shared Facts Layer

A shared-facts layer may be defined as a governed extension.
If it exists:

| Aspect | Rule |
|--------|------|
| Who can propose | Any agent, with justification |
| Who can approve | James or a designated operator |
| Lifecycle | Versioned; retractable |
| When agents may rely on them | Only after promotion |
| Conflicts | Resolved by James or operator |

Shared facts are not a shortcut for lazy cross-agent communication.

## Self-Improvement and Memory

The self-improvement loop produces candidates for procedural-memory and semantic-memory updates.

Candidates go through review before promotion. An agent may not autonomously overwrite
procedural memory or durable semantic facts without approval.

## Context Budget and Overflow Policy

Memory must be loaded selectively. Loading all memory is not viable at scale.

**Context budget guidance:**

| Layer | Load policy | v1 limit |
|-------|------------|----------|
| Working memory | Current session-relevant entries | Full |
| Procedural memory | Domain-relevant, non-retracted entries | Full (small set) |
| Episodic memory | Most recent matching entries | N = 3–5 |
| Semantic memory | Top-K relevant domain entries | selective |

If loading the full relevant set would exceed context budget, preference order is:
procedural → working → episodic → semantic.

Never silently truncate without logging a `memory.context_overflow` event.

For non-memory retrieval planes (project index / transcript search), the runtime should also surface retrieval truncation or stale-index conditions through structured diagnostics rather than failing silently.

## Indexing and Freshness

Because Yaga also vectorizes codebases and project knowledge, freshness is a first-class concern.

Indexed materials should track enough metadata to answer:
- what was indexed,
- when,
- with which parser/chunker version,
- with which embedding model/version,
- and whether the current source material has changed.

At minimum, indexed file/chunk metadata should include:
- path
- content hash
- size / mtime
- chunker/parser version
- embedding model/version
- last indexed timestamp

The system should support:
- dirty-file queues
- resumable indexing
- deleted-file tombstones
- periodic repair scans
- operator-visible stale-index diagnostics

## Memory Integrity

Memory is a potential attack surface.
Writes derived from external sources must be validated before promotion.

**Write source validation:**
- user-derived content must not be promoted to semantic/procedural memory without confirmation
- artifact content is not trusted as durable fact until validated
- corrections proposed from external content require the same review path as improvement candidates

**Retraction integrity:**
- retracted entries carry: `retracted_by`, `retraction_reason`, `retracted_at`
- retracted entries are never deleted
- an agent relying on a retracted entry should emit `memory.stale_read`

**Memory write failure policy:**
- failed memory write does not block task completion
- the failure is logged as `memory.write_failed`
- the agent may retry memory write independently of task completion

## Boundary Reminder for the Doc 12 Model

Memory may remember:
- outcomes
- user preferences
- lessons learned
- reusable procedures

Memory must **not** become the durable source of truth for:
- request routing
- callback routing contracts
- reply target
- reply publication state

Likewise, vector indexes for code, docs, or transcripts must not become the durable source of truth for workflow state. They are retrieval accelerators over canonical source material, not replacements for runtime state or human-readable records.