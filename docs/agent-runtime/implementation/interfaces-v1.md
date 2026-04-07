# Interfaces v1

## Services

Capability tags:
- `core-slice` — required for minimum runtime bring-up.
- `full-v1` — required for full local operator/UI/CLI surface.

- `IngressService`
  - `accept_request(command: AcceptRequestCommand) -> RequestAccepted`
  - Tag: `core-slice`

- `OrchestratorService`
  - `create_task(command: CreateTaskCommand) -> TaskCreated`
  - `dispatch_handoff(command: DispatchHandoffCommand) -> HandoffDispatched`
  - Tag: `core-slice`

- `HandoffService`
  - `accept(command: AcceptHandoffCommand) -> HandoffAccepted`
  - `reject(command: RejectHandoffCommand) -> HandoffRejected`
  - Tag: `core-slice`

- `TaskService`
  - `complete(command: CompleteTaskCommand) -> TaskCompleted`
  - Tag: `core-slice`

- `WatchdogService`
  - `arm(timer: WatchdogTimer) -> WatchdogArmed`
  - `cancel(timer_id: str) -> WatchdogCancelled`
  - Internal runtime module only; not a separate service/process/deployment unit
  - Tag: `core-slice`

- `EventStoreService`
  - `append(event: DomainEvent) -> EventAppended`
  - `read_stream(aggregate_key: str, from_sequence: int) -> list[DomainEvent]`
  - Tag: `core-slice`

- `PolicyEnforcer`
  - `handle(event: DomainEvent) -> list[Command]`
  - (Reacts to domain events and emits named policy commands per `reference/policies.md`)
  - Tag: `core-slice`

- `MemoryService`
  - `write(entry: MemoryEntry) -> MemoryWriteResult`
  - `search(query: MemoryQuery) -> MemoryResults`
  - Tag: `full-v1`

- `PublicationService`
  - `record_attempt(command: RecordPublicationAttemptCommand) -> PublicationAttemptRecorded`
  - `record_result(command: RecordPublicationResultCommand) -> PublicationResultRecorded`
  - Tag: `core-slice`

- `RuntimeQueryService`
  - `get_run_state(filter: RunStateFilter) -> RunStateSnapshot`
  - `get_queue_state(filter: QueueFilter) -> QueueSnapshot`
  - `get_event_timeline(filter: EventTimelineFilter) -> EventTimeline`
  - Tag: `full-v1`

- `RecoveryService`
  - `retry(command: RetryCommand) -> RetryIssued`
  - `escalate(command: EscalateCommand) -> EscalationIssued`
  - Tag: `full-v1`

- `AgentOpsService`
  - `list_agents(filter: AgentFilter) -> AgentList`
  - `interrupt_session(command: InterruptSessionCommand) -> SessionInterruptAccepted`
  - Tag: `full-v1`

- `DiagnosticsService`
  - `get_runtime_health() -> RuntimeHealth`
  - `get_memory_index_health() -> MemoryIndexHealth`
  - Tag: `full-v1`

## Background Workers (hosted inside `services/runtime`)

These event consumers run as background loops inside the runtime daemon, not as separate default apps:

- **Runtime Projection Worker** — materializes `request_projection`, `task_projection`, and `publication_projection` from ordered event streams
- **Planning Integration Projection Worker** — materializes planning-specific loop counters when an integration such as MC is enabled
- **Agent Inbox / Assignee Inbox** — delivers dispatched handoffs to target agents; backed by `HandoffService.accept()`
- **Requester Callback Handler** — processes task completion callbacks routed back to requester; backed by `TaskService.complete()`
- **Watchdog Policy / Retry Policy** — event-driven reactions handled by `PolicyEnforcer.handle()`

## DTO Boundaries
- External DTOs: HTTP/webhook/A2A payloads.
- Internal DTOs: command/event models.
- Persistence DTOs: ORM rows.

Mapping rule:
- Convert at boundary once; domain services operate only on internal DTOs.
