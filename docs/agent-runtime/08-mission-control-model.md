# 08 — Mission Control Model

## What Mission Control Is

Mission Control (MC) is the first serious **planning + control-plane integration** for the Agent Runtime.

It may provide:
- work-item planning (`epic`, `story`, `task`, `bug`),
- backlog and sprint context,
- operator-facing UI,
- agent/operator CLI,
- control-plane visibility over execution progress,
- manual or automated flow start from planning state.

Mission Control is important, but it is still an integration.
The runtime must remain able to function without it.

---

## Relation to the Runtime

| Aspect | Agent Runtime | Mission Control |
|--------|---------------|-----------------|
| User-originated ingress | Owns | May link to it |
| Agent execution semantics | Owns | Observes / triggers via integration |
| Handoffs / callbacks / retries / watchdogs | Owns | Does not own |
| Work items / planning context | Integrates with | Owns when present |
| Backlog / sprint / planning UI | Does not own | Owns |
| Operator-facing execution visibility | Exposes runtime truth | May present it in UI/CLI |

---

## Source-of-Truth Boundary

Mission Control may be the source of truth for planning/work-item state when it is present.
It is **not** the source of truth for runtime execution semantics.

| What | Source of Truth |
|------|-----------------|
| Request routing + publication state | runtime request record |
| Handoff semantics | runtime |
| Task execution / callback / retry / watchdog state | runtime |
| Planning work items (`epic`, `story`, `task`, backlog, sprint) | Mission Control when integrated |
| Review / verify loop counters in MC-managed dev flow | Mission Control when integrated |
| Chronological execution evidence | runtime event log |

The runtime must not require MC to exist.
MC must not compete with runtime for ownership of retries, callbacks, or publication truth.

---

## Integration Model

The intended integration path is:

```text
planning system emits intent
  → runtime starts or advances agent work
  → runtime executes, retries, escalates, and records events
  → planning system reflects resulting state through explicit contracts
```

For Mission Control specifically:
- James may create epics/stories/tasks through `mc` CLI,
- an operator may move work into backlog / active sprint,
- a human or James may start the development flow,
- runtime then takes responsibility for execution semantics,
- MC shows work-item and control-plane state back to the operator.

This same shape must remain possible for future integrations such as Jira via MCP.

---

## Development Flow When MC Is Present

The agreed baseline is:

1. A story exists in planning and is eligible to be worked.
2. James assigns the story to Naomi via MC CLI or equivalent integration path.
3. Runtime receives that assignment/start intent and creates runtime execution state.
4. Naomi explicitly takes up the work.
5. Naomi loads:
   - the story,
   - parent context such as epic when available,
   - repository context.
6. Naomi updates `main`, creates a branch, plans the work, and records tasks through the planning integration.
7. Naomi executes tasks sequentially.
8. Blockers escalate to James.
9. After implementation tasks are complete, Naomi moves the story to code review.
10. Amos performs code review.
11. Review loops back to Naomi when needed.
12. Review loop limit is 3; on the 3rd return the work escalates.
13. Amos performs verify after review passes.
14. Verify loops back when needed.
15. Verify loop limit is 2 failures; on the 2nd failure the work escalates.
16. Terminal successful outcome becomes `Done`.

---

## What MC Must Not Own

Even when MC is deeply integrated, it must not become the hidden runtime core.

MC must not own:
- request routing,
- reply publication state,
- callback delivery truth,
- watchdog recovery semantics,
- stale-run detection,
- runtime idempotency,
- handoff acceptance semantics.

Those stay in the runtime.

---

## Operator Value

When MC is present, it is valuable because it gives one place to see:
- planning state,
- assignment state,
- backlog / sprint context,
- whether a development flow was started,
- what stage a story is in,
- and runtime/control-plane visibility for agent work.

That makes MC a strong first integration.
It does not make MC the foundation under the runtime.
