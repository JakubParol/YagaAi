# Artifact Model

## What an Artifact Is

An artifact is a durable, versioned work result produced by a task and passed between
agents or stored for audit. Artifacts are the primary mechanism for moving work products
through the system.

An artifact is not:
- a memory entry (memory is per-agent context; artifacts are task outputs)
- an event (events record what happened; artifacts carry what was produced)
- an inline message (artifacts are addressable, storable references)
- the durable source of truth for request routing or reply-publication state

## Artifact Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique artifact identifier |
| `type` | Yes | Artifact type |
| `produced_by` | Yes | Agent and task that produced it |
| `task_ref` | Yes | Task this artifact belongs to |
| `correlation_id` | Yes | Links to parent execution lineage |
| `version` | Yes | Artifact version |
| `content_ref` | Yes | Pointer to content |
| `summary` | Yes | Brief human-readable description |
| `created_at` | Yes | Timestamp |
| `status` | Yes | `draft`, `produced`, `validated`, `superseded` |

## Artifact Types

| Type | Description | Typical producer |
|------|-------------|-----------------|
| `research-report` | Research findings, synthesis, sources | Alex |
| `implementation-diff` | Code change; PR reference or diff | Naomi |
| `test-result` | Test run output and summary | Naomi or Amos |
| `review-comments` | Code review or peer review comments | Amos |
| `verify-evidence` | Functional verification record | Amos |
| `approval-record` | Formal approval of a review or verify step | Amos |
| `execution-log` | Structured trace of an execution run | runtime |
| `plan` | Task plan or decomposition created by an agent | Naomi or James |
| `escalation-report` | Summary of an escalation with context | system or James |
| `reply-draft` | Candidate human-visible reply content before publication | James / owner path |

## Artifact Lifecycle

```text
draft → produced → validated → [referenced by other tasks]
                             ↓
                         superseded
```

- **draft**: partially produced; not yet safe to reference
- **produced**: complete and ready to reference
- **validated**: explicitly checked against expected shape or criteria
- **superseded**: newer version exists; prior version retained for audit

## Lineage

Artifacts carry lineage:
- `produced_by`: task and agent that created the artifact
- `derived_from`: optional references to prior artifacts
- `referenced_by`: tasks that consumed this artifact

This supports full provenance tracking.

## Passing Artifacts Between Agents

Artifacts are passed by reference, not by value. A handoff includes `input_artifacts`
as a list of artifact IDs. The receiving agent loads the artifact from the artifact store.

Inline `input_context` is for small ephemeral context that does not need to become a
first-class artifact.

## Boundary Reminder: Artifacts and Reply Routing

Artifacts may contain content that is later published to a human.
That does **not** make artifacts the source of truth for:
- reply target
- publication state
- publish success / failure
- fallback routing decisions

Those belong to the request record and related event/audit path.