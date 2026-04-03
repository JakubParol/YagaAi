# 15 — Internal Prompt Architecture

## Status
Draft HLD for Yaga’s internal prompt architecture.

## Purpose
Define how Yaga should shape agent behavior internally:
- what belongs in runtime-owned prompts,
- what belongs in editable files,
- what belongs in policy/tool/runtime enforcement instead of prompt text,
- how memory should enter the model,
- how skills/playbooks should be loaded,
- and how to keep the whole thing compact, inspectable, and operationally strong.

This document is based on:
- OpenClaw prompt/runtime patterns,
- Hermes prompt assembly patterns,
- and the target Yaga design direction.

---

## 1. Core Principle

Yaga should not rely on “one giant hidden system prompt.”

The right model is a **hybrid control stack**:

1. **runtime enforcement**
   - tool availability
   - approvals
   - sandboxing
   - session visibility
   - routing constraints
   - execution boundaries

2. **runtime-owned prompt layers**
   - stable global behavior rules
   - task/workflow posture
   - memory discipline
   - tool discipline
   - delegation discipline

3. **editable agent/workspace files**
   - persona
   - user model
   - local operating notes
   - long-term memory source files

4. **tool schemas / model-native tool calling**
   - shape what can be called
   - shape argument structure
   - reduce ambiguity

5. **session mechanics**
   - compaction
   - memory flush
   - retrieval injection
   - child-session prompt minimization

6. **on-demand skills/playbooks**
   - load richer procedures only when needed

This is the right center of gravity.

---

## 2. Non-Negotiable Rule

> **Prompt text is for behavior shaping. Runtime/policy is for enforcement.**

This is one of the most important design rules we should steal from OpenClaw.

### Prompt should handle things like:
- posture
- style
- workflow discipline
- memory discipline
- when to read files
- when to load a skill/playbook
- how to delegate
- how to summarize
- how to reason about operator expectations

### Runtime/policy should handle things like:
- whether a tool exists
- whether a tool call is allowed
- whether elevated execution is allowed
- sandbox boundaries
- approval requirements
- session visibility
- binding/routing constraints
- data access boundaries

If a rule truly matters for safety or correctness, it should not depend only on prompt obedience.

---

## 3. The Best Synthesis from OpenClaw and Hermes

## From OpenClaw, we should copy:
- runtime-owned system prompt
- strict separation of prompt guidance vs hard runtime policy
- small injected bootstrap files
- on-demand skills loading
- prompt modes (`full`, `minimal`, etc.)
- memory flush before compaction
- keeping long-tail memory out of the always-on prompt

## From Hermes, we should copy:
- clear prompt assembly layers
- **cached stable prompt** vs **ephemeral turn-time additions**
- better distinction between identity substrate and per-turn overlays
- compaction-aware prompt discipline
- procedural learning via reusable authored skills/playbooks

## Yaga synthesis

Yaga should combine:
- **OpenClaw’s runtime governance**
with
- **Hermes’ prompt layering discipline**

That is likely the strongest prompt architecture available from the two systems.

---

## 4. Recommended Prompt Stack

Yaga should have at least three prompt modes.

## 4.1 Full prompt
Used for:
- main owner sessions
- durable reasoning sessions
- agent sessions that need full operating context

Includes:
- global runtime system block
- agent identity/persona block
- user block
- workspace/ops block
- selected memory context
- selected project/runtime context
- skill index
- current turn context

## 4.2 Minimal/subagent prompt
Used for:
- bounded workers
- isolated execution runs
- specialized child sessions

Includes only:
- minimal runtime rules
- exact task contract
- tool/sandbox context
- narrow relevant project context
- no unnecessary long-lived identity baggage

This prevents prompt bloat and accidental inheritance of irrelevant instructions.

## 4.3 Execution-only prompt
Optional but likely useful.
Used for:
- deterministic bounded task execution
- pure implementation/analysis workers
- repair/reindex/reconciliation runs

This mode should be more operational and less conversational.

---

## 5. Cached vs Ephemeral Prompt Layers

This is the strongest single structural idea to steal from Hermes.

