# 10 — Governance and v1 Boundaries

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

These control points are not optional. The system is not designed to eliminate human
judgment — it is designed to make human judgment cheaper and better-informed.

## Self-Improvement Loop

Self-improvement matters, but at the start it must not mean autonomous self-rewriting.

### What Agents May Do Without Review

- Update local working notes (working memory)
- Propose improvement candidates
- Tag their own episodic memory with lessons-learned markers

### What Requires Review

| Change type | Review required? | Approver |
|-------------|-----------------|----------|
| Local working notes | No | — |
| Memory updates (episodic, semantic) | Justified; logged | — |
| Behavior changes (prompts, procedures, routing) | Yes | James / operator |
| Skill library changes | Yes | James / operator |
| Platform changes (runtime policy, contracts, topology) | Yes | Operator |

### Improvement Candidate Format

An improvement candidate is a structured record containing:

| Field | Description |
|-------|-------------|
| `proposed_by` | Agent proposing the change |
| `target` | What is being changed: `working_note`, `episodic`, `semantic`, `procedural`, `behavior`, `platform` |
| `current_state` | The current prompt fragment, routing rule, or memory entry being replaced |
| `proposed_state` | The replacement |
| `justification` | Why this change is expected to improve outcomes |
| `evidence` | References to tasks or episodes that support the proposal |
| `baseline_test` | How to verify the change doesn't regress existing behavior |

### Reviewer and Approval Criteria

| Change target | Reviewer | Approval criterion |
|--------------|----------|--------------------|
| `working_note` | None required | Auto-approved |
| `episodic` / `semantic` | Agent self (logged) | Justification required |
| `procedural` / `behavior` | James | Evidence of improvement; baseline test passes |
| `platform` | Human operator | Full review; rollback plan required |

### Drift Detection

After any approved behavior change, the system must verify no regression occurred:
- Run the `baseline_test` defined in the candidate against the deployed change
- If baseline test fails after deployment: auto-rollback and `improvement.regression_detected` event
- Cumulative drift monitoring: if multiple improvements have been applied over time,
  James or the operator should periodically review the aggregate change to agent behavior

### Improvement Candidate Lifecycle

```
agent proposes candidate → candidate stored with justification
  → reviewer assigned based on target type
  → reviewed: approved / rejected / modified
  → if approved: change deployed with version tag
  → baseline_test run → if pass: confirmed; if fail: auto-rollback
  → audit trail retained regardless of outcome
```

The system stores an improvement candidate before any change is made. The change
does not go live until it clears review and passes baseline test.

## v1 Scope

v1 is internal-first.

### What v1 Supports

- 4 agents: James, Naomi, Amos, Alex
- 3 main flow types: research, development, QA
- The privileged development workflow in Mission Control
- Per-agent memory with layered model
- Detached task execution with callbacks
- Full event trail with correlation and causation IDs
- Replay and debug path for failed runs

### What v1 Explicitly Does Not Try to Solve

- Broad onboarding or multi-tenancy
- Agent marketplaces or pluggable agent registry
- Product-grade support or SLA guarantees beyond internal use
- Full capability parity with existing agent platforms
- An autonomous self-modifying production loop
- A full declarative workflow DSL (a simpler event/state contract is enough)
- General-purpose framework for any workload

The system should not try to win on feature breadth at the start. It should win operationally.

## Non-Goals

The following are permanent non-goals or post-v1 concerns:

- Universal chatbot capability
- Broad multi-tenant distribution
- Full enterprise BPM suite
- Autonomous topology rebuilding
- Replacing domain experts with a single general agent

## v1 Success Criteria

The system is successful at v1 if:

1. **Handoffs are predictable and visible end-to-end.** An operator can trace any
   handoff from dispatch to acceptance to completion.

2. **For each task, owner, status, and callback target are unambiguous.**
   No task exists in an ambiguous state for more than a defined recovery window.

3. **An operator can replay a flow and understand what happened** without reading
   session transcripts.

4. **Per-agent memory improves future work** without collapsing into an execution log
   or contaminating across agents.

5. **Execution failures can be retried or escalated safely.** No failure produces
   silent data loss or undetectable side effects.

## v1 Contract-Style Edge Case Tests

The system should pass these tests before v1 is considered stable:

| Test | Description |
|------|-------------|
| Duplicate event | Same event delivered twice; outcome is idempotent |
| Lost callback | Callback not received; task correctly moves to `Blocked` and notifies James |
| Worker crash mid-task | Execution terminates; task reassigned; no orphaned state |
| Review reassignment | Code review loop: Amos → Naomi → Amos; state transitions correct |
| Stale ownership conflict | Prior owner gone; James reassigns; no state corruption |
| Retry after partial artifact | Artifact partially produced; task retried; prior partial artifact handled |
| Replay after failure | Failed run replayed; event timeline reconstructed correctly |
| Verify loop escalation | Verify fails twice; `verify_loop.limit_reached` emitted; escalation to James |
| Review loop at limit | 3rd Code Review return triggers `review_loop.limit_reached`; not 4th |
| Session-bound timeout | Session-bound task exceeds time; event logged; no orphaned state |
| Concurrent US assignments | Naomi receives two US assignments; priority ordering respected |
| Rejected handoff | Naomi rejects assignment with reason; James receives rejection; retry or escalate |
| Transition rejected by MC | Agent emits intent event MC cannot allow; `transition.rejected` returned; state unchanged |
| Improvement regression | Behavior change deployed; baseline test fails; auto-rollback triggered |

## MVP Success Metrics

| Metric | What it measures |
|--------|----------------|
| Callback success rate | Fraction of detached tasks that deliver a callback without manual intervention |
| Handoff completion rate | Fraction of handoffs that reach accepted/done without retry or escalation |
| Mean time to debug a failed run | How quickly an operator can identify the failure point |
| Duplicate-safe processing rate | Fraction of duplicate events that are correctly deduplicated |
| Share of tasks requiring manual recovery | Fraction of tasks that need operator intervention outside defined escalation paths |
