# 07 — Memory Model & Vectorization

## Core Principle

Yaga does not treat memory as one giant blob.

There are four distinct retrieval planes. They may share infrastructure, but they must not be
conflated conceptually:

- **agent memory** — durable facts, preferences, decisions, lessons, procedures
- **project code index** — source files, symbols, AST-aware chunks, repo map
- **project knowledge/docs index** — architecture docs, ADRs, READMEs, specs
- **session/transcript search** — raw interaction history for replay, debugging, fallback recall

Vectors are an index over these materials, not the source of truth.

---

## Part 1 — Memory Model

### Memory Is Per-Agent

Memory is not shared by default. Each agent has its own memory store. This is a
deliberate architectural choice: it gives each agent a coherent, stable context
it can rely on, and prevents uncontrolled cross-agent contamination.

A shared-facts layer may exist as a governed exception. It is not the default interaction model.

### Memory Layers

| Layer | Meaning | Written by | Retention |
|-------|---------|-----------|-----------|
| **Working memory** | Current operational context within a session | agent during session | session-scoped; may be promoted |
| **Episodic memory** | History of completed tasks and notable outcomes | agent after task completion | durable, prunable |
| **Semantic / long-term memory** | Durable knowledge, decisions, preferences, patterns | agent, with justification | durable, correctable |
| **Procedural memory / skills** | Validated ways of operating | agent or operator via improvement loop | durable, versioned |

These are conceptual layers. They may share storage, but reads/writes must respect
layer semantics.

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

### Event History Is Not Memory

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

### Write Policy

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

### Read Policy

Agents should read memory selectively, not exhaustively.
At task start, an agent may load:
- relevant working memory from current context
- episodic memory related to the task type or domain
- procedural memory related to the expected approach

Memory reads do not substitute for reading current task/request state from the proper durable store.
If memory conflicts with task/request state, the durable operational store wins.

### Correction and Retraction

Memory entries must be correctable and retractable:
- an agent may propose a correction to its own memory
- an operator may override or retract any memory entry
- retracted entries are marked as retracted, not deleted
- corrections are versioned

Incorrect memory that affects behavior is a class of bug.

### Shared Facts Layer

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

### Self-Improvement and Memory

The self-improvement loop produces candidates for procedural-memory and semantic-memory updates.

Candidates go through review before promotion. An agent may not autonomously overwrite
procedural memory or durable semantic facts without approval.

### Context Budget and Overflow Policy

Memory must be loaded selectively. Loading all memory is not viable at scale.

| Layer | Load policy | v1 limit |
|-------|------------|----------|
| Working memory | Current session-relevant entries | Full |
| Procedural memory | Domain-relevant, non-retracted entries | Full (small set) |
| Episodic memory | Most recent matching entries | N = 3–5 |
| Semantic memory | Top-K relevant domain entries | selective |

If loading the full relevant set would exceed context budget, preference order is:
procedural → working → episodic → semantic.

Never silently truncate without logging a `memory.context_overflow` event.

### Memory Integrity

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

---

## Part 2 — Retrieval & Vectorization

### Product Requirements

The memory and retrieval architecture must support:

- local-first operation
- Linux and macOS installs
- one-command setup
- low operational overhead
- strong operator inspectability
- hybrid retrieval quality
- fast incremental refresh
- durability across restarts
- recovery from stale or broken indexes

This pushes toward embedded/local storage first, not a server-heavy vector stack by default.

### Recommended Stack: SQLite + FTS5 + sqlite-vec

For Yaga v1, the default stack is:

- **SQLite + WAL**
- **FTS5** for lexical retrieval
- **sqlite-vec** for semantic retrieval
- metadata/path filters
- optional rank fusion / weighted merge
- repo map + symbol graph + grep fallback for code navigation

This applies to both project vectorization and agent memory retrieval.

This gives:
- zero external DB requirement
- simple install
- easy debugging
- good local performance
- one product / one state directory mental model
- a path to later upgrades without overcommitting too early

### Storage Model

**Global runtime DB** (`~/.yaga/state.db`):
- agents, sessions, requests
- tasks / flows / runs
- memory records, memory embeddings, memory FTS indexes
- retrieval diagnostics, indexing jobs
- failures / repair markers

**Per-project index DB** (`~/.yaga/projects/<project-id>/index.db`):
- files with hashes / mtimes / parser versions
- chunks and chunk embeddings
- chunk FTS indexes
- symbols, repo map summaries
- dirty queues, index runs / repairs

Per-project DBs are preferred over a single shared index:
- easier rebuilds and isolation
- better corruption boundaries
- better export and debug story

### Codebase Vectorization

For every project managed in Yaga, the goal is semantic + exact + structural code understanding
without a cloud-heavy indexing backend.

