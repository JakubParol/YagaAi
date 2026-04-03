# Handoff Contract

## Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique handoff identifier |
| `correlation_id` | string | Yes | Links to parent execution lineage |
| `causation_id` | string | Yes | Event that triggered this handoff |
| `dedup_key` | string | Yes | Idempotency key for the handoff message |
| `owner` | agent_id | Yes | Agent taking execution ownership |
| `requester` | agent_id | Yes | Agent requesting the work |
| `executor` | agent_id | No | Optional explicit executor if different from owner |
| `goal` | string | Yes | What needs to be accomplished |
| `definition_of_done` | string | Yes | Explicit acceptance criteria |
| `input_artifacts` | list[artifact_ref] | If applicable | References to prior work or context |
| `input_context` | string | If applicable | Inline context when no artifact exists |
| `callback_target` | agent/session ref | Yes | Where loop returns go (operational callback) |
| `strategic_callback` | agent/session ref | No | Where terminal strategic outcomes go if distinct |
| `priority` | enum | Yes | `low`, `normal`, `high`, `urgent` |
| `deadline` | timestamp | If applicable | Expected completion time or SLA |
| `execution_mode` | enum | Yes | `session-bound` or `detached` |
| `version` | string | Yes | Contract schema version |

## Request / Reply Routing Fields

These fields apply to **user-originated durable work**. They keep the handoff linked to the
request-routing/publication model without making the handoff itself the source of truth.

| Field | Required | Meaning |
|-------|----------|---------|
| `request_id` | Yes for user-originated durable work | Durable identity of the originating request |
| `request_class` | Recommended | `session-bound` or `durable` |
| `reply_target_ref` | Recommended | Pointer/reference to authoritative reply-routing state |
| `reply_target_version` | Optional | Version for concurrency / stale-snapshot detection |
| `reply_session_key` | Optional | Current publish-capable endpoint snapshot; advisory only |

### v1 carriage rule

- `request_id` travels inline.
- Reply-routing truth remains authoritative on the request record.
- `reply_session_key` is a read-only snapshot when present.
- Specialists must not mutate reply routing directly by default.

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
| `request_id` | If applicable | Originating durable request |

## Field Matrix: Do Not Collapse These

| Field | Role |
|-------|------|
| `callback_target` | Operational loop-return destination |
| `strategic_callback` | Terminal strategic-notification destination when distinct |
| `reply_target_ref` | Pointer to authoritative human-reply routing state |
| `reply_session_key` | Concrete current publish endpoint snapshot |

## Invariants

- A handoff without a `callback_target` is only allowed for `session-bound` execution with
  an expected inline response.
- A handoff without a `definition_of_done` must be rejected by the receiving agent.
- Ownership does not transfer until an `accepted` response is emitted.
- Rejected handoffs return ownership to the requester. The requester must address the
  rejection reason before retrying. After 2 rejections, the requester must escalate to James.
- A handoff without `strategic_callback` uses `callback_target` for all outcomes.
- When a `strategic_callback` is set (dual callback pattern), terminal outcomes
  (Done, Escalated) go to `strategic_callback`; loop returns go to `callback_target`.
- Reply/publication metadata does not make the handoff the source of truth for human reply routing.
  The request record remains authoritative.
- Specialists may read routing metadata needed for context, but must not treat themselves as
  owners of reply routing or publication state.
- `reply_session_key` must be treated as advisory/read-only when present. It may become stale.
- `request_id` links the handoff back to durable request state; it does not replace `correlation_id`.
