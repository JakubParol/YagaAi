# 14 — Memory and Vectorization

## Status
Draft HLD for memory, retrieval, and codebase vectorization in Yaga Runtime.

## Purpose
Define how Yaga should handle:
- vectorization of managed project codebases,
- agent memory retrieval,
- long-term and episodic memory,
- hybrid search,
- indexing/update strategies,
- and lightweight local deployment constraints.

This document takes into account:
- the current Agent Runtime architecture direction,
- Alex research on OpenClaw and Hermes,
- and the product constraint that Yaga must stay simple, lightweight, and practical on Linux/macOS.

---

## 1. Core Principle

Yaga should not treat “memory” as one giant blob.

We need at least four distinct retrieval planes:

1. **Project code index**
   - source files
   - symbols
   - AST-aware chunks
   - repo map / structure metadata

2. **Project knowledge/docs index**
   - READMEs
   - ADRs
   - design docs
   - architecture notes
   - tickets/specs imported into project context

3. **Agent memory**
   - durable facts
   - preferences
   - decisions
   - recurring lessons
   - unresolved questions
   - important episodic outcomes

4. **Session/transcript search**
   - raw interaction history
   - debugging trace
   - replay support
   - secondary recall source, not primary long-term memory

These can share infrastructure, but they must not be conflated conceptually.

---

## 2. Product-Level Requirements

The design must support:

- local-first operation,
- Linux and macOS installs,
- one-command setup,
- low operational overhead,
- strong operator inspectability,
- hybrid retrieval quality,
- fast incremental refresh,
- durability across restarts,
- and recovery from stale or broken indexes.

This pushes us toward embedded/local storage first, not a server-heavy vector stack by default.

---

## 3. What We Borrow from OpenClaw and Hermes

## 3.1 OpenClaw: what is worth copying

OpenClaw’s strongest ideas here are:

- **memory source of truth stays human-readable** (`MEMORY.md`, daily notes),
- vectors are an **index**, not the canonical truth,
- built-in memory uses a **local SQLite-based hybrid engine**,
- retrieval combines:
  - semantic search,
  - keyword search,
  - weighted merge,
  - optional temporal logic,
- advanced local search is possible through **QMD**, but that is a sidecar/advanced path, not the only model.

Important clarification from research:
- the thing that looked like “QME / QWE / Qdrant-something” is most likely **QMD**,
- QMD is a local-first search engine / sidecar,
- OpenClaw’s default memory path is still fundamentally **SQLite + FTS5 + embeddings**, not “OpenClaw on Qdrant”.

## 3.2 Hermes: what is worth copying

Hermes appears to be stronger on:
- clean local SQLite state,
- WAL mode,
- FTS-backed local search,
- explicit persistent session storage,
- and a direction toward richer memory structures.

What seems less mature there, compared to OpenClaw, is a clearly shipped full semantic/vector memory layer and codebase indexing stack.

### Synthesis

The best synthesis for Yaga is:

- copy the **lightweight local SQLite discipline**,
- copy the **hybrid retrieval model**,
- keep memory **typed and distilled**,
- and avoid starting with an external vector DB unless the local-first shape proves insufficient.

---

## 4. Strong Recommendation for Yaga v1

## Default choice

For Yaga v1, use:

- **SQLite + WAL**
- **FTS5** for lexical retrieval
- **sqlite-vec** for semantic retrieval
- metadata/path filters
- optional rank fusion / weighted merge
- repo map + symbol graph + grep fallback for code navigation

This should be the default architecture for both:
- project vectorization,
- and agent memory retrieval.

### Why this is the best fit

Because it gives us:
- zero external DB requirement,
- simple install,
- easy debugging,
- good local performance,
- one product / one state directory mental model,
- and a path to later upgrades without overcommitting too early.

---

## 5. Storage Model

## 5.1 Global runtime DB

Recommended path:
- `~/.yaga/state.db`

This DB should contain runtime-global data such as:
- agents
- sessions
- requests
- tasks / flows / runs
- memory records
- memory embeddings
- memory FTS indexes
- retrieval diagnostics
- indexing jobs
- failures / repair markers

## 5.2 Per-project index DB

Recommended path:
- `~/.yaga/projects/<project-id>/index.db`

This DB should contain project-specific retrieval/index data such as:
- files
- file hashes / mtimes / parser versions
- chunks
- chunk embeddings
- chunk FTS indexes
- symbols
- repo map summaries
- dirty queues
- index runs / repairs

### Why per-project DBs are preferable

- easier rebuilds,
- easier isolation,
- better corruption boundaries,
- better export/debug story,
- and avoids a single giant shared index file.

---

## 6. Codebase Vectorization

## 6.1 Goal

For every project managed in Yaga, we want Cursor/Antigravity-style code understanding without requiring a cloud-heavy indexing backend.

That means:
- semantic search,
- exact search,
- structural search,
- and refresh behavior that can keep up with a changing repo.

## 6.2 Index inputs

Per managed project, Yaga should be able to index:
- source code
- tests
- markdown docs
- architecture docs
- config files
- optionally issue/spec snapshots imported into the project context

## 6.3 Chunking strategy

Code should **not** be chunked like prose.

Recommended strategy:
- use **Tree-sitter** or equivalent parser-aware chunking,
- prefer boundaries such as:
  - function
  - method
  - class
  - module
  - interface / type definition
