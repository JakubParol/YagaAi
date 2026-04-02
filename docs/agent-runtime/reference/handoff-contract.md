# Handoff Contract

## Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique handoff identifier |
| `correlation_id` | string | Yes | Links to parent flow or request |
| `causation_id` | string | Yes | Event that triggered this handoff |
| `dedup_key` | string | Yes | For idempotent processing |
| `owner` | agent_id | Yes | Agent taking ownership of the work |
| `requester` | agent_id | Yes | Agent requesting the work |
| `executor` | agent_id | No | Optional explicit executor if different from owner |
| `goal` | string | Yes | What needs to be accomplished |
| `definition_of_done` | string | Yes | Explicit acceptance criteria |
| `input_artifacts` | list[artifact_ref] | If applicable | References to prior work or context |
| `input_context` | string | If applicable | Inline context when no artifact exists |
| `callback_target` | agent_id | Yes | Where loop returns go (operational callback) |
| `strategic_callback` | agent_id | No | Where terminal outcomes go (Done, Escalated); defaults to `callback_target` if absent |
| `priority` | enum | Yes | `low`, `normal`, `high`, `urgent` |
| `deadline` | timestamp | If applicable | Expected completion time or SLA |
| `execution_mode` | enum | Yes | `session-bound` or `detached` |
| `version` | string | Yes | Contract schema version |

## Acceptance Response

When an agent receives a handoff, they must respond with one of:

| Response | Fields | Meaning |
|----------|--------|---------|
| `accepted` | `handoff_id`, `owner`, `timestamp` | Taking ownership; task moves to `Accepted` |
| `rejected` | `handoff_id`, `assignee`, `reason`, `timestamp` | Declining; ownership reverts to requester |

`claimed` is not a v1 response. Use `accepted` for all ownership transfers.

Acceptance is not implied by silence. Unacknowledged handoffs trigger workflow timeouts.

## Completion Response

When a task completes, the owner sends a callback event to `callback_target`:

| Field | Required | Description |
|-------|----------|-------------|
| `handoff_id` | Yes | Reference to original handoff |
| `task_ref` | Yes | Associated task |
| `outcome` | Yes | `done`, `partial`, `failed`, `blocked`, `escalated` |
| `artifacts` | If applicable | References to produced artifacts |
| `summary` | Yes | Brief description of outcome |
| `reason` | If outcome ≠ done | Reason for partial, failed, or blocked outcome |

## Invariants

- A handoff without a `callback_target` is only allowed for `session-bound` execution with
  an expected inline response.
- A handoff without a `definition_of_done` must be rejected by the receiving agent.
- Ownership does not transfer until an `accepted` response is emitted.
- Rejected handoffs return ownership to the requester. The requester must address the
  rejection reason before retrying. After 2 rejections, the requester must escalate to James.
- A handoff without `strategic_callback` uses `callback_target` for all outcomes.
  When a `strategic_callback` is set (dual callback pattern), terminal outcomes
  (Done, Escalated) go to `strategic_callback`; loop returns go to `callback_target`.
