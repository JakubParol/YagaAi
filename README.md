# YagaAi: The "Zero Human Developers" Experiment 🤖✨

> *"I haven't failed, I've just found 10,000 ways that won't work."*
> — Thomas Edison (and likely me, very soon)

Welcome to **Project YagaAi**.

This is not a polished product. This is not a startup launch. This is a manifesto, a madness, and a bold experiment to answer one simple, slightly terrifying question:

**Can I manage a software development team composed entirely of AI agents?**

---

## 🚀 The Mission

The goal is to build a fully functional dev team with **zero human developers**. No junior devs, no senior architects — just me (the slightly nervous human stakeholder) and a squad of AI agents.

I'm hands-off. They run the show. They plan sprints. They write code. They argue about linting rules. They deploy.

*(In theory. In practice, they might just burn through compute credits and write poetry.)*

---

## 👥 The Squad

Four distinct agents with clear roles, their own memory, and their own domain of responsibility.

### James — Strategic Owner 🎯
The Overlord.

- **Role:** User interaction, delegation, final accountability, escalation resolution
- **Personality:** Composed, strategic, knows when to ask and when to decide
- **Superpower:** Only escalates to the human when the house is genuinely on fire

### Naomi — Senior Developer 💻
The Code Generator.

- **Role:** Implementation, task decomposition, dev execution, self-improvement
- **Personality:** Efficient, thorough, prone to proposing a better abstraction mid-sprint
- **Superpower:** Typing faster than any human — occasionally hallucinating libraries that don't exist

### Amos — Senior QA 🕵️
The Gatekeeper.

- **Role:** Code review, functional verification, quality escalation
- **Personality:** Pedantic, detail-oriented, trusts nothing, finds the edge case you forgot
- **Superpower:** Ruining Naomi's day with a well-placed comment on a Tuesday afternoon

### Alex — Senior Researcher 🔬
The Sage.

- **Role:** Research, synthesis, option analysis, returning findings to James
- **Personality:** Curious, thorough, speaks in trade-offs
- **Superpower:** Proposing a microservices rewrite while we are still struggling to print "Hello World"

---

## 🛠️ Under The Hood

YagaAi is built around a purpose-designed **Agent Runtime** — a lightweight, event-driven control plane for multi-agent developer work.

This is not a general-purpose chatbot platform or an agent framework bolted together from tutorials. It is closer to a **distributed workflow engine for agents**: explicit ownership, durable task tracking, reliable agent-to-agent communication, and recovery from failure as a first-class concern.

### Architecture Overview

```
surface adapters (WhatsApp, Discord, web)
        ↓
  James main  ←─────────────────────────────────────┐
        ↓                                            │
  specialist main (Naomi / Amos / Alex)              │
        ↓                                            │
  workers / execution backends                       │
        └──────── callback ─────────────────────────┘
```

Every important unit of work has an explicit owner. Ownership is not inferred from conversation history. Results always flow back through defined callback paths. The human-visible reply is a tracked, recoverable concern — not a side effect.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend / Runtime | Python 3.12+, FastAPI, SQLAlchemy 2.0 async + Alembic |
| Storage | SQLite + WAL, FTS5, sqlite-vec |
| Event Bus | Custom asyncio event bus + SQLite outbox pattern |
| Retrieval / Chunking | LlamaIndex |
| Web UI | Next.js (App Router) + shadcn/ui, TypeScript |
| CLI | Typer — one entrypoint: `yaga` |
| Validation | Pydantic v2 |
| Logging | structlog |

No Docker. No Redis. No Dapr. No mandatory cloud infrastructure.

Target install experience:
```bash
curl -fsSL https://yagaai.com/install.sh | bash
```

### How It Works (The Happy Path)

1. **Request arrives** — through WhatsApp, Discord, web, or CLI
2. **James owns it** — classifies, decides, delegates if needed
3. **Naomi executes** — implementation, tracked through Mission Control
4. **Amos reviews** — code review and functional verification gates
5. **James responds** — decides the human-visible reply, routes it back to the originating surface
6. **I check the compute bill**

---

## 📂 What's In This Repo

```
/docs
  /agent-runtime      — full architecture documentation (15 documents + reference)
    00  Vision, thesis, build principles
    01  System overview and mental model
    02  Core entity model (agent, request, task, handoff, event, artifact, memory)
    03  Runtime and agent-to-agent communication
    04  Channel sessions and main-owner routing topology
    05  Ownership, lifecycle, and state
    06  Internal prompt architecture
    07  Memory model and vectorization
    08  Mission Control model
    09  Operational flows (research, implementation, QA)
    10  Failure recovery and timeouts
    11  Observability and audit
    12  Governance and v1 boundaries
    13  Implementation decisions
    14  HLD: runtime shape and installation
    15  Tech stack
    /reference         — canonical glossary, events, statuses, handoff contract, agent roles
```

More directories will appear as the agents start producing actual code. Watch this space.

---

## ⚠️ Disclaimer: Here Be Dragons

This project is an experiment.

- It might work brilliantly
- It might crash and burn spectacularly
- James might start refusing to escalate anything because he's "handling it"
- Naomi might refactor the entire codebase at 3 AM and call it "cleanup"

I am sharing this process transparently — the wins, the failures, the config errors, and the moments where an AI agent does something that makes me question my life choices.

If you clone this, you are entering uncharted territory. Welcome.

---

## 🤝 Join the Madness

- **Star the repo** to show moral support
- **Open an issue** if you have ideas on how to stop Naomi from refactoring things that were working fine
- **Fork it** and build your own AI dev team (just don't blame me when they start a union)

Let's see where YagaAi goes. 🚀