## 5.1 Cached stable layers
These should stay stable across many turns unless something important changes.

Recommended stable layers:
1. runtime global behavior block
2. agent identity / role block
3. user model block
4. workspace operating rules block
5. stable memory snapshot pointers or compact memory summary
6. skill index / capability map
7. platform/runtime metadata

## 5.2 Ephemeral layers
These should be computed per turn.

Recommended ephemeral layers:
- current task/request context
- current retrieval results
- current project/repo snippets
- current operator/system event
- current tool result context
- current follow-up deltas

### Why this matters
This gives:
- lower token churn
- better cacheability
- more predictable behavior
- cleaner separation between identity and current work
- easier introspection and debugging

This should be a first-class Yaga design principle.

---

## 6. What Should Live in Editable Files

Editable files are useful because they let the user and agent shape behavior without changing runtime code.

Recommended editable file categories:

## 6.1 Identity / persona file
Equivalent to `SOUL.md`.

Purpose:
- tone
- vibe
- personality
- posture
- what kind of assistant this is

Should influence style and stance, not tool permission.

## 6.2 User model file
Equivalent to `USER.md`.

Purpose:
- who the user is
- preferences
- communication style
- important standing context
- topics to prioritize/avoid

## 6.3 Workspace operating file
Equivalent to `AGENTS.md`.

Purpose:
- local rules
- session-start expectations
- documentation priorities
- delegation conventions
- memory conventions
- project-specific behavior norms

## 6.4 Local notes / environment file
Equivalent to `TOOLS.md`.

Purpose:
- local environment notes
- aliases
- device names
- paths
- infra reminders

Must not control actual permission.

## 6.5 Long-term memory files
Equivalent to:
- `MEMORY.md`
- daily notes
- maybe later structured memory records as first-class data

These are source material for retrieval, not giant permanent prompt payloads.

---

## 7. What Should Not Live in Editable Files

Do **not** let editable files control:
- hard tool availability
- sandbox escapes
- approval bypass
- cross-session visibility
- routing ownership rules that must stay invariant
- destructive execution permissions

Those belong in runtime policy.

The user should be able to shape behavior. The user should not accidentally turn prompt prose into fake enforcement.

---

## 8. Memory in the Prompt

## 8.1 Long-tail memory should not be injected wholesale
This is another excellent lesson from OpenClaw.

Do not stuff all memory into the base system prompt.

Instead:
- keep a compact stable memory layer only if truly useful,
- retrieve the rest on demand,
- use memory search tools/services,
- inject only relevant recalled material.

## 8.2 Memory flush before compaction
This is worth stealing nearly directly.

Before context compaction or aggressive summarization, the runtime should explicitly remind the agent to:
- save important decisions
- save durable preferences
- save lessons worth keeping
- save unresolved items worth continuing later

This creates a practical self-curation loop.

## 8.3 Typed memory direction
Yaga should evolve toward typed memory records:
- fact
- preference
- decision
- lesson
- todo/reminder
- open_question
- project_note

Even if the user-visible source remains Markdown or other editable files, runtime retrieval should trend toward structured memory semantics.

---

## 9. Tool Calling: Prompt vs Schema vs Policy

## 9.1 Tool calling is not purely prompt-driven
Tool usage is shaped by three things at once:
- prompt guidance
- tool schemas
- runtime policy/enforcement

Sometimes also by:
- model-native tool calling behavior
- runtime wrappers and gating rules

## 9.2 Yaga stance

### Prompt should teach:
- when to use a tool
- when not to use a tool
- when to read docs first
- when to delegate
- when to ask vs act
- how to avoid pointless tool spam

### Tool schemas should enforce:
- argument shape
- required fields
- safe narrow inputs
- explicit action selection

### Runtime should enforce:
- availability
- approvals
- execution limits
- elevated restrictions
- sandbox rules
- routing constraints

This layered model is much stronger than asking the model to “please be careful.”

---

## 10. Skills and Playbooks

This is another pattern worth stealing heavily.

## 10.1 Skill index, not giant preloaded manuals
The base prompt should contain a **capability/skill index**, not full procedures.

