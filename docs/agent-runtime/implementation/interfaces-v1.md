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

## DTO Boundaries
- External DTOs: HTTP/webhook/A2A payloads.
- Internal DTOs: command/event models.
- Persistence DTOs: ORM rows.

Mapping rule:
- Convert at boundary once; domain services operate only on internal DTOs.
