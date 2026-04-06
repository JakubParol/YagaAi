# Interfaces v1

## Services

- `IngressService`
  - `accept_request(command: AcceptRequestCommand) -> RequestAccepted`

- `OrchestratorService`
  - `create_task(command: CreateTaskCommand) -> TaskCreated`
  - `dispatch_handoff(command: DispatchHandoffCommand) -> HandoffDispatched`

- `HandoffService`
  - `accept(command: AcceptHandoffCommand) -> HandoffAccepted`
  - `complete(command: CompleteHandoffCommand) -> HandoffCompleted`
  - `reject(command: RejectHandoffCommand) -> HandoffRejected`

- `WatchdogService`
  - `arm(timer: WatchdogTimer) -> WatchdogArmed`
  - `cancel(timer_id: str) -> WatchdogCancelled`

- `EventStoreService`
  - `append(event: DomainEvent) -> EventAppended`
  - `read_stream(aggregate_key: str, from_sequence: int) -> list[DomainEvent]`

- `PolicyEnforcer`
  - `handle(event: DomainEvent) -> list[Command]`
  - (Reacts to domain events and emits named policy commands per `reference/policies.md`)

- `MemoryService`
  - `write(entry: MemoryEntry) -> MemoryWriteResult`
  - `search(query: MemoryQuery) -> MemoryResults`

- `PublicationService`
  - `publish(reply: ReplyCommand) -> PublicationAttempted`

## Background Workers (hosted inside `services/runtime`)

These event consumers run as background loops inside the runtime daemon, not as separate default apps:

- **Runtime Projection Worker** — materializes `request_projection` and `task_projection` from ordered event streams
- **Mission Control Projection Worker** — materializes review/verify loop counters in `task_projection`
- **Agent Inbox / Assignee Inbox** — delivers dispatched handoffs to target agents; backed by `HandoffService.accept()`
- **Requester Callback Handler** — processes handoff completions routed back to requester; backed by `HandoffService.complete()`
- **Watchdog Policy / Retry Policy** — event-driven reactions handled by `PolicyEnforcer.handle()`

## DTO Boundaries
- External DTOs: HTTP/webhook/A2A payloads.
- Internal DTOs: command/event models.
- Persistence DTOs: ORM rows.

Mapping rule:
- Convert at boundary once; domain services operate only on internal DTOs.
