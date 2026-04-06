# 12 — Governance and v1 Boundaries

## Human Control Points

A human must have explicit control over:

| Action | When required |
|--------|--------------|
| Approving published changes | Before any agent behavior change goes live |
| Rolling back changes | Any time a deployed change needs reverting |
| Overriding policy | Operator-level policy exceptions |
| Incident review | Post-failure analysis and root cause |
| Promoting shared facts | Before a proposed fact enters the shared-facts layer |
| Approving platform-level changes | Runtime policy, topology rules, memory governance |
| Approving controlled topology exceptions | Before any exception to the channel session routing baseline is allowed |

These control points are not optional.

## Self-Improvement Loop

Self-improvement matters, but at v1 it does not mean autonomous self-rewriting.

### What agents may do without review
- update local working notes
- propose improvement candidates
- tag their own episodic memory with lessons-learned markers

### What requires review

| Change type | Review required? | Approver |
|-------------|-----------------|----------|
| Local working notes | No | — |
| Episodic memory updates | Justified; logged | — |
| Semantic memory promotion / correction | Yes | James / operator |
| Behavior changes (prompts, procedures, routing) | Yes | James / operator |
| Skill library changes | Yes | James / operator |
| Platform changes (runtime policy, contracts, topology) | Yes | operator |

## Controlled Topology Exceptions

The channel session routing model (see [04-channel-sessions-and-main-owner-routing.md](04-channel-sessions-and-main-owner-routing.md)) is the default.
Any deviation must be explicit, bounded, and approved.

### Approved-exception catalog

This document is the home for the approved-exception catalog.
Each exception should record:
- exception name
- reason
- allowed surfaces/agents
- duration / scope
- approval owner
- rollback rule

No ad hoc per-feature routing exceptions are allowed outside this catalog.

Current v1 catalog state: no topology exceptions are approved by default.

## v1 Scope

v1 is internal-first.

### What v1 supports
- 4 agents: James, Naomi, Amos, Alex
- user-originated durable requests with explicit routing/publication state
- 3 main flow types: research, development, QA
- an optional planning/control-plane integration for development workflow (Mission Control first; others later)
- per-agent memory with layered model
- detached task execution with callbacks
- explicit reply publication and recovery semantics
- full event trail with correlation and causation IDs
- replay and debug path for failed runs

### What v1 explicitly does not try to solve
- broad onboarding or multi-tenancy
- agent marketplaces or pluggable agent registry
- product-grade SLA guarantees beyond internal use
- a full declarative workflow DSL
- autonomous self-modifying production loop
- generic request workflow engine beyond what the runtime needs

## v1 Success Criteria

The system is successful at v1 if:
1. handoffs are predictable and visible end to end
2. for each task, owner, status, and callback target are unambiguous
3. for each durable request, reply target and publication state are unambiguous
4. an operator can replay a flow and understand what happened without reading transcripts
5. per-agent memory improves future work without becoming an execution log
6. execution and publication failures can be retried or escalated safely

## v1 Contract-Style Edge Case Tests

The system should pass these tests before v1 is considered stable:

| Test | Description |
|------|-------------|
| Duplicate inbound normalized once | Same inbound request normalized twice; no duplicate request or downstream work |
| Duplicate event | Same event delivered twice; outcome remains idempotent |
| Lost callback | Callback not received; task correctly blocks / escalates |
| Worker crash mid-task | Execution terminates; task reassigned or retried; no orphaned state |
| Review reassignment | Amos → Naomi → Amos loop preserves correct state |
| Stale ownership conflict | Prior owner gone; reassignment does not corrupt state |
| Retry after partial artifact | Partial artifact produced; retry path remains safe |
| Replay after failure | Failed run replayed; request/task/publication timeline reconstructed |
| Verify loop escalation | Verify fails twice; escalation emitted correctly |
| Review loop at limit | 3rd code-review return triggers escalation rule |
| Session-bound timeout | Session-bound task exceeds time; logged with no orphaned state |
| Rejected handoff | Rejection reason preserved; retry/escalation path remains valid |
| Transition rejected by MC | MC rejects invalid transition; state unchanged |
| Publication failed after specialist success | Work complete, reply unpublished; request remains open and recoverable |
| Reply-target mutation audit | Reply target changes are explicitly recorded and explainable |
| Cross-surface continuation | New surface message creates new request unless explicitly merged/linked |
| Fallback authorization | Fallback path requires the defined approval rule |
| Callback arrives after reassignment | Late callback reconciled without silently restoring prior ownership |
| Publish succeeds after retry ambiguity | Ambiguous publish resolves without duplicate human-visible reply |
| Duplicate publish ack | Duplicate publish result does not corrupt publication state |
| Improvement regression | Behavior change deployed; baseline test fails; auto-rollback triggered |

## MVP Success Metrics

| Metric | What it measures |
|--------|------------------|
| Callback success rate | Fraction of detached tasks that deliver a callback without manual intervention |
| Publication success rate | Fraction of durable requests whose intended reply publishes without manual intervention |
| Handoff acceptance rate | Fraction of handoffs that reach accepted without retry or escalation |
| Mean time to debug a failed run | How quickly an operator can identify the failure point |
| Duplicate-safe processing rate | Fraction of duplicate events safely deduplicated |
| Share of tasks requiring manual recovery | Fraction of tasks needing manual intervention |
| Share of requests requiring manual publication recovery | Fraction of durable requests needing manual publish/fallback intervention |
