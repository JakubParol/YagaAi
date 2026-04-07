# 14 — HLD: Runtime Shape, Deployment Pattern, and Mission Control Integration

## Purpose
Define the preferred high-level deployment and runtime architecture for Yaga as a lightweight, local-first developer-agent system that is easy to install on Linux and macOS.

This document focuses on:
- whether we want a Gateway-centric pattern,
- what the always-on runtime should look like,
- how Mission Control should fit into the system,
- how agents and operators should interact with Mission Control via both CLI and API,
- why the Web UI host is a mandatory built-in surface,
- how vectorization and memory fit into the runtime shape,
- how to keep the system simple enough for `curl -fsSL https://yagaai.com/install.sh | bash`,
- and what must be true if we want something that is genuinely lightweight and operationally reliable.

---

## 1. Design Constraints

The target system must be:

- **easy to install**,
- **easy to run**,
- **easy to debug**,
- **lightweight on a single laptop or workstation**,
- **portable across Linux and macOS**,
- **capable of long-running agent work**,
- **able to survive LLM/runtime failures without falling apart**.

This immediately rules out some architectural habits that are common in heavier systems.

### Anti-goals for the runtime shape

We do **not** want the default installation to require:

- Docker,
- Kubernetes,
- Redis,
- Dapr,
- multiple always-on services just to answer a message,
- multi-step manual provisioning before the first useful run,
- Ubuntu-only installation assumptions,
- or a server-style control-plane architecture for a single-user local install.

If the product promise is “simple, light, working”, the deployment shape must match it.

---

## 2. Key Design Lessons

### 2.1 A long-lived process is necessary

Some things genuinely require a single long-lived process:
- channel connections and WebSocket control plane,
- long-lived auth state,
- background jobs and watchdogs,
- supervision of running agent work.

That is legitimate. The runtime must own it.

### 2.2 The failure mode is when that process becomes a god-process

The bad outcome is not “a long-running process exists.”
The bad outcome is when that process becomes:
- networking layer,
- orchestration brain,
- transport adapter owner,
- session router,
- persistence coordinator,
- and product architecture center,

all at once. That leads to protocol coupling and operational fragility.

### 2.3 A heavy multi-service control plane is not the target product shape

A Mission Control architecture with separate API service, worker, Redis, Postgres, Dapr sidecars,
and container-first deployment is acceptable for staging infrastructure.
It is **not** the right default product shape for:

> `curl -fsSL https://yagaai.com/install.sh | bash`

The conclusion is not “throw away Mission Control thinking.”
The conclusion is:

> **Keep the domain model, simplify the runtime shape.**

---

## 3. Recommended Pattern

## Short version

**Do not make Gateway the product center.**

**Do use one local always-on runtime daemon as the host control plane.**

**Treat “gateway/adapters” as one subsystem of that daemon, not the whole architecture.**

Recommended name for the always-on process:

- **Yaga Runtime**
- internal shape: **local runtime daemon** / **host runtime**

This is a better fit than calling the whole thing “Gateway”.

### Why this is the right naming split

- **Gateway** sounds like transport/network ingress.
- **Runtime** correctly covers:
  - agents,
  - sessions,
  - event processing,
  - retries,
  - watchdogs,
  - memory,
  - task execution,
  - adapter ownership,
  - local APIs,
  - Mission Control integration.

In this model:
- **gateway/adapters** are edge modules,
- **runtime** is the real product core.

---

## 4. Target v1 Runtime Shape

The recommended v1 shape is:

```text
+-----------------------------------------------------------+
|                       Yaga Runtime                        |
|-----------------------------------------------------------|
|  Local API + CLI surface + built-in Web UI host          |
|  Agent supervisor                                         |
|  Session/run manager                                      |
|  Event log + job/retry engine                             |
|  Watchdogs / recovery loops                               |
|  Memory and vectorization services                        |
|  Adapter manager (chat/channel/provider integrations)     |
|  Optional planning/control-plane integrations / read models |
|  Local persistence                                        |
+-----------------------------------------------------------+
```

### Key idea

For v1, the default install should feel like **one product, one runtime, one state directory**.

Not:
- many services,
- many ports,
- many containers,
- many persistence layers,
- or many moving parts that fail independently.

---

## 5. Recommended Component Breakdown

## 5.1 Yaga Runtime daemon (mandatory)

One always-on local process per machine.

**Formal default:** single process is the normative v1 install shape.
Any API/worker split is an optional scaling profile and must not be required by default.

Responsibilities:
- manage agent identities and agent configs,
- own long-running sessions and execution supervision,
- own channel/provider adapters,
- accept local CLI/API/UI requests,
- persist request/task/run state and request records,
- run retries and watchdog logic,
- emit and consume internal events,
- manage callbacks and publication status,
- host or expose optional planning/control-plane integration read models,
- own the prompt assembly path for all agent sessions.

