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
- `from_agent != to_agent`.
- `status` enum: `received|accepted|rejected|completed|failed|blocked`.
- `dedup_key` MUST be stable across safe retries of the same handoff/callback intent.
