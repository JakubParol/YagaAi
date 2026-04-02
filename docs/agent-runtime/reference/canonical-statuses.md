# Canonical Statuses

## Task Statuses

| Status | Meaning | Entry condition | Exit conditions |
|--------|---------|----------------|----------------|
| `Created` | Task exists, not yet acknowledged by assignee | Task created by requester | → `Accepted` (assignee accepts) / `Cancelled` |
| `Accepted` | Assignee has explicitly taken ownership | Assignee emits accepted event | → `In Progress` (work begins) / `Blocked` / `Cancelled` |
| `In Progress` | Active work underway | Owner begins work | → `Review` / `Blocked` / `Cancelled` |
| `Review` | Submitted for code review or peer check | Owner submits artifact | → `Verify` (approved) / `In Progress` (returned) / `Escalated` |
| `Verify` | Submitted for functional verification | Reviewer approves code review | → `Done` (passed) / `In Progress` (failed) / `Escalated` |
| `Done` | Work complete; callback sent | Verifier passes | terminal |
| `Blocked` | Cannot proceed; reason required | Owner or system blocks | → `In Progress` (resolved) / `Escalated` / `Cancelled` |
| `Escalated` | Active recovery owner is James | Loop limit exceeded or deadlock | → `In Progress` (resolved) / `Done` / `Cancelled` |
| `Cancelled` | Explicitly terminated | Requester or James cancels | terminal |

## User Story (Mission Control) Statuses

| Status | Meaning | Assigned to |
|--------|---------|-------------|
| `Created` | US exists, not yet started | — |
| `In Progress` | Naomi is working | Naomi |
| `Code Review` | Submitted for Amos' code review | Amos |
| `Verify` | Code review passed; Amos verifies | Amos |
| `Done` | Verify passed; work accepted | — |
| `Blocked` | Cannot proceed; reason on record | Owner |
| `Escalated` | James is active recovery owner | James |
| `Cancelled` | Explicitly terminated | — |

## Transition Rules

- `Done` and `Cancelled` are terminal. No further transitions allowed.
- `Blocked` and `Escalated` are near-terminal. They have defined exit paths and require active recovery.
- `Escalated` may only be resolved by James.
- Moving from `Blocked` to `In Progress` requires an explicit unblock event with a reason.
- Moving from `Review` to `In Progress` requires review comments attached to the task.
- Moving from `Verify` to `In Progress` requires verify failure notes attached to the task.
- Status overrides by an operator are allowed but must include a reason and are audit-logged.

## Review Loop Counter

The system tracks the number of times a US returns from `Code Review` to `In Progress`.

**Counter increment:** The `review_loop.incremented` event is emitted when a US transitions
`Code Review → In Progress` (i.e., when Amos returns with comments). It is NOT emitted
on first entry to `Code Review`.

| Loop Count | Meaning | Action |
|------------|---------|--------|
| 0 | First Code Review, no returns yet | Normal |
| 1–2 | Prior returns with comments | Normal |
| 3 | Third return; final allowed cycle | If still unresolved after this review: escalate |
| >3 | Not allowed | `review_loop.limit_reached` emitted; auto-escalation to James |

**Reset policy:** The counter does NOT reset when a US moves to `Verify` or returns from
`Verify` to `In Progress`. It is a lifetime per-US counter.

## Verify Loop Counter

The system tracks the number of times a US returns from `Verify` to `In Progress`.

**Counter increment:** The `verify_loop.incremented` event is emitted when a US transitions
`Verify → In Progress` (i.e., when Amos records a verify failure).

| Loop Count | Meaning | Action |
|------------|---------|--------|
| 0–1 | First or second verify attempt | Normal |
| 2 | Second return from Verify; final allowed cycle | If still failing: escalate |
| >2 | Not allowed | `verify_loop.limit_reached` emitted; auto-escalation to James |