Per skill/playbook, the base layer should expose only:
- name
- short description
- when it applies
- where to load it from

Then the agent loads the richer playbook only on demand.

## 10.2 Why this is good
This keeps prompts:
- smaller
- cleaner
- cheaper
- more relevant
- easier to evolve

## 10.3 Yaga direction
Yaga should support:
- skill index in the base prompt
- on-demand loading of detailed skill/playbook content
- possible gating by OS / tool availability / repo context

This is better than one giant hidden prompt containing every workflow forever.

---

## 11. Delegation Behavior

Yaga is multi-agent by design, so delegation behavior must be shaped explicitly.

The prompt should teach:
- owner vs worker distinction
- when to delegate
- when to stay in the owner session
- how to brief another agent compactly
- how to define goal / context / constraints / expected output
- how not to block the main conversation unnecessarily

The runtime should enforce:
- which sessions are visible
- which sessions can be messaged
- which agent owns which workspace
- whether a subagent is isolated or durable

Again:
- prompt for behavior
- runtime for boundaries

---

## 12. Self-Improvement Loop

Yaga should have a self-improvement loop, but not as uncontrolled autonomous self-rewriting.

## 12.1 What prompt should do
Prompt should teach the agent to:
- notice repeated friction
- propose better procedures
- distill lessons
- save reusable patterns
- suggest playbook/skill changes

## 12.2 What runtime/process should do
Runtime/process should decide:
- where improvement candidates are stored
- who can approve them
- what becomes globally active
- what is versioned
- what is rolled back

## 12.3 Best design rule

> Agents may propose changes freely. They may not silently rewrite the platform’s operating constitution.

That is the right balance.

---

## 13. Prompt Introspection

Yaga should let operators understand what shaped a run.

At minimum, it should be possible to inspect:
- which prompt mode was used
- which stable layers were active
- which ephemeral layers were injected
- which editable files contributed
- which skills/playbooks were loaded
- which memory recalls were injected
- whether any layer was truncated

This is crucial for debugging and for trust.

Without this, prompt architecture becomes cargo cult magic.

---

## 14. Recommended Yaga Prompt Assembly

A good default full-session prompt assembly would look like this:

1. **Global runtime system block**
   - product-level rules
   - behavior discipline
   - memory/tool/delegation expectations

2. **Runtime policy summary block**
   - compact explanation of tool/sandbox/approval environment
   - advisory only; actual enforcement lives below prompt

3. **Agent identity block**
   - role
   - persona
   - default posture

4. **User block**
   - preferences
   - communication style
   - relevant profile

5. **Workspace ops block**
   - local project rules
   - delegation conventions
   - operational notes

6. **Skill index block**
   - names/descriptions only

7. **Stable context metadata**
   - date/time/runtime/platform/session info

8. **Ephemeral turn block**
   - current request
   - current task
   - current relevant retrievals
   - current memory recall
   - current tool outputs if needed

This is probably the cleanest Yaga v1 shape.

---

## 15. Anti-Patterns to Avoid

Do not copy these mistakes:

- one giant permanent hidden prompt with everything in it
- using prompt prose as fake security enforcement
- injecting all long-term memory by default
- stuffing all skill manuals into the base prompt
- making child sessions inherit full parent prompt baggage
- mixing persona, permissions, memory, and workflow state into one undifferentiated block
- making the operator unable to inspect what prompt layers were active

These are the easiest ways to make the system expensive, brittle, and mysterious.

---

## 16. Decision Summary

Yaga’s internal prompt architecture should be built around:
- **runtime enforcement for hard boundaries**
- **runtime-owned global system prompt for behavior discipline**
- **editable files for persona/user/ops context**
- **cached stable prompt layers vs ephemeral turn layers**
- **on-demand skill/playbook loading**
- **retrieved memory instead of giant always-on memory injection**
- **minimal prompt modes for child/subagent sessions**
- **prompt introspection for debugging and trust**

In short:

> **Teach behavior in prompts. Enforce boundaries in runtime. Keep memory and skills selective. Make the whole stack inspectable.**