**Session model:** Each named agent has exactly one `main` coordination session — the durable owner
endpoint — regardless of how many channel adapters (WhatsApp, Discord, web, etc.) are active.
Channel adapters are ingress/egress surfaces; they do not create additional agent sessions. The
runtime also manages bounded worker sessions spawned by agents for specific tasks; these are not
durable owners and always return results to the spawning agent's `main`.

**Agent supervision model:**
Each named agent (James, Naomi, Amos, Alex) has a stable durable identity registered in the runtime.
The daemon supervises agent processes/workers and is responsible for:
- detecting crashes or unresponsive agents,
- restarting agents within policy,
- draining in-flight work safely before restart where possible,
- resuming durable state from the request record and event log after restart,
- never reconstructing routing or publication state from transcript.

This is the operational heart of the system.

Implementation clarification:
- agent workers may be implemented in-process or as runtime-supervised subprocesses,
- but the default product shape remains one runtime deployment unit, not a fleet of separately deployed agent services.

## 5.2 Local API and CLI surfaces (mandatory)

The runtime should expose a **local API**.
This can be Unix domain socket, loopback HTTP, or both.

Use it for:
- CLI,
- built-in web UI,
- automation hooks,
- diagnostics,
- external integrations where appropriate.

Important product stance:
- **Mission Control must be reachable through both API and CLI**,
- because UI/admin/integration flows naturally prefer API,
- while agents will often prefer the CLI for structured operational work.

Important rule:
- this API is a product boundary,
- not an internal transport leak of implementation details.

Mission Control should talk to this stable local API/event contract, not to low-level protocol trivia.

## 5.3 Adapter subsystem (optional per integration, but inside runtime)

Adapters for:
- WhatsApp,
- Discord,
- Slack,
- Web chat,
- email/calendar later,
- or other user-facing surfaces.

Important architectural stance:

> Adapters are runtime plugins/subsystems, not separate orchestration services.

They should report events into the same runtime state model.

**Mandatory routing topology:**
Adapters are ingress/egress surfaces only — they must never become durable owners of agent logic.
Every durable, delegated, or non-trivial user-originated request must normalize through the owning
agent's `main` session. Specialist delegation is main-to-main. Final reply routes back through
stored reply-target metadata.

Adding a new adapter must not create a new ownership model — only a new ingress/egress adapter.
See [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md)
for the full topology specification and invariants.

## 5.4 Agent execution subsystem (mandatory)

Responsibilities:
- start agent runs,
- resume/route to durable owner sessions,
- spawn bounded workers,
- track accepted/running/completed/failed state,
- capture artifacts and summaries,
- feed the event model,
- supervise retries where policy allows.

This subsystem should treat runtimes like Claude Code, Codex, ACP, etc. as execution backends.

## 5.5 Event engine (mandatory)

The runtime must have a real internal event engine.
Not Kafka-scale. Not overengineered. Just real.

Needs to support:
- append-only event logging,
- correlation IDs,
- causation IDs,
- dedup keys,
- job scheduling,
- retry scheduling,
- timeout scheduling,
- watchdog wakeups,
- replay for diagnostics.

This is where a lot of “A2A must be serious” becomes real.

## 5.6 Prompt assembly subsystem (runtime-owned)

The runtime owns the prompt assembly path for all agent sessions.
This is not a job for the agent process alone or for an external service.

The runtime is responsible for:
- assembling the correct prompt mode (full / minimal / execution) per session type,
- injecting cached stable layers (identity, workspace, skill index),
- computing and injecting ephemeral turn layers (current task, retrieval results, memory recall),
- enforcing that child/subagent sessions receive minimal prompts, not full parent context,
- triggering memory flush before compaction,
- exposing which prompt layers were active for a given run (prompt introspection).

See [06-internal-prompt-architecture.md](06-internal-prompt-architecture.md) for the full
prompt layering specification.

## 5.7 Mission Control as first-party optional integration

Mission Control should be treated as a **first-party optional integration** in the Yaga product architecture, not an externally mandatory multi-service platform for local installs.

Mission Control remains the home for:
- planning concepts,
- stories/tasks/bugs,
- queue/read-model/operator views,
- assignment state,
- review/verify workflow,
- dashboards and orchestration visibility,
- admin/configuration/management UI flows,
- and CLI/API contracts for operational work.

But for the target product shape, it should integrate through:
- local UI pages/read models when present,
- stable runtime-owned API/event contracts,
- shared local deployment ergonomics by default.

That is much healthier than shipping:
- separate API service,
- separate worker,
- Redis,
- Dapr sidecars,
- container-only orchestration.

## 5.8 Local state layout

