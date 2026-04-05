# Event Topic Map

> **Coverage:** v1 event map with capability tags (`core-slice`, `full-v1`). Full canonical event catalogue is in `reference/canonical-events.md`. Additional topics will be mapped as bounded contexts are implemented.
>
> **Note on consumers:** `Audit Writer` and `Metrics Pipeline` listed below are planned v1 components; they are not yet scoped in `implementation/interfaces-v1.md` or `implementation/repo-structure-v1.md` and will be added in a follow-up slice.
>
> **Note on aggregate types:** `reply.published` and `reply.publication_failed` use `reply` as the aggregate segment in the topic name, consistent with the `yaga.v1.<context>.<aggregate>.<event>` naming convention. `handoff.rejected` and `handoff.timeout` are operationally critical v1 events (referenced by runbooks and watchdog policies); they are included here even though their consumers are policy-driven rather than direct stream consumers.

| Canonical Event | Topic | Aggregate Type | Producer | Consumers | Capability Tag |
|-----------------|-------|---------------|----------|-----------|----------------|
| `request.received` | `yaga.v1.runtime.request.received` | `request` | Surface Adapter | Runtime Orchestrator, Audit Writer | `core-slice` |
| `request.normalization_accepted` | `yaga.v1.runtime.request.normalization_accepted` | `request` | Runtime Orchestrator | Request Projection, Mission Control | `core-slice` |
| `task.created` | `yaga.v1.runtime.task.created` | `task` | Strategic Owner | Task Projection, Agent Inbox | `core-slice` |
| `handoff.dispatched` | `yaga.v1.runtime.handoff.dispatched` | `handoff` | Requester Agent | Assignee Inbox, Watchdog Policy | `core-slice` |
| `handoff.accepted` | `yaga.v1.runtime.handoff.accepted` | `handoff` | Assignee Agent | Task Projection | `core-slice` |
| `handoff.rejected` | `yaga.v1.runtime.handoff.rejected` | `handoff` | Assignee Agent | Watchdog Policy, Retry Policy | `core-slice` |
| `handoff.timeout` | `yaga.v1.runtime.handoff.timeout` | `handoff` | Runtime (Watchdog) | Retry Policy, On-call Alerts | `full-v1` |
| `execution.timeout` | `yaga.v1.runtime.execution.timeout` | `execution` | Runtime (Watchdog) | Recovery Policy, On-call Alerts | `full-v1` |
| `workflow.timeout` | `yaga.v1.runtime.workflow.timeout` | `workflow` | Runtime (Watchdog) | Workflow Escalation Policy | `full-v1` |
| `callback.timeout` | `yaga.v1.runtime.callback.timeout` | `callback` | Runtime (Watchdog) | Callback Recovery Policy | `full-v1` |
| `task.completed` | `yaga.v1.runtime.task.completed` | `task` | Owner Agent | Publication Service, Requester Callback Handler, Metrics Pipeline | `core-slice` |
| `reply.published` | `yaga.v1.runtime.reply.published` | `reply` | Adapter | Request Projection, Audit Log | `core-slice` |
| `reply.publication_failed` | `yaga.v1.runtime.reply.publication_failed` | `reply` | Adapter | Retry Policy, On-call Alerts | `core-slice` |
