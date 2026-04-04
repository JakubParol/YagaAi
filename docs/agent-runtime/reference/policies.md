# Policies

A Policy is an automatic reaction to a Domain Event.

Expressed as: "Whenever [Domain Event], issue [Command]."

Policies are enforced by the runtime or Mission Control, not by individual agents making
ad-hoc decisions. They are first-class system concepts, not implementation details.

Every watchdog start, retry schedule, loop-limit escalation, and fallback invocation in
the system is a named Policy in this catalog.

## Policy Catalog

| Policy | Trigger Event | Command Issued | Owner | Notes |
|--------|---------------|----------------|-------|-------|
| `WatchAcceptanceTimeout` | `handoff.dispatched` | `StartAcceptanceWatchdog` | runtime | Watchdog fires `watchdog.fired` → `handoff.timeout` if not accepted within window |
| `EscalateOnHandoffTimeout` | `handoff.timeout` | `EscalateToStrategicOwner` | runtime | |
| `WatchOrphanedWork` | `task.accepted` | `StartOrphanWatchdog` | runtime | Watchdog fires `execution.timeout` if no progress within window |
| `EscalateOnOrphanTimeout` | `execution.timeout` (orphan) | `NotifyTaskOwner` → `EscalateToJames` | runtime | Two-stage: notify first, escalate if no response |
| `WatchPublicationTimeout` | `reply.publication_attempted` | `StartPublicationWatchdog` | runtime | Watchdog fires `watchdog.fired` if no terminal outcome within policy window |
| `RetryPublicationOnFailure` | `reply.publication_failed` | `RetryPublish` | runtime / strategic owner | Reuses same `publish_dedup_key` |
| `InvokeFallbackOnPublicationTimeout` | `watchdog.fired` (policy: `WatchPublicationTimeout`) | `InvokeReplyFallback` | strategic owner | Requires explicit fallback target |
| `RetryNormalizationOnAdapterFailure` | `request.normalization_attempted` (no ack within window) | `RetryNormalization` | surface adapter | Idempotent; same dedup identity |
| `ReturnToInProgressOnReviewComment` | `review_loop.incremented` | `ReturnTaskToOwner` | Mission Control | Carries review comments as artifact |
| `EscalateOnReviewLimitReached` | `review_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `EscalateOnVerifyLimitReached` | `verify_loop.limit_reached` | `EscalateToJames` | Mission Control | |
| `ContinueOnMemoryWriteFailure` | `memory.write_failed` | _(none — explicit non-interruption)_ | runtime | Domain Event is emitted and observable. Policy explicitly chooses not to issue a blocking Command. Task continues. |

## Reading the Catalog

- **Policy** — the name used in inline annotations throughout the operational flow docs.
- **Trigger Event** — the Domain Event that causes the Policy to fire.
- **Command Issued** — what the Policy tells the system to do next. `_(none)_` means the Policy explicitly chooses non-interruption; the Domain Event is still observable.
- **Owner** — which component is responsible for enforcing this Policy.
- **Notes** — additional constraints, two-stage behaviour, or escalation clauses.

Watchdog-based Policies follow the sequence:

```
[trigger event] → watchdog.started → watchdog.fired → [reaction Policy] → [command]
```

`watchdog.cancelled` is emitted if the condition resolves before the watchdog fires
(e.g., a handoff is accepted before the acceptance window closes).