Recommended default paths:
- global runtime DB: `~/.local/share/yaga/state.db` on Linux, `~/Library/Application Support/Yaga/state.db` on macOS
- per-project indexes: `~/.local/share/yaga/projects/<project-id>/index.db` on Linux, `~/Library/Application Support/Yaga/projects/<project-id>/index.db` on macOS

The global runtime DB is expected to hold:
- requests, tasks, handoffs, and publication state
- command log, event log, event outbox, and jobs
- memory state and runtime diagnostics

---

## 6. Strong Recommendation: Make Mission Control an Optional Integration, Not a Stack

This is the biggest HLD recommendation.

### Today
Mission Control behaves like a separate platform:
- web,
- API,
- worker,
- Redis,
- Postgres,
- Dapr,
- Docker-based runtime assumptions.

### Target
Mission Control should become:
- a **first-party planning/control-plane integration**,
- a **UI/read-model layer**,
- an **operator workflow surface**,
- and a consumer of the runtime's stable local contracts.

### What to preserve from Mission Control
Preserve:
- entity model,
- planning model,
- story/task semantics,
- runtime read-model ideas,
- queueing and operator views,
- review/verify workflow,
- assignment-driven orchestration.

### What to kill or demote
Kill or demote in the default product install:
- mandatory Redis,
- mandatory Dapr,
- mandatory split API/worker topology,
- Docker-first local runtime,
- deployment assumptions that require system-level ops from day one.

That is how we keep the product light without throwing away the good domain work.

---

## 7. Storage Pattern

## Default v1 recommendation

Use **one local durable store** by default.

Preferred default:
- **SQLite with WAL mode** for local installs

Why:
- zero external dependency,
- good enough for one-machine local runtime,
- excellent fit for `curl | bash`,
- strong operational simplicity,
- easy backup/export,
- easy diagnostics.

**Global runtime DB** (`~/.local/share/yaga/state.db` on Linux, `~/Library/Application Support/Yaga/state.db` on macOS) — use SQLite for:
- request records (source of truth for routing and `reply_publish_status`),
- task/run state,
- event log (append-only, dedup by `dedup_key`, replayable),
- retry queue and watchdog schedule,
- Mission Control planning/read-model state,
- agent memory records, memory embeddings (via sqlite-vec), memory FTS indexes (via FTS5).

**Per-project index DBs** (`~/.local/share/yaga/projects/<project-id>/index.db` on Linux, `~/Library/Application Support/Yaga/projects/<project-id>/index.db` on macOS) — separate SQLite files for:
- codebase chunks and chunk embeddings,
- symbol metadata and repo map,
- dirty queues and index repair state.

Keeping per-project index DBs separate from the global runtime DB improves isolation,
simplifies rebuilds, and limits corruption blast radius.

See [07-memory-model-and-vectorization.md](07-memory-model-and-vectorization.md) for the full
memory and vectorization storage model.

### Optional later upgrade path
For heavier team/server deployment:
- support **PostgreSQL** as an advanced deployment mode,
- but do not force it for the default user install.

### Important HLD principle

> If PostgreSQL is mandatory on day one, the product is already heavier than the promise.

---

## 8. Queue / Retry / Watchdog Pattern

Do not introduce Redis just to feel “serious”.

Default v1 recommendation:
- use a **database-backed job table** and scheduler inside the runtime,
- use the same event log/store for retry bookkeeping,
- keep retry and watchdog execution inside the same always-on daemon.

This is enough for:
- ack timeouts,
- stale execution detection,
- publish retry,
- dead-letter / exhausted retries,
- backoff scheduling,
- periodic reconciliation sweeps.

For v1, this is a better pattern than:
- Redis queue,
- separate worker service,
- external event bus,
- Dapr actors/pubsub.

That extra stack buys complexity faster than it buys value.

---

## 9. API, CLI, and UI Pattern

## 9.1 One CLI

The user-facing command should be one thing:

- `yaga`

Examples:
- `yaga up`
- `yaga status`
- `yaga logs`
- `yaga doctor`
- `yaga agent list`
- `yaga mc`

No split-brain between separate products by default.

## 9.2 Built-in Web UI host (mandatory)

The Web UI host is **not optional**.
It should be a built-in part of the runtime.

We need it for:
- management,
- administration,
- configuration,
- runtime health,
- queue and agent visibility,
- Mission Control operator views,
- indexing/memory diagnostics,
- and repair/recovery actions.

Important constraint:
- keep it simple,
- keep it local-first,
- keep it tightly coupled to the runtime’s stable local API,
- do not let it drag the architecture back into a heavy multi-service web platform.

## 9.3 Stable local API

Mission Control UI, CLI, and automation should all talk to a stable local API.

That API should expose:
- planning operations,
- runtime/run state,
- queue state,
- event timelines,
- retry/recovery actions,
- agent/session operations,
- memory and vectorization/index health,
- diagnostics.

