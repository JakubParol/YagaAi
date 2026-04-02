# Canonical Events

All events carry: `correlation_id`, `causation_id`, `dedup_key`, `event_type`,
`timestamp`, `actor`, `version`. Additional fields are per-type.

## Lifecycle Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `task.created` | requester | `task_ref`, `owner`, `requester`, `callback_target` | Task created and assigned |
| `task.accepted` | owner | `task_ref`, `owner`, `timestamp` | Owner explicitly accepts task |
| `task.rejected` | assignee | `task_ref`, `assignee`, `reason` | Assignee declines; ownership reverts |
| `task.started` | owner | `task_ref`, `owner` | Work begins |
| `task.completed` | owner | `task_ref`, `outcome`, `artifacts` | Work done; callback triggered |
| `task.blocked` | owner | `task_ref`, `reason`, `recovery_owner` | Task cannot proceed |
| `task.unblocked` | recovery_owner | `task_ref`, `resolution` | Block resolved |
| `task.escalated` | system or owner | `task_ref`, `reason`, `escalation_target` | Escalated to James |
| `task.cancelled` | requester or James | `task_ref`, `reason` | Task terminated |

## Handoff Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `handoff.dispatched` | requester | `handoff_ref`, `owner`, `requester`, `goal`, `callback_target` | Handoff sent |
| `handoff.accepted` | new owner | `handoff_ref`, `owner` | Owner accepts |
| `handoff.rejected` | assignee | `handoff_ref`, `assignee`, `reason` | Assignee declines |
| `handoff.timeout` | system | `handoff_ref`, `elapsed`, `recovery_action` | Handoff not accepted within window |

Note: `handoff.claimed` is removed from v1. Use `handoff.accepted` for all ownership transfers.

## Artifact Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `artifact.produced` | agent | `artifact_ref`, `task_ref`, `artifact_type` | Artifact created |
| `artifact.validated` | agent or system | `artifact_ref`, `validation_result` | Artifact passed validation |
| `artifact.invalidated` | agent or system | `artifact_ref`, `reason` | Artifact failed validation |
| `artifact.referenced` | agent | `artifact_ref`, `referencing_task` | Artifact used by another task |

## Memory Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `memory.written` | agent | `agent`, `layer`, `key`, `justification` | Memory entry created or updated |
| `memory.corrected` | agent or operator | `agent`, `key`, `prior_value`, `new_value`, `reason` | Existing entry corrected |
| `memory.retracted` | agent or operator | `agent`, `key`, `reason`, `retracted_by` | Entry marked retracted |
| `memory.write_failed` | system | `agent`, `layer`, `key`, `error` | Memory write failed; task not blocked |
| `memory.context_overflow` | agent | `agent`, `task_ref`, `layers_truncated` | Context budget exceeded; memory selectively loaded |
| `memory.stale_read` | agent | `agent`, `key`, `retracted_at` | Agent read a retracted memory entry |

## Execution Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `execution.started` | runtime | `task_ref`, `runtime`, `actor` | Execution begun |
| `execution.timeout` | runtime or system | `task_ref`, `runtime`, `elapsed` | Execution timed out |
| `tool.called` | runtime | `task_ref`, `tool_name`, `inputs` | Tool invocation |
| `tool.returned` | runtime | `task_ref`, `tool_name`, `output`, `success` | Tool result |

## Flow Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `flow.started` | James or MC | `flow_ref`, `owner`, `goal` | Flow initiated |
| `flow.completed` | system | `flow_ref`, `outcome` | Flow reached terminal state |
| `flow.escalated` | system | `flow_ref`, `reason`, `escalation_target` | Flow escalated |
| `review_loop.incremented` | MC | `us_ref`, `loop_count` | Code Review → In Progress transition; counter incremented |
| `review_loop.limit_reached` | MC | `us_ref`, `loop_count` | Max code review returns hit; auto-escalation triggered |
| `verify_loop.incremented` | MC | `us_ref`, `loop_count` | Verify → In Progress transition; counter incremented |
| `verify_loop.limit_reached` | MC | `us_ref`, `loop_count` | Max verify failures hit; auto-escalation triggered |
| `transition.rejected` | MC | `us_ref`, `attempted_transition`, `reason` | MC rejected an agent's intent event; state unchanged |

## Improvement Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `improvement.proposed` | agent | `proposed_by`, `target`, `justification` | Improvement candidate created |
| `improvement.approved` | James or operator | `candidate_ref`, `approver` | Candidate approved; deployment begins |
| `improvement.rejected` | James or operator | `candidate_ref`, `reason` | Candidate rejected |
| `improvement.deployed` | system | `candidate_ref`, `version_tag` | Change deployed |
| `improvement.regression_detected` | system | `candidate_ref`, `baseline_test`, `result` | Baseline test failed; rollback triggered |

## Callback Events

| Event Type | Emitted by | Key fields | Meaning |
|------------|-----------|------------|---------|
| `callback.sent` | agent | `task_ref`, `callback_target`, `outcome`, `artifacts` | Result returned to requester |
| `callback.received` | callback_target | `task_ref`, `outcome` | Requester acknowledged result |
| `callback.failed` | system | `task_ref`, `callback_target`, `error` | Callback delivery failed |
