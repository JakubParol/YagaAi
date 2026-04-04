# 15 — Technology Stack

## Purpose

This document records the concrete technology choices for Yaga v1 and the rationale
behind each decision. Architecture docs (00–14) are intentionally technology-agnostic.
This document breaks that abstraction and commits to specific tools.

Every choice here must be consistent with the non-negotiable product constraint:

> `curl -fsSL https://yagaai.com/install.sh | bash`

If a technology requires Docker, Redis, a running server, or manual provisioning before
the first useful run, it does not belong in the default stack.

---

## Language Split

| Layer | Language |
|-------|----------|
| Runtime daemon, backend API, CLI, agents | **Python 3.12+** |
| Web UI | **TypeScript** |

**Why Python for backend:**
- Dominant ecosystem for LLM tooling, embeddings, and agent frameworks
- LlamaIndex, SQLAlchemy, FastAPI, Pydantic — all first-class Python
- Avoids maintaining a polyglot backend

**Why TypeScript for UI:**
- Next.js + shadcn/ui is the current high-quality standard for this type of operator UI
- Clean separation: UI is a consumer of the stable local API, not part of the runtime

---

## Backend Framework

**Chosen: FastAPI**

- Async-first, ASGI-native — matches the asyncio runtime model
- Pydantic v2 integration is native — same validation layer as the event/command schemas
- OpenAPI docs generated automatically — useful for CLI tooling and debugging
- Dependency injection model maps cleanly to service layer (event bus, session factories)

**Rejected:**
- Django REST Framework — sync-first, heavyweight for a local daemon
- Flask — no native async, no DI, more glue code
- Litestar — technically excellent but smaller ecosystem

---

## Data Layer

### ORM: SQLAlchemy 2.0 async + Alembic

**Chosen: SQLAlchemy 2.0 (async) + Alembic**

SQLAlchemy 2.0 introduced a clean async API (`AsyncSession`, `async_sessionmaker`) backed
by `aiosqlite`. This is the production-grade path for async SQLite in Python.

Alembic is mandatory. The schema will evolve continuously — new event types, new fields,
new MC concepts. `autogenerate` + revision history makes migrations safe and auditable.
This is not optional infrastructure.

Separate SQLAlchemy models and Pydantic schemas. The DB layer must not leak into the API
layer. This adds boilerplate but prevents a class of bugs where DB internals become API
contracts.

**Rejected: SQLModel**
- Async support has historically lagged behind SQLAlchemy 2.0
- Tiangolo (author) is known for slow maintenance cycles
- Dual-purpose model (Pydantic + SQLAlchemy in one class) is convenient at first and
  painful at scale — schema evolution becomes harder when the API contract and DB model
  are the same object
- Alembic configuration is still required separately anyway

### Storage: SQLite + WAL

**Chosen: SQLite with WAL journal mode**

- Zero external dependency
- Single file: `~/.yaga/state.db`
- WAL mode enables concurrent reads and non-blocking writes
- `aiosqlite` provides async access
- FTS5 for lexical search — built into SQLite
- sqlite-vec for vector search — single compiled extension, no server
- Easy backup: copy one file
- Easy diagnostics: standard SQL tooling works

**Default paths (aligned with `14-hld-runtime-shape-and-installation.md`):**
- Global runtime DB: `~/.local/share/yaga/state.db` (Linux) / `~/Library/Application Support/Yaga/state.db` (macOS)
- Per-project index: `~/.local/share/yaga/projects/<project-id>/index.db`

**Upgrade path:**
PostgreSQL is a supported future deployment mode (Mode B/C from `14`). SQLAlchemy's
dialect abstraction makes this a configuration change, not a rewrite. Do not design
for PostgreSQL first — it violates the install constraint.

**Rejected: PostgreSQL as default**
- Requires running server
- Requires provisioning before first run
- Kills the `curl | bash` promise
- SQLite is genuinely sufficient for a single-machine local runtime

---

## Event Bus

**Chosen: Custom asyncio event bus + SQLite outbox pattern**

The event system is the backbone of Yaga (see `00-input-one-pager.md`, `03-runtime-and-a2a.md`).
It must be durable, replayable, deduplication-safe, and inspectable. It must not require
an external broker.

