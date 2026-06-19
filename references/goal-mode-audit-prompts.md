# Goal Mode Audit Prompts

Use these prompts when a goal-mode run needs a paste-back message for the main thread, a supervisor thread, a reviewer, or a finalizer.

## Goal Mode Start

```text
Use $codex-efficiency-auditor as a Goal Compiler.

Turn this request into a bounded Codex /goal contract.

Requirements:
- Keep the executable command prefix as /goal.
- Put the recommended Chinese copy-ready goal first.
- Include verification, constraints, boundaries, iteration policy, completion conditions, pause conditions, polling audit, human intervention triggers, and final report format.
- Choose conservative defaults for low-risk unknowns.
- Ask only if a decision changes cost, risk, ownership, or product direction.
- Use a discovery-first goal when the domain or project rules are not yet clear.
- Do not implement the goal yet.

Request:
<paste user request>
```

## Preflight Goal Audit

```text
Use $codex-efficiency-auditor to perform a read-only preflight audit for this authorized goal.
Load references/read-only-audit-guard.md.

Do not edit files, stage changes, commit, push, publish, deploy, delete, reset, or continue implementation.

Check:
- Is the /goal outcome concrete and verifiable?
- Are verification commands, evidence, or discovery steps explicit?
- Are constraints, allowed paths, forbidden paths, and shared locks clear?
- Is the iteration policy bounded?
- Does this goal need a Task State Pack for durable state, recovery, or handoff?
- If metric-driven, does it meet Experiment Lane entry criteria: metric, direction, baseline, gates, boundaries, rollback, and human gates?
- Are completion and pause conditions strong enough?
- Is polling audit scoped to read-only supervision?
- Are human intervention triggers explicit?
- Are Human Gates needed for push, publish, deploy, destructive work, account changes, credentials, paid services, or outbound comments?
- Is a Done Gate or Evidence Bundle needed before completion?
- Should this stay single-threaded, use Task Cards, or split into worktrees/agents?

Output:
- State machine stage
- Audit mutation status
- Git evidence
- Contract gaps
- Risk level
- Recommended Task Card or split decision
- Task State Pack need and proposed path
- Experiment Lane suitability: EXPERIMENT_LANE_READY / NEEDS_FIX / NOT_SUITABLE / NEEDS_HUMAN_DECISION
- Required Human Gates
- Done Gate and Evidence Bundle needs
- Validation commands to discover or run
- Whether execution may begin
- Next copy-ready prompt
```

## Periodic Goal Audit

```text
Use $codex-efficiency-auditor as a goal-mode supervisor.
Load references/read-only-audit-guard.md.

Perform a read-only periodic audit of the current run against the authorized goal.

Do not implement new work, modify files, or expand scope.

Report:
- Current state machine stage
- Audit mutation status
- Git evidence
- UI file card provenance, if file cards appear
- Whether the run remains within the authorized goal
- Recent progress and evidence
- Task State Pack path, status, iteration, stale_count, and last evidence, if present
- directions_tried summary and whether the next action is meaningfully different
- Metric/gate status, if the run is in Experiment Lane
- Files changed so far
- Validation already run
- Missing validation or weak evidence
- Scope drift or forbidden-path risk
- Blockers and repeated failures
- Stall/Pivot status: fresh progress / stale activity / repeated failure / pivot required
- Recovery/Stale Work status: CONTINUE / STALE_PROGRESS / REPEATED_FAILURE / RECOVERY_NEEDED / CONTEXT_OVERFLOW_RISK / SCOPE_DRIFT / BLOCKED
- Human Gate needs
- Done Gate readiness
- Whether human intervention is required
- Verdict: CONTINUE / NEEDS_HUMAN_DECISION / READY_FOR_FINAL_AUDIT / BLOCKED
- Next copy-ready prompt for the main thread
```

## Scope Drift Stop

```text
Pause implementation and perform a goal scope drift stop.
Load references/read-only-audit-guard.md.

Do not edit files.

Compare the current work against the authorized /goal contract.

Report:
- Audit mutation status
- Git evidence
- Original authorized outcome
- Current work being attempted
- Task State Pack status, if any
- stale_count and repeated failure signature, if any
- Changed files and paths
- Any work outside boundaries, constraints, or shared locks
- Whether validation still matches the goal
- The smallest safe scope to continue
- Whether the user must approve expansion

If drift is present, output only a corrective paste-back prompt that narrows the run back to the authorized goal or asks the user for a decision.
```

## Human Decision Required

```text
Stop autonomous progress and request a human decision.

Reason:
<credentials | payments | production data | destructive operation | public release | external account change | legal/medical/financial judgment | copyright | ownership unclear | scope expansion | validation unavailable | repeated blocker>

Report:
- Current state machine stage
- What was attempted
- Evidence gathered
- Why this exceeds autonomous authority
- Required Human Gate token, if applicable
- Decision options with the recommended safe default
- What Codex can continue doing after the decision
```

## Final Version Closure

```text
Use $codex-efficiency-auditor to perform final version closure for this goal-mode run.
Load references/read-only-audit-guard.md, references/goal-mode-done-gate.md, and references/goal-mode-evidence-bundle.md.

Do not modify files, expand feature scope, or continue implementation.

Report:
- Final state machine stage
- Audit mutation status
- Git evidence
- UI file card provenance, if file cards appear
- Authorized /goal summary
- Completion evidence
- Files changed
- Commands run and results
- Done Gate verdict
- Evidence Bundle Index
- Validation gaps
- Risk review: constraints, boundaries, forbidden paths, generated files, external systems
- Human Gate tokens and unresolved gates
- Recovery/Stale Work status, if relevant
- Codex capability utilization: subagents, worktrees, CodeGraph, Browser, GitHub/PR, automation, memory
- Final verdict: VERSION_CLOSED / READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
- Next copy-ready prompt, if any
```
