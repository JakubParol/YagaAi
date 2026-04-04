# Internal A2A Contract v1

## Scope
Naomi↔Alex and Naomi↔Amos handoff envelopes, acceptance, completion.

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
  "causation_id":"evt_01"
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
- `handoff_id`, `from_agent`, `to_agent`, `goal`, `callback_target` required.
- `from_agent != to_agent`.
- `status` enum: `received|accepted|rejected|completed|failed|blocked`.