### Design

```
Command arrives
  → written to commands table (SQLite)
  → CommandHandler processes
  → Domain Event(s) emitted
  → written to events table (append-only, SQLite outbox)
  → in-process asyncio dispatch to Policy handlers
  → Read Models updated
```

**Outbox pattern ensures durability:** events are committed to SQLite before in-process
dispatch. If the process crashes between write and dispatch, events are recovered on
restart via table scan. No event is silently lost.

**In-process asyncio dispatch gives low latency** for the common case — no IPC, no
serialization round-trip for local event routing.

**Events table is append-only.** Rows are never updated or deleted (within retention
policy). This is the audit trail and the replay source.

### Key schema concepts

| Table | Purpose |
|-------|---------|
| `commands` | Incoming intent; may be rejected |
| `events` | Immutable facts; append-only |
| `outbox` | Events pending in-process dispatch; cleared after delivery |
| `jobs` | Retry, watchdog, timeout scheduling |

Every event row carries: `id`, `type`, `aggregate_id`, `aggregate_type`, `correlation_id`,
`causation_id`, `dedup_key`, `payload` (JSON), `created_at`, `schema_version`.

**Rejected: Dapr + Redis**
- Requires Docker or external process
- Violates local-first install constraint
- Operationally heavy for a single-machine developer runtime
- Significant infrastructure surface for minimal gain at v1 scale

**Rejected: python-eventsourcing library**
- Designed for pure Event Sourcing (state reconstructed solely from events)
- Yaga uses a hybrid model: durable mutable records (request store, task store, MC)
  alongside an event log
- The library's `Aggregate` / `Application` abstraction would fight the architecture
- Abstraction mismatch is worse than writing 400 lines of focused infrastructure

**Rejected: Celery / Dramatiq / RQ**
- All require an external broker (Redis, RabbitMQ)
- Overkill for a single-daemon local runtime

**Rejected: Temporal**
- Excellent workflow engine but requires a running Temporal server
- Not compatible with `curl | bash`

---

## Validation and Serialization

**Chosen: Pydantic v2**

Pydantic v2 is the validation layer for:
- Command and Domain Event schemas
- API request/response models
- Agent configuration models
- Handoff contract validation

Pydantic v2 is used throughout FastAPI natively. Keeping one validation library
across the stack reduces the cognitive surface.

---

## Retrieval and Vectorization

**Chosen: LlamaIndex**

LlamaIndex is the retrieval and indexing layer. It covers:
- Document loaders (code files, markdown, config)
- Code-aware chunking via `CodeSplitter` (Tree-sitter under the hood — no direct
  Tree-sitter dependency required)
- Prose chunking with section/heading preservation
- Embedding pipeline integration
- Vector store adapters

LlamaIndex integrates with sqlite-vec as a vector backend, which keeps the zero-external-
dependency constraint intact.

**Why LlamaIndex over LangChain for this layer:**
- LlamaIndex is retrieval-focused by design; LangChain is more general-purpose
- Retrieval pipeline primitives (nodes, chunkers, indices, retrievers) map cleanly to
  Yaga's four retrieval planes (agent memory, code index, project docs, transcript search)
- Less surface area for a retrieval-specific use case

**Why LlamaIndex over DIY Tree-sitter chunking:**
- Tree-sitter bindings, grammar management, and chunk boundary logic are non-trivial
- LlamaIndex's `CodeSplitter` solves this problem and is maintained by a large team
- Implementation effort is better spent on the event bus, ownership model, and MC module

**Vector storage:** sqlite-vec extension (embedded SQLite vector search).
No Qdrant, no Weaviate, no Pinecone in the default install.
See `07-memory-model-and-vectorization.md` for retrieval plane design.

---

## Web UI

**Chosen: Next.js (App Router) + shadcn/ui + TypeScript**

The Web UI is a mandatory built-in runtime surface (see `14-hld-runtime-shape-and-installation.md`,
Decision 15 in `13-implementation-decisions.md`).

- **Next.js** (App Router): file-based routing, React Server Components for operator views,
  streaming for real-time run/event feeds
- **shadcn/ui**: accessible component primitives, no component library lock-in — components
  are owned in the codebase, not a black-box dependency
