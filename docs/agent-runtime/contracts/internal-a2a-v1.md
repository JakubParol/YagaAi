# Internal A2A Contract v1

## Scope
All internal agent-to-agent handoff envelopes, acceptance, and completion. Covers all agent pairs: James→Naomi, James→Alex, Naomi→Amos, Naomi→Alex, and any future additions.

## Handoff Payload
```json
{
  "handoff_id":"hof_01",
  "request_id":"req_01",
  "from_agent":"naomi",
  "to_agent":"alex",
  "goal":"Research framework options",
  "definition_of_done":"Provide ranked options with trade-offs",
  "callback_target":"naomi",
  "correlation_id":"corr_01",
  "causation_id":"evt_01",
  "dedup_key":"msg_hof_01_dispatch_1"
}
```

## Ack / Accept / Complete
### Ack (transport-level)
```json
{"handoff_id":"hof_01","status":"received","received_at":"2026-04-04T10:00:00Z"}
```

### Accept
```json
{"handoff_id":"hof_01","status":"accepted","owner":"alex","accepted_at":"2026-04-04T10:00:05Z"}
```

### Complete
```json
{
  "handoff_id":"hof_01",
  "status":"completed",
  "outcome":"done",
  "summary":"3 viable options with recommendation",
  "artifacts":["artifact://research/options-v1.md"]
}
```

## Validation
- `handoff_id`, `from_agent`, `to_agent`, `goal`, `definition_of_done`, `callback_target`, `dedup_key` required.
- `correlation_id` always required (audit/replay linkage per `11-observability-and-audit.md`).
- `request_id` required when the handoff originates from user-originated durable work (per `03-runtime-and-a2a.md`); nullable for agent-internal tasks with no user request.
- `from_agent != to_agent`.
- `status` enum: `received|accepted|rejected|completed|failed|blocked`.
- `outcome` enum (set on completion): `done|partial|failed|blocked|escalated`. For the kickoff slice, only `done`, `failed`, and `blocked` are expected in normal paths; `partial` and `escalated` are schema-valid but reserved for richer workflow slices.
- `dedup_key` MUST be stable across safe retries of the same handoff/callback intent.

Completion note:
- `status=completed` means the assignee emitted a terminal completion message.
- `outcome` describes the semantic result of that completion and may still require strategic recovery or operator handling.

## Field Naming Note
This contract uses `from_agent`/`to_agent` (dispatch-centric naming for v1). The full handoff field set — including `priority`, `execution_mode`, `input_artifacts`, `reply_target_ref`, and reply routing fields — is defined in `reference/handoff-contract.md`. The v1 thin-slice omits those fields; implementers adding richer handoff payloads should treat `handoff-contract.md` as the authoritative schema extension point.

## Persistence Note
`task_id` is not part of the A2A wire payload but is required (`NOT NULL`) in the `handoffs` SQL table. The runtime resolves it from the originating task context at dispatch time before writing to storage. The dispatching agent's task record is the source of this linkage.
