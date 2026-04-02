# Artifact Model

## What an Artifact Is

An artifact is a durable, versioned work result produced by a task and passed between
agents or stored for audit. Artifacts are the primary mechanism for moving work products
through the system.

An artifact is not:
- a memory entry (memory is per-agent context; artifacts are task outputs)
- an event (events record what happened; artifacts carry what was produced)
- an inline message (artifacts are addressable, storable references)

## Artifact Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique artifact identifier |
| `type` | Yes | Artifact type (see below) |
| `produced_by` | Yes | Agent and task that produced it |
| `task_ref` | Yes | Task this artifact belongs to |
| `correlation_id` | Yes | Links to parent flow |
| `version` | Yes | Artifact version (incremented on update) |
| `content_ref` | Yes | Pointer to content (storage path, URL, or inline) |
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

## Artifact Lifecycle

```
draft → produced → validated → [referenced by other tasks]
                             ↓
                         superseded (if replaced by a newer version)
```

- **draft**: Partially produced; not yet safe to reference
- **produced**: Complete and ready to reference
- **validated**: Explicitly checked against expected shape or criteria
- **superseded**: A newer version of this artifact exists; prior version retained for audit

## Lineage

Artifacts carry a lineage chain:

- `produced_by`: task and agent that created the artifact
- `derived_from`: references to prior artifacts this one was built on (optional)
- `referenced_by`: tasks that consumed this artifact

This supports full provenance tracking: given any output, trace back to the inputs
and execution that produced it.

## Passing Artifacts Between Agents

Artifacts are passed by reference, not by value. A handoff includes `input_artifacts`
as a list of artifact IDs. The receiving agent loads the artifact from the artifact store.

Inline context in a handoff (the `input_context` field) is for small, ephemeral context
that does not need to be stored as a first-class artifact.