- **TypeScript**: type safety across the UI layer; API contract types can be generated from
  FastAPI's OpenAPI schema

The UI is a consumer of the stable local API. It has no direct DB access. It does not
contain business logic. It is thin by design.

**Build integration:** Next.js static export or standalone build, served by the runtime
daemon's built-in HTTP server. No separate web server process.

---

## CLI

**Chosen: Typer**

- Typer is built on Click, adds type annotation-driven CLI generation
- Pydantic v2 compatible
- FastAPI-adjacent (same ecosystem, similar DX)
- One entrypoint: `yaga`

CLI command structure (from `14`):
```
yaga up / down / status / logs / doctor
yaga agent list / status / restart
yaga mc (Mission Control subcommands)
yaga request list / inspect / retry
yaga index status / rebuild
```

---

## Structured Logging

**Chosen: structlog**

structlog produces structured (JSON) log output that is queryable and consistent with
the event model. Every log entry should carry `correlation_id`, `request_id` where
relevant, and `agent_id`. This is the operational companion to the event log.

Plain `logging` module is not sufficient for a system where log lines must be
machine-parseable for diagnostics and replay.

---

## Development Tooling

| Tool | Purpose |
|------|---------|
| **uv** | Python package and venv management (fast, modern replacement for pip/poetry) |
| **ruff** | Linting and formatting (replaces flake8 + black + isort) |
| **mypy** | Static type checking — mandatory for agent/event schemas and service interfaces |
| **pytest + pytest-asyncio** | Test runner with async support |
| **httpx** | Async HTTP client for FastAPI test client and integration tests |

---

## Service Management

| Platform | Service manager |
|----------|----------------|
| Linux | `systemd --user` unit |
| macOS | `launchd` plist |

The runtime daemon starts on login, runs in user space, requires no root.
See `14-hld-runtime-shape-and-installation.md` for installer flow.

---

## What This Stack Deliberately Does Not Include (v1)

| Technology | Why excluded |
|------------|-------------|
| Docker | Violates local-first install constraint |
| Redis | External process; SQLite + job table is sufficient |
| Dapr | Sidecar architecture is operationally heavy for single-machine use |
| Celery / Dramatiq | Require external broker |
| Temporal | Requires running server |
| PostgreSQL | Not default; available as upgrade path in Mode B/C deployment |
| python-eventsourcing | Pure ES mismatch with Yaga's hybrid state model |
| SQLModel | Async immaturity, slow maintenance, abstraction leaks at scale |
| External vector DB (Qdrant, Weaviate) | Violates local-first; sqlite-vec is sufficient for v1 |
| LangChain (for retrieval) | Too general-purpose; LlamaIndex is retrieval-focused |
| Kafka / NATS / RabbitMQ | Distributed message bus; incompatible with single-daemon local model |

---

## Stack at a Glance

```
┌─────────────────────────────────────────────────┐
│                   Web UI                         │
│         Next.js + shadcn/ui (TypeScript)         │
├─────────────────────────────────────────────────┤
│              CLI  ─  yaga (Typer)                │
├─────────────────────────────────────────────────┤
│              Local API (FastAPI)                 │
│              Pydantic v2 schemas                 │
├─────────────────────────────────────────────────┤
│    Event Bus (asyncio + SQLite outbox)           │
│    Commands → Domain Events → Policies           │
├──────────────────┬──────────────────────────────┤
│  SQLAlchemy 2.0  │   LlamaIndex                 │
│  async + Alembic │   CodeSplitter + retrievers  │
├──────────────────┴──────────────────────────────┤
│         SQLite + WAL + FTS5 + sqlite-vec         │
│    state.db  /  projects/<id>/index.db           │
└─────────────────────────────────────────────────┘
```

---

## Upgrade Invariant

Any future migration away from SQLite (to PostgreSQL for Mode B/C) or from sqlite-vec
(to an external vector backend) must be achievable via:
- SQLAlchemy dialect swap
- LlamaIndex vector store swap
- Alembic migration

It must not require rewriting business logic, event bus, or agent code.
The stack is designed so that storage is a replaceable dependency, not a foundation assumption.