**Index inputs** per managed project:
- source code and tests
- markdown and architecture docs
- config files
- optionally issue/spec snapshots imported into project context

**Chunking strategy:**

Code must not be chunked like prose. Use Tree-sitter or equivalent parser-aware chunking.
Prefer boundaries at: function, method, class, module, interface / type definition.
Add a small parent/context wrapper when useful.
Store file-level metadata and symbol tables separately.

For prose/docs: use token/window chunking with small explicit overlap, preserving
heading/section metadata.

**Retrieval stack for code:**
- FTS5 for exact lexical matches
- sqlite-vec for semantic similarity
- symbol index for names, definitions, references
- repo map for structural hints
- ripgrep fallback for exact diagnostics

Code queries come in different forms: semantic ("where is retry logic?"), lexical
("find `X-Request-ID`"), structural ("who calls this adapter?"). Vectors alone are not enough.

**Repo map / symbol graph:**

Yaga should maintain a lightweight repo map per project:
- key directories, entrypoints, major modules, important files
- symbol summaries
- optionally import/call relations where cheap to compute

The repo map is often cheaper and more useful than full semantic search for orientation and planning.

### Typed Memory Records

Long-term memory should consist primarily of typed memory records, not raw transcript chunks.

Each memory record should carry:
- `agent_id`
- `subject` / `scope`
- `type` (fact, preference, decision, lesson, todo/reminder, open_question, relationship/context, project_note)
- `text` / normalized content
- confidence or validation source
- `created_at`, `updated_at`
- superseded / retracted markers where relevant

Raw transcripts remain searchable as a separate retrieval plane for audit, replay,
debugging, and fallback recall. They must not be conflated with curated memory.

### Hybrid Search Strategy

Hybrid retrieval is mandatory. Default v1 retrieval combines:
- dense embeddings
- lexical search (FTS5/BM25)
- metadata filters
- optional recency weighting

Recommended merge approach: weighted score merge or **RRF** (Reciprocal Rank Fusion).

Recommended retrieval flow for memory:
1. direct/typed filters first when possible
2. lexical/FTS match
3. semantic match
4. merge/rerank
5. optionally apply recency/importance weighting

For non-memory retrieval planes (project index / transcript search), the runtime should also
surface retrieval truncation or stale-index conditions through structured diagnostics rather
than failing silently.

### Index Freshness & Staleness Control

A vector system that quietly goes stale is worse than no vector system.

Each indexed file/chunk must track at least:
- path
- content hash
- file size / mtime
- parser version
- chunker version
- embedding model/version
- last indexed commit/HEAD if useful
- last indexed timestamp

**Required refresh behaviors:**
- dirty-file queue
- resumable indexing
- delete/tombstone handling
- periodic repair scan
- broken-file error tracking
- operator-visible stale-index diagnostics

The operator must be able to answer at any time:
- Is this index fresh?
- What is stale?
- What failed?
- What is waiting to be reindexed?

If not, the indexing system is not operationally complete.

### Failure & Recovery Model

The vectorization and memory system must survive:
- interrupted indexing
- model/provider failure
- file parsing failure
- embedding timeouts
- DB lock/restart issues
- stale chunks after repo changes
- partial upgrades of chunking/index schema

**Recovery pattern:**
- log index jobs as first-class runtime jobs/events
- mark jobs as: queued → running → partial → failed → repaired → completed
- keep failed chunks/files visible
- allow explicit repair/reindex commands
- prefer idempotent rebuild behavior

### Mission Control Integration

**Operator / UI level:**
Mission Control UI should surface:
- project indexing status
- stale/failing indexes
- memory health
- retrieval diagnostics
- project-level search/admin operations

**Agent execution level:**
Agents interact with Mission Control and project context through CLI and API.
Agents will often prefer CLI for structured operational work, but API remains important
for UI and integrations. The architecture must support both cleanly.

### v1 Scope vs Later

**Ship in v1:**
- SQLite + WAL, FTS5, sqlite-vec
- per-project index DBs
- project code/doc indexing
- typed memory records
- transcript search as separate plane
- repo map + symbol metadata
- dirty queue and repair scan
- CLI/API access to index state
- UI visibility into index health

**Consider later:**
- richer graph memory relations
- advanced rerankers
- local sidecar search engine mode
- optional Qdrant / external vector backend for larger server installs
- cross-project semantic federation
- multimodal indexing
- background summarization/distillation loops

### Decision Summary

For Yaga, the memory and vectorization pattern is:

- **local-first**
- **SQLite-backed**
- **hybrid retrieval**
- **repo-aware for code**
- **typed/distilled for memory**
- **operator-visible and repairable**

> **Vectors are an index, not the truth.**
> **Code retrieval needs structure, not just embeddings.**
> **Memory should be curated, typed, and inspectable.**
> **The default product shape must stay light enough for a real `curl | bash` install.**
