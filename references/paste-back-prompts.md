# Paste-Back Prompts

Use these prompts when returning an actionable next message for the original Codex thread, a worker thread, a reviewer thread, or a finalizer thread.

## Preflight Split Check

```text
Before implementing, decide whether this task should be single-threaded or split across multiple Codex agents/worktrees.

Evaluate:
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
Execute only this Task Card.

Rules:
- Modify only owned paths.
- Do not modify forbidden paths or shared locks unless explicitly assigned.
- Run the listed validation commands.
- Stop and report if the task requires expanding scope.

End with:
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
- current objective
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

Tasks:
1. Compare worker reports and changed files.
2. Identify conflicts, shared-lock changes, and generated files.
3. Integrate in dependency order.
4. Run targeted validation after each integration step.
5. Run final validation.
6. Prepare a final report or PR description.

Output:
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

