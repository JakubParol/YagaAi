# Event Topic Map

| Canonical Event | Topic | Producer | Consumers |
|-----------------|-------|----------|-----------|
| `request.received` | `yaga.v1.runtime.request.received` | Surface Adapter | Runtime Orchestrator, Audit Writer |
| `request.normalization_accepted` | `yaga.v1.runtime.request.normalization_accepted` | Runtime Orchestrator | Request Projection, Mission Control |
| `task.created` | `yaga.v1.runtime.task.created` | Strategic Owner | Task Projection, Agent Inbox |
| `handoff.dispatched` | `yaga.v1.runtime.handoff.dispatched` | Requester Agent | Assignee Inbox, Watchdog Policy |
| `handoff.accepted` | `yaga.v1.runtime.handoff.accepted` | Assignee Agent | Task Projection, Requester Callback Handler |
| `task.completed` | `yaga.v1.runtime.task.completed` | Owner Agent | Publication Service, Metrics Pipeline |
| `reply.published` | `yaga.v1.runtime.reply.published` | Adapter | Request Projection, Audit Log |
| `reply.publication_failed` | `yaga.v1.runtime.reply.publication_failed` | Adapter | Retry Policy, On-call Alerts |
