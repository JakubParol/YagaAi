# Canonical Statuses

## Task Statuses

| Status | Meaning | Entry condition | Exit conditions |
|--------|---------|----------------|----------------|
| `Created` | Task exists, not yet acknowledged by assignee | Task created by requester | → `Accepted` / `Cancelled` |
| `Accepted` | Assignee has explicitly taken ownership | Assignee emits accepted event | → `In Progress` / `Blocked` / `Cancelled` |
| `In Progress` | Active work underway | Owner begins work | → `Review` / `Blocked` / `Cancelled` |
| `Review` | Submitted for code review or peer check | Owner submits artifact | → `Verify` / `In Progress` / `Escalated` |
| `Verify` | Submitted for functional verification | Reviewer approves code review | → `Done` / `In Progress` / `Escalated` |
| `Done` | Execution work complete; callback obligations satisfied | Verifier passes or terminal work accepted | terminal |
| `Blocked` | Cannot proceed; reason required | Owner or system blocks | → `In Progress` / `Escalated` / `Cancelled` |
| `Escalated` | Active recovery owner is James | Loop limit exceeded or deadlock | → `In Progress` / `Done` / `Cancelled` |
| `Cancelled` | Explicitly terminated | Requester or James cancels | terminal |

### Important clarification

`Done` is a canonical **task / workflow** status.
It does **not** mean the human-visible reply was published successfully.

Request/publication projection labels are not canonical task statuses.

## User Story (Mission Control) Statuses

| Status | Meaning | Assigned to |
|--------|---------|-------------|
| `Created` | US exists, not yet started | — |
| `In Progress` | Naomi is working | Naomi |
| `Code Review` | Submitted for Amos' code review | Amos |
| `Verify` | Code review passed; Amos verifies | Amos |
| `Done` | Verify passed; workflow complete | — |
| `Blocked` | Cannot proceed; reason on record | Owner |
| `Escalated` | James is active recovery owner | James |
| `Cancelled` | Explicitly terminated | — |

## Transition Rules

- `Done` and `Cancelled` are terminal.
- `Blocked` and `Escalated` are near-terminal and require active recovery.
- `Escalated` may only be resolved by James.
- Moving from `Blocked` to `In Progress` requires an explicit unblock event with a reason.
- Moving from `Review` to `In Progress` requires review comments attached to the task.
- Moving from `Verify` to `In Progress` requires verify failure notes attached to the task.
- Status overrides by an operator are allowed but must include a reason and are audit-logged.

## Request / Publication Projection Note

Useful request-level projection labels may include:
- `normalized`
- `delegated`
- `awaiting_callback`
- `reply_publish_pending`
- `reply_published`
- `reply_publish_failed`
- `fallback_required`
- `closed`

These are operator-facing request/publication views.
They are **not** canonical task or US statuses.

## Review Loop Counter

The system tracks how many times a US returns from `Code Review` to `In Progress`.

| Loop Count | Meaning | Action |
|------------|---------|--------|
| 0 | First Code Review, no returns yet | Normal |
| 1–2 | Prior returns with comments | Normal |
| 3 | Third return; final allowed cycle | If still unresolved after this review: escalate |
| >3 | Not allowed | `review_loop.limit_reached` emitted; auto-escalation |

**Reset policy:** does not reset when a US moves to `Verify` or returns from `Verify`.

## Verify Loop Counter

The system tracks how many times a US returns from `Verify` to `In Progress`.

| Loop Count | Meaning | Action |
|------------|---------|--------|
| 0–1 | First or second verify attempt | Normal |
| 2 | Second return from Verify; final allowed cycle | If still failing: escalate |
| >2 | Not allowed | `verify_loop.limit_reached` emitted; auto-escalation |