- add a small parent/context wrapper when useful,
- separately store file-level metadata and symbol tables.

For prose/docs:
- use token/window chunking,
- keep overlap small and explicit,
- preserve heading/section metadata.

## 6.4 Retrieval stack for code

Best practical retrieval stack:
- **FTS5** for exact lexical matches
- **sqlite-vec** for semantic similarity
- symbol index for names/definitions/references
- repo map for structural hints
- ripgrep fallback for exact diagnostics

This matters because code queries come in different forms:
- semantic: “where is retry logic implemented?”
- lexical: “find `X-Request-ID`”
- structural: “who calls this adapter?”

Vectors alone are not enough.

## 6.5 Repo map / symbol graph

Yaga should maintain a lightweight **repo map** per project.

It should include:
- key directories
- entrypoints
- major modules
- important files
- symbol summaries
- optionally import/call relations where cheap to compute

This repo map is often cheaper and more useful than full semantic search for orientation and planning.

---

## 7. Memory Model

## 7.1 Memory should be distilled, not transcript-first

Long-term memory should consist primarily of **typed memory records**, not raw transcript chunks.

Recommended categories:
- **fact**
- **preference**
- **decision**
- **lesson**
- **todo/reminder**
- **open_question**
- **relationship/context**
- **project note**

Each memory record should carry:
- agent_id
- subject / scope
- type
- text / normalized content
- confidence or validation source
- created_at
- updated_at
- superseded / retracted markers where relevant

## 7.2 Raw transcripts remain searchable, but separate

We still want transcript search for:
- audit,
- replay,
- debugging,
- and fallback recall.

But transcript search should remain a separate retrieval plane.
It should not be confused with curated memory.

## 7.3 Memory retrieval pattern

Recommended retrieval flow:
1. direct/typed filters first when possible
2. lexical/FTS match
3. semantic match
4. merge/rerank
5. optionally apply recency/importance weighting

This is close to the better parts of OpenClaw’s memory model, but with clearer separation of planes.

---

## 8. Hybrid Search Strategy

Hybrid retrieval is mandatory.

Default v1 retrieval should combine:
- dense embeddings
- lexical search
- metadata filters
- optional recency weighting

Recommended merge approaches:
- weighted score merge
- or **RRF** (Reciprocal Rank Fusion)

The goal is not mathematical elegance.
The goal is stable practical recall.

---

## 9. Index Refresh and Staleness Control

This is one of the most important non-obvious parts.

A vector system that quietly goes stale is worse than no vector system.

## Required controls

Each indexed file/chunk should track at least:
- path
- content hash
- file size / mtime
- parser version
- chunker version
- embedding model/version
- last indexed commit/HEAD if useful
- last indexed timestamp

## Required refresh behaviors

We need:
- dirty-file queue,
- resumable indexing,
- delete/tombstone handling,
- periodic repair scan,
- broken-file error tracking,
- and operator-visible stale-index diagnostics.

### Important rule

The operator should be able to answer:
- is this index fresh?
- what is stale?
- what failed?
- what is waiting to be reindexed?

If not, the indexing system is not operationally complete.

---

## 10. Failure and Recovery Model

The vectorization and memory system must survive:
- interrupted indexing,
- model/provider failure,
- file parsing failure,
- embedding timeouts,
- DB lock/restart issues,
- stale chunks after repo changes,
- and partial upgrades of chunking/index schema.

## Recommended recovery pattern

- log index jobs as first-class runtime jobs/events,
- mark jobs as:
  - queued
  - running
  - partial
  - failed
  - repaired
  - completed
- keep failed chunks/files visible,
- allow explicit repair/reindex commands,
- prefer idempotent rebuild behavior.

---

## 11. Mission Control Integration

Mission Control needs this at two levels.

## 11.1 Operator / UI level

Mission Control UI should surface:
- project indexing status,
- stale/failing indexes,
- memory health,
- retrieval diagnostics,
- and project-level search/admin operations.

## 11.2 Agent execution level

Agents should be able to interact with Mission Control and project context through:
- **CLI**
- **API**

Important practical stance:
- **agents will often prefer CLI** for structured operational work,
- but API remains important for UI and integrations.

So the architecture should support both cleanly.

---

## 12. v1 vs Later

## v1

Ship in v1:
- SQLite + WAL
- FTS5
- sqlite-vec
- per-project index DBs
- project code/doc indexing
- typed memory records
- transcript search as separate plane
- repo map + symbol metadata
- dirty queue and repair scan
- CLI/API access to index state
- UI visibility into index health

## Later

Consider later:
- richer graph memory relations
- advanced rerankers
- local sidecar search engine mode like QMD
- optional Qdrant / external vector backend for larger server installs
- cross-project semantic federation
- multimodal indexing
- background summarization/distillation loops

---

## 13. Decision Summary

For Yaga, the best memory/vectorization pattern is:

- **local-first**,
- **SQLite-backed**,
- **hybrid retrieval**,
- **repo-aware for code**,
- **typed/distilled for memory**,
- **operator-visible and repairable**.

In short:

> **Vectors are an index, not the truth.**
> **Code retrieval needs structure, not just embeddings.**
> **Memory should be curated, typed, and inspectable.**
> **The default product shape should stay light enough for a real `curl | bash` install.**
