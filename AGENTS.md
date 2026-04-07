# AGENTS.md — YagaAi

## What This Is

YagaAi is a multi-agent runtime specification — a workflow-first control plane
for an AI development team (James, Naomi, Amos, Alex). This repository contains
architecture documentation, contracts, standards, and implementation plans.
There is no application code yet.

## Scope

- **In scope:** architecture docs, API contracts, data models, standards,
  implementation plans, operational runbooks
- **Out of scope:** application code (not yet written), infrastructure,
  deployment

---

## Required Reading — Before Any Work

You **MUST** read these files before making any change in this repository:

| # | File | Why |
|---|------|-----|
| 1 | This file (`AGENTS.md`) | Orientation and navigation rules |
| 2 | [README.md](./README.md) | Project vision, agent squad, tech stack |
| 3 | [docs/INDEX.md](./docs/INDEX.md) | Documentation table of contents — tells you where everything is |

Do **not** skip step 3. The docs index links to all documentation areas and
their own indexes.

---

## How to Find What You Need

1. **Start here** — you already did this by reading `AGENTS.md`
2. **Go to [docs/INDEX.md](./docs/INDEX.md)** — it lists every documentation
   area with a link to its own index
3. **Open the index of the area you need** — each area (standards, agent-runtime,
   etc.) has its own index or README that lists contents and reading order
4. **Follow reading order within each area** — numbered docs build on each other,
   read sequentially

**Rule:** Never read a numbered document (e.g., `05-ownership-lifecycle.md`)
without first reading the documents before it in sequence.

---

## Protocols

### `[E2E]` — Delivery Protocol

When the user includes **`[E2E]`** in their prompt, activate the full delivery
flow: [docs/DELIVERY_PROTOCOL.md](./docs/DELIVERY_PROTOCOL.md).

This protocol uses `mc` CLI for all work-item management (stories, tasks, bugs,
sprints, backlogs). Before making any planning mutations, read the MC CLI skill:
`/home/kuba/.openclaw/skills/mc-cli-router/SKILL.md`

Do **not** activate the delivery protocol for regular tasks without `[E2E]`.

---

## Rules

- Read required files before making changes — no exceptions
- Follow [documentation-standards.md](./docs/standards/documentation-standards.md) when creating or editing docs
- Follow the relevant coding standards when writing code
- Every new doc must be linked from its parent index — no orphaned files
- When in doubt about reading order, check the index of the directory you are in
- Do not restructure documentation without explicit approval

## Navigation

- [README.md](./README.md) — project overview
- [docs/INDEX.md](./docs/INDEX.md) — documentation table of contents
