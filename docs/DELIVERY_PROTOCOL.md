# Delivery Protocol

End-to-end delivery flow for work-items (user stories, bugs) through the
Mission Control workflow.

## When to Use

Use this protocol **only** when the user includes `[E2E]` in their prompt.
Do not activate for regular coding, documentation, or research tasks.

## Project Maturity

This project does not yet have application code, deploy scripts, quality gates,
or infrastructure. Phases that depend on missing capabilities are marked with
`🚧 NOT YET AVAILABLE`. When you hit such a phase:

1. **Skip it** — do not attempt to run commands that do not exist.
2. **Report the skip** in your status output (e.g., "Phase 4 skipped — no
   deploy pipeline yet").
3. **Adjust the stop point** — if deploy is unavailable, the flow stops after
   PR creation (Phase 2) + review (Phase 3) instead of after DEV deploy.
   Move the work-item to `CODE_REVIEW` and stop. Do not move to `VERIFY`
   without a successful deploy.

As the project matures, these markers will be removed.

## Preconditions

- Read repo AGENTS.md and required reading before starting.
- For all planning operations (work-items, sprints, backlogs, labels, agents),
  use `mc` CLI only — no direct DB or API mutations.
- Read the MC CLI skill before making planning mutations:
  `/home/kuba/.openclaw/skills/mc-cli-router/SKILL.md`
- A work-item means a User Story, Task, or Bug.

## MC CLI Execution Context

The dispatch/delivery contract provides an explicit API target URL
(e.g., `http://127.0.0.1:5000` for DEV, `http://127.0.0.1:5100` for PROD).

Rules:
1. When dispatch provides an API target, use `mc --api-base <target-url>` for
   **all** operations (reads and writes).
2. Bare `mc` (no `--api-base`) defaults to PROD — safe for direct operator
   usage but agents must always use the explicit target from their dispatch.
3. Execution target is a property of the dispatched run, not of the agent
   identity.

## Core Delivery Rule

- The default autonomous objective is to reach **VERIFY** safely, not to merge.
- A work-item may enter VERIFY **only after a successful DEV deploy**.
- **Merge, PROD deploy, status DONE, and branch cleanup are human-gated.**
- Never assume verification is complete.
- Never infer release approval from silence, green checks, or PR existence.

---

## Phase 0 — Preparation

1. Read the work-item details using MC CLI by element code.
2. If the work-item is not attached to the current sprint, attach it.
3. If it is not attached to an epic, attach it to the best matching epic.
4. Add labels to the work-item.
5. Assign the story to Naomi unless the user directs otherwise.
6. Checkout `main`, pull latest.
7. Create a new implementation branch using the work-item code and a short
   description.
8. Confirm you are on the new branch, not on `main`.

## Phase 1 — Implementation

### 1.1 — Plan (the plan IS the MC tasks)

1. Design atomic implementation tasks for the target work-item.
2. Record each task in MC via `mc task create` with
   `--set parent_id=<WORK_ITEM_ID>`.
   Every task MUST have `parent_id` set. Do NOT use `story_id`.
3. Verify linkage: `mc task list --parent-key <WORK_ITEM_KEY> --output json`
   and confirm `total` matches.

### 1.2 — Execute (task-by-task loop)

4. Set story `IN_PROGRESS` via `mc story update`.
5. For each task sequentially:
   a. Set task `IN_PROGRESS`.
   b. Implement code + commit.
   c. Run quality gates (lint, tests) — skip if not yet configured.
   d. Set task `DONE`.
   e. If blocked: set task `BLOCKED` with `blocked_reason`, report `BLOCKER`,
      stop.
   - Do NOT start the next task until the current one is DONE or BLOCKED.

## Phase 2 — Pull Request

1. Create a PR to `main` using `gh pr create`.
2. Set story status to `CODE_REVIEW` via `mc story update`.

## Phase 3 — Review and Fixes

Code review is delegated to a sub-agent. Maximum **3 review loops** before
escalation.

### 3.1 — Spawn review sub-agent

Use the `Agent` tool with subagent_type `superpowers:code-reviewer` providing:
- Work item key and title
- PR number
- Repo root path
- Instruction to read AGENTS.md and relevant standards before reviewing

**Do NOT spawn the review agent with `isolation: "worktree"`.**

### 3.2 — Handle review result

**If CLEAR:** proceed to Phase 4.

**If DIRTY:**
1. Set story status back to `IN_PROGRESS`.
2. Fix each finding.
3. Run quality gates.
4. Commit and push fixes.
5. Resolve all review comments from the round.
6. Set story status to `CODE_REVIEW`.
7. Loop back to 3.1 — spawn a fresh review sub-agent.

### 3.3 — Escalation

If 3 review loops still return DIRTY:
- Stop and report `BLOCKER`.
- Post a summary of unresolved findings to the PR.
- Escalate to the user.

## Phase 4 — Deploy Candidate to DEV `🚧 NOT YET AVAILABLE`

> Skip this phase until `./infra/deploy.sh` exists. Report the skip in output.

1. Confirm you are on the implementation branch.
2. Run the deploy script: `./infra/deploy.sh dev`
3. Verify: build steps pass, smoke checks pass, `[OK] DEV deploy complete`.
4. If deploy fails: report `BLOCKER`, do NOT retry, do NOT advance story.

## Phase 5 — VERIFY Handoff (default stop point)

1. Move the work-item to `VERIFY` via MC CLI.
2. Assign the story to Amos.
3. Return `VERIFY_READY` with: story/task keys, PR URL, branch name,
   deployed commit SHA, DEV URLs checked.
4. **Stop.**

Do NOT merge, deploy PROD, set DONE, or clean up branches at this point.

## Phase 6 — Post-VERIFY Release (human-gated) `🚧 DEPLOY NOT YET AVAILABLE`

Proceed only after explicit human authorization (e.g., "verified", "merge it",
"deploy prod", "close it").

1. Merge the PR using `gh pr merge`.
2. Checkout `main` and pull.
3. Deploy PROD: `./infra/deploy.sh prod` — skip if deploy script does not exist.
4. Verify PROD deploy — skip if step 3 was skipped.
5. Set story status to `DONE`.
6. Unassign the story.
7. Delete implementation branches (local + remote).

If merge or PROD deploy fails: report `BLOCKER`, do not advance.

---

## Quality Bar

- Zero-warnings policy: fix at source.
- Do not suppress issues with `# noqa`, blanket disables, or lint-ignore hacks
  unless explicitly approved.

## Blocker Protocol

Stop and report `BLOCKER` only when autonomous resolution is not possible.
Do not stop for routine fixable issues (lint errors, straightforward test
failures, review comments).

## Output Contract

Return concise status:
1. `VERIFY_READY`, `DONE`, or `BLOCKER`
2. Changed resources (story/task keys, PR URL, commit refs, deploy target)
3. Follow-up needed (if any)

## Navigation

- [AGENTS.md](../AGENTS.md) — agent orientation and rules
- [docs/INDEX.md](INDEX.md) — documentation table of contents