### API capability tags (without version bump)

Expose operations with capability tags so one contract can serve staged rollout:

- `core-slice` — minimum ingress/request/publication path needed for initial runtime bring-up.
- `full-v1` — planning, queue/run state, timelines, recovery actions, agent/session ops, memory/index health, diagnostics.

This is one v1 API surface with tagged capability coverage, not a `v1`/`v1.1` split.

At the same time, the runtime should provide a first-class CLI surface for agents and operators.
Agents will often find CLI interactions simpler and more robust than direct API choreography.

---

## 10. Installer and Service Model

## Product promise

The target experience is:

```bash
curl -fsSL https://yagaai.com/install.sh | bash
```

That only works if the install shape is intentionally boring.

## Default install flow should do roughly this

1. detect Linux vs macOS,
2. download one runtime package/binary bundle,
3. create user-local config/state directories,
4. install the CLI entrypoint,
5. install a user service:
   - `launchd` on macOS,
   - `systemd --user` on Linux,
6. start the runtime,
7. run a health check,
8. optionally open onboarding or UI.

## Default paths

Recommended direction:
- config: `~/.config/yaga/`
- state: `~/.local/share/yaga/` on Linux
- state: `~/Library/Application Support/Yaga/` on macOS
- logs: platform-local user directory

## Critical product rule

The default installer should **not** require:
- Docker install,
- root-only host setup for normal local usage,
- manual DB provisioning,
- multi-service orchestration.

If we need those for advanced server mode later, fine.
But not for the core promise.

---

## 11. Gateway Reframed as a Subsystem

The right answer is not “no gateway ever”.
The right answer is:

> **Gateway is a subsystem inside Yaga Runtime, not the product’s architectural center.**

This means:
- if a transport needs a long-lived connection owner, the runtime owns it,
- if a control socket/API is needed, the runtime exposes it,
- if remote nodes/devices are added later, they connect to runtime-managed endpoints,
- but the top-level system model stays centered on:
  - requests,
  - tasks,
  - agents,
  - events,
  - retries,
  - memory,
  - Mission Control state.

That is a much healthier center of gravity.

---

## 12. Recommended v1/v1.5 Deployment Modes

## Mode A — Default personal/dev install

Target user:
- developer on Linux/macOS

Shape:
- one runtime daemon
- SQLite
- built-in scheduler/retry/watchdog
- optional local UI
- no Docker required

This should be the product default.

## Mode B — Power-user workstation / small team host

Shape:
- one runtime daemon
- optional Postgres
- optional remote access/auth hardening
- optional always-on channel integrations
- optional multi-agent richer setup

Still avoid unnecessary service explosion.

## Mode C — Advanced server deployment

Allowed later:
- multiple runtimes,
- external Postgres,
- reverse proxy,
- managed upgrades,
- stronger auth/remote ops,
- possibly separate web delivery.

But this must be a later deployment profile, not the baseline design pressure.

---

## 13. What This Means for the Rebuild

### Keep
- the event-driven orchestration model,
- explicit A2A contracts,
- request/task/flow separation,
- retry/watchdog/recovery logic,
- Mission Control domain semantics,
- operator observability,
- owner-main routing model.

### Rebuild
- Mission Control as integrated module instead of heavy stack,
- runtime around one always-on daemon,
- local store around SQLite-first design,
- queue/retry/watchdog around DB-backed scheduling,
- install/deploy around one-command user-local setup,
- UI as optional local layer, not mandatory operational dependency.

### Avoid
- Redis-first thinking,
- Dapr-first thinking,
- Docker-first thinking,
- “split into many services because that looks enterprise”,
- forcing every product concern through a Gateway-branded mental model.

---

## 14. One-Paragraph Decision

The best pattern for Yaga is **not** a Gateway-centric distributed stack by default.
The best pattern is a **local-first runtime daemon** that owns agent execution, adapters, events, retries, watchdogs, memory, and local APIs, while **Mission Control remains a first-party optional planning/operator integration** instead of a separate heavy platform. Gateway-like behavior still exists where needed, but as a subsystem of the runtime. The default install should run on Linux and macOS with one command, one runtime, one local state store, and no mandatory Docker/Redis/Dapr stack.

---

## 15. Practical Naming Recommendation

### Product-level names
- **Yaga Runtime** — preferred
- **Agent Runtime** — acceptable technical name

### Internal subsystem names
- **Runtime daemon** — preferred always-on process name
- **Adapter subsystem** — preferred over “Gateway” as the whole architecture
- **Mission Control integration** — preferred first-party planning/operator layer

### Naming to avoid as the top-level product term
- “Gateway” — too transport-centric
- “Orchestrator” — too narrow
- “Framework” — too vague and too heavy-sounding

Best short sentence:

> **Yaga Runtime is a lightweight local control plane for developer agents.**
