# Interfaces v1

## Services
- `IngressService`
  - `accept_request(command) -> RequestAccepted`
- `OrchestratorService`
  - `create_task(command) -> TaskCreated`
  - `dispatch_handoff(command) -> HandoffDispatched`
- `MemoryService`
  - `write(entry) -> MemoryWriteResult`
  - `search(query) -> MemoryResults`
- `PublicationService`
  - `publish(reply) -> PublicationAttempted`

## DTO Boundaries
- External DTOs: HTTP/webhook/A2A payloads.
- Internal DTOs: command/event models.
- Persistence DTOs: ORM rows.

Mapping rule:
- Convert at boundary once; domain services operate only on internal DTOs.
