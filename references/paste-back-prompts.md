# Paste-Back Prompts

Use these prompts when returning an actionable next message for the original Codex thread, a worker thread, a reviewer thread, or a finalizer thread.

For goal-mode work, start with `references/goal-mode-audit-prompts.md`. The Goal Contract is the source of truth; Task Cards, worker prompts, reviewer prompts, and finalizer prompts should inherit its verification, constraints, boundaries, iteration policy, completion conditions, pause conditions, polling audit, human intervention triggers, and final report format.

## Goal Mode Contract First

```text
Use $codex-efficiency-auditor as a Goal Compiler and Supervisor.

Before planning implementation, convert this request into a bounded /goal contract or audit the existing goal contract.

The contract must include:
- /goal outcome
- verification
- constraints
- boundaries
- iteration policy
- completion conditions
- pause conditions
- polling audit
- human intervention triggers
- final report format

After the contract is clear, decide whether execution should be single-threaded, Task Card based, or split across agents/worktrees.

Do not implement until the contract is concrete enough to supervise.
```

## Preflight Split Check

```text
Before implementing, decide whether this task should be single-threaded or split across multiple Codex agents/worktrees.

Evaluate:
- authorized /goal contract
- goal clarity
- affected modules
- shared files
- validation commands
- conflict risk
- expected coordination cost

If it should be split, output Task Cards for each worker.
If it should stay single-threaded, explain why and provide the single-thread execution plan.
Do not edit files yet.
```

## Worker Guardrail

```text
Execute only this Task Card and its authorized /goal contract.

Rules:
- Treat the Goal Contract as the source of truth.
- Modify only owned paths.
- Do not modify forbidden paths or shared locks unless explicitly assigned.
- Run the listed validation commands.
- Stop and report if the task requires expanding scope, credentials, payments, production data, destructive operations, public release, external account changes, or other pause-condition work.

End with:
- goal state machine stage
- files changed
- commands run
- tests passed/failed
- git status
- remaining risks
```

## Mid-Run Drift Check

```text
Pause implementation and perform a scope drift check.

Report:
- authorized /goal objective
- current objective being attempted
- files changed so far
- whether any changes are outside owned paths
- validation already run
- risks introduced
- whether to continue, narrow scope, or stop for human review

Do not add new feature work during this check.
```

## Read-Only Reviewer

```text
Act as a read-only reviewer for this branch/worktree.
Do not modify files.

Check:
- correctness
- regression risk
- missing tests
- unsafe broad changes
- generated files or secrets
- Git hygiene

Return blocking issues first, with file paths and evidence.
If no blocking issues are found, say so and list residual risks.
```

## Efficiency Auditor

```text
Use $codex-efficiency-auditor to audit this Codex run.

Context:
- thread/session id:
- repo path:
- branch/worktree:
- PR URL:
- original objective:

Focus:
- Did the run start from a concrete /goal contract?
- Did it stay inside verification, constraints, boundaries, iteration policy, completion conditions, and pause conditions?
- Was the run scoped and isolated?
- Did it use the right Codex capabilities?
- Was validation deep enough?
- Is the final report handoff-ready?
- What paste-back prompt should improve the original run?
```

## Finalizer

```text
Act as the finalizer for these Codex worker outputs.

Do not expand feature scope.
Use the authorized /goal contract as the source of truth.

Tasks:
1. Compare worker reports and changed files against the Goal Contract.
2. Identify conflicts, shared-lock changes, generated files, and pause-condition triggers.
3. Integrate in dependency order.
4. Run targeted validation after each integration step.
5. Run final validation.
6. Prepare a final closure report or PR description.

Output:
- final state machine stage
- integrated branches/worktrees
- final changed files
- validation results
- unresolved risks
- READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```

## CodeGraph Initialization Suggestion

```text
This repository would benefit from CodeGraph for structural navigation.

Please check whether `.codegraph/` exists.
If it does not exist, ask before running `codegraph init -i`.
After initialization, use CodeGraph for symbol, caller/callee, and impact questions before grep.
```
