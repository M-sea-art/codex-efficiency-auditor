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

Do not edit files yet.

Check:
- Is the /goal outcome concrete and verifiable?
- Are verification commands, evidence, or discovery steps explicit?
- Are constraints, allowed paths, forbidden paths, and shared locks clear?
- Is the iteration policy bounded?
- Are completion and pause conditions strong enough?
- Is polling audit scoped to read-only supervision?
- Are human intervention triggers explicit?
- Should this stay single-threaded, use Task Cards, or split into worktrees/agents?

Output:
- State machine stage
- Contract gaps
- Risk level
- Recommended Task Card or split decision
- Validation commands to discover or run
- Whether execution may begin
- Next copy-ready prompt
```

## Periodic Goal Audit

```text
Use $codex-efficiency-auditor as a goal-mode supervisor.

Perform a read-only periodic audit of the current run against the authorized goal.

Do not implement new work and do not expand scope.

Report:
- Current state machine stage
- Whether the run remains within the authorized goal
- Recent progress and evidence
- Files changed so far
- Validation already run
- Missing validation or weak evidence
- Scope drift or forbidden-path risk
- Blockers and repeated failures
- Whether human intervention is required
- Verdict: CONTINUE / NEEDS_HUMAN_DECISION / READY_FOR_FINAL_AUDIT / BLOCKED
- Next copy-ready prompt for the main thread
```

## Scope Drift Stop

```text
Pause implementation and perform a goal scope drift stop.

Do not edit files.

Compare the current work against the authorized /goal contract.

Report:
- Original authorized outcome
- Current work being attempted
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
- Decision options with the recommended safe default
- What Codex can continue doing after the decision
```

## Final Version Closure

```text
Use $codex-efficiency-auditor to perform final version closure for this goal-mode run.

Do not expand feature scope.

Report:
- Final state machine stage
- Authorized /goal summary
- Completion evidence
- Files changed
- Commands run and results
- Validation gaps
- Risk review: constraints, boundaries, forbidden paths, generated files, external systems
- Codex capability utilization: subagents, worktrees, CodeGraph, Browser, GitHub/PR, automation, memory
- Final verdict: VERSION_CLOSED / READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
- Next copy-ready prompt, if any
```
