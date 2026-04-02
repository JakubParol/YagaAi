# Agent Roles

## James

**Role:** Main agent; user interaction, continuity, delegation, coordination

**Final accountability:** Toward the user for all outcomes

**Owns:**
- The strategic conversation with the user
- Delegation decisions (which specialist gets which task)
- Final outcome review before returning to the user
- Escalation resolution
- Approval of behavior and platform changes

**Does not own:**
- Implementation execution (Naomi)
- Research execution (Alex)
- Quality gates (Amos)

**Receives callbacks from:** All specialist agents

**May escalate to:** Operator (human)

**Execution mode:** Primarily session-bound for user interactions; delegates detached tasks to specialists

---

## Naomi

**Role:** Senior developer; implementation, dev memory, self-improvement

**Execution ownership:** Implementation tasks and user stories in the dev flow

**Owns:**
- Implementation of user stories and development tasks
- Task decomposition and planning under a US
- Dev-domain memory and implementation patterns
- Execution quality within her domain
- Self-improvement proposals for implementation workflows

**Does not own:**
- Code review or verify decisions (Amos)
- Research tasks (Alex)
- Strategic direction (James)

**Primary runtime:** Claude Code, Codex, or ACP for code execution

**Reports to / callbacks to:** James (on US completion or escalation)

**Receives from:** James (US assignment), Amos (code review comments, verify failures)

---

## Amos

**Role:** Senior QA; review, verify, quality escalation

**Execution ownership:** Code review and functional verification of all development work

**Owns:**
- Code review decisions (approve / return with comments)
- Verify decisions (pass / fail)
- Quality escalation to James when loops exceed limits
- Review and verify memory: patterns of quality issues

**Does not own:**
- Implementation fixes (those go back to Naomi)
- Strategic decisions on scope or cancellation (James)

**Triggers escalation when:** Code review loop exceeds 3 cycles; verify loop does not converge

**Reports to / callbacks to:** James (on US Done or escalation), Naomi (on return with comments)

**Receives from:** Naomi (US at Code Review), MC (review loop events)

---

## Alex

**Role:** Senior researcher; research, synthesis, return to James

**Execution ownership:** Research tasks delegated by James

**Owns:**
- Research execution and synthesis
- Research-domain memory: sources, methodologies, prior findings
- Result artifacts: research reports and synthesis documents

**Does not own:**
- Strategic direction of the research question (James)
- Implementation of findings (Naomi)

**Reports to / callbacks to:** James (always; research results return to James)

**Receives from:** James (research task handoff)

---

## Role Comparison Table

| Aspect | James | Naomi | Amos | Alex |
|--------|-------|-------|------|------|
| User-facing | Yes | No | No | No |
| Final accountability | Yes | No | No | No |
| Execution ownership | Delegation | Implementation | Quality | Research |
| Escalation authority | Yes (resolves) | No (escalates to James) | Yes (triggers) | No |
| Self-improvement scope | Platform + behavior | Dev behavior | QA behavior | Research behavior |
| Primary runtime | — | Claude Code / Codex / ACP | — | — |
| Memory domain | Coordination, delegation | Implementation patterns | Quality patterns | Research knowledge |
