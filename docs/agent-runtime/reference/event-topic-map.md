# Event Topic Map

> **Coverage:** v1 thin-slice events only. Full canonical event catalogue is in `reference/canonical-events.md`. Additional topics will be mapped as bounded contexts are implemented.
>
> **Note on consumers:** `Audit Writer` and `Metrics Pipeline` listed below are planned v1 components; they are not yet scoped in `implementation/interfaces-v1.md` or `implementation/repo-structure-v1.md` and will be added in a follow-up slice.

| Canonical Event | Topic | Aggregate Type | Producer | Consumers |
|-----------------|-------|---------------|----------|-----------|
| `request.received` | `yaga.v1.runtime.request.received` | `request` | Surface Adapter | Runtime Orchestrator, Audit Writer |
| `request.normalization_accepted` | `yaga.v1.runtime.request.normalization_accepted` | `request` | Runtime Orchestrator | Request Projection, Mission Control |
| `task.created` | `yaga.v1.runtime.task.created` | `task` | Strategic Owner | Task Projection, Agent Inbox |
| `handoff.dispatched` | `yaga.v1.runtime.handoff.dispatched` | `handoff` | Requester Agent | Assignee Inbox, Watchdog Policy |
| `handoff.accepted` | `yaga.v1.runtime.handoff.accepted` | `handoff` | Assignee Agent | Task Projection, Requester Callback Handler |
| `task.completed` | `yaga.v1.runtime.task.completed` | `task` | Owner Agent | Publication Service, Metrics Pipeline |
| `reply.published` | `yaga.v1.runtime.reply.published` | `request` | Adapter | Request Projection, Audit Log |
| `reply.publication_failed` | `yaga.v1.runtime.reply.publication_failed` | `request` | Adapter | Retry Policy, On-call Alerts |
