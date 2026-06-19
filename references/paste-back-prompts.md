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

## Task State Pack Init

```text
Use $codex-efficiency-auditor and load references/task-state-pack-template.md plus references/stall-and-pivot-rules.md.

Create or audit a Task State Pack proposal for this authorized /goal.

Do not implement feature work yet.

Report:
- proposed state pack path
- required files
- task_spec summary
- progress.json initial state
- gates.json summary
- stale_count policy
- rollback readiness
- whether scripts/lint_task_state_pack.py should be run after files exist
- next copy-ready prompt
```

## Experiment Lane Preflight

```text
Use $codex-efficiency-auditor and load references/evo-style-experiment-lane.md.

Run a read-only Experiment Lane Preflight.

Do not install evo, modify hooks, create telemetry, or run optimization.

Report:
- objective
- metric and direction
- baseline evidence
- candidate directions
- required gates
- allowed paths / forbidden paths / shared locks
- human gates
- rollback
- missing criteria
- suitability: EXPERIMENT_LANE_READY / NEEDS_FIX / NOT_SUITABLE / NEEDS_HUMAN_DECISION
- next copy-ready prompt
```

## Ideator Brief

```text
Use $codex-efficiency-auditor and load references/ideator-verifier-loop.md.

Act as Ideator only. Do not edit files or run experiments.

Produce candidate directions for:
- failure_analysis
- literature_or_repo_scan
- frontier_extrapolation

For each candidate include:
- hypothesis
- based_on_evidence
- differentiation_from_existing
- expected_effect
- cost
- risk
- human_gate_needed

End with the one candidate recommended for verifier review.
```

## Verifier Audit

```text
Use $codex-efficiency-auditor and load references/ideator-verifier-loop.md plus references/read-only-audit-guard.md.

Act as Verifier only. Do not edit files, run implementation, or expand scope.

Audit the selected candidate for:
- scope and forbidden-path risk
- metric/gate completeness
- validation evidence
- false progress
- stale evidence or cache risk
- human gate needs

Return:
- Audit mutation status
- JSON-style verifier result with pass/warn/fail
- blocking findings
- whether implementation may begin
```

## Read-Only Audit Guard

```text
Use $codex-efficiency-auditor and load references/read-only-audit-guard.md.

Perform a read-only audit only. Do not modify files, stage changes, commit, push, publish, deploy, delete, reset, or continue implementation.

Collect and report:
- git status --short --branch
- git diff --name-status
- git diff --cached --name-status
- whether any displayed Codex UI file cards belong to the audited commit/diff or current working-tree changes
- Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN
- Validation evidence
- Residual risks
- Verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```

## Human Gate Check

```text
Use $codex-efficiency-auditor and load references/goal-mode-human-gates.md.

Stop before any push, publish, deploy, destructive action, external account change, credential use, paid service, or outbound public comment.

Report:
- Gate ID
- Blocked action
- Evidence the user must review
- Exact APPROVED:Gx token needed
- Exact REJECTED:Gx token option
- What read-only or local validation can continue while waiting
```

## Done Gate Check

```text
Use $codex-efficiency-auditor and load references/goal-mode-done-gate.md plus references/read-only-audit-guard.md.

Run a read-only Done Gate for the authorized /goal.

Report:
- Audit mutation status
- Contract audit
- Scope check
- Verification evidence
- Stop condition proof
- Pause scan
- Next-task check
- Verdict: DONE_GATE_PASS / READY_FOR_FINAL_AUDIT / NEEDS_FIX / NEEDS_HUMAN_DECISION / BLOCKED
```

## Evidence Bundle Request

```text
Use $codex-efficiency-auditor and load references/goal-mode-evidence-bundle.md.

Create an Evidence Bundle Index for this goal-mode run.

Include:
- goal contract source
- branch/worktree and changed files
- commands and results
- tests/CI/manual evidence
- screenshots or artifacts
- diff/security/privacy scans
- human gate tokens
- unverified claims
- known risks
- next copy-ready prompt
```

## Recovery Snapshot

```text
Use $codex-efficiency-auditor and load references/goal-mode-recovery-stale-work.md.

Create a Recovery Snapshot before continuing this goal.

Report:
- authorized /goal
- current state machine stage
- last known good evidence
- branch/worktree
- changed files
- commands already run
- last failure signature
- repeated failures
- missing context
- forbidden paths/shared locks
- next safe action
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
- evidence bundle entries, if finalizing
- human gate needs, if any
- git status
- remaining risks
```

## Mid-Run Drift Check

```text
Pause implementation and perform a scope drift check.
Load references/read-only-audit-guard.md if this check is meant to be read-only.

Report:
- authorized /goal objective
- current objective being attempted
- files changed so far
- whether any changes are outside owned paths
- validation already run
- risks introduced
- recovery/stale-work status
- whether to continue, narrow scope, or stop for human review

Do not add new feature work during this check.
```

## Read-Only Reviewer

```text
Act as a read-only reviewer for this branch/worktree.
Do not modify files.
Load references/read-only-audit-guard.md.

Check:
- correctness
- regression risk
- missing tests
- unsafe broad changes
- generated files or secrets
- Git hygiene

Return blocking issues first, with file paths and evidence.
If no blocking issues are found, say so and list residual risks.
Include Audit mutation status and Git evidence before the verdict.
```

## Efficiency Auditor

```text
Use $codex-efficiency-auditor to audit this Codex run.
If this is a final, commit, PR, or read-only audit, load references/read-only-audit-guard.md.

Context:
- thread/session id:
- repo path:
- branch/worktree:
- PR URL:
- original objective:

Focus:
- Did the run start from a concrete /goal contract?
- Did it stay inside verification, constraints, boundaries, iteration policy, completion conditions, and pause conditions?
- Did it stop at required Human Gates?
- Does it have a Done Gate verdict and Evidence Bundle?
- Is recovery/stale-work status clear for long or interrupted runs?
- Was the run scoped and isolated?
- Did it use the right Codex capabilities?
- Was validation deep enough?
- Is the final report handoff-ready?
- Did the audit itself avoid modifying files?
- What paste-back prompt should improve the original run?

For read-only audits, include:
- Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN
- Git evidence
- UI file card provenance, if file cards appear
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
- Done Gate verdict
- Evidence Bundle Index
- Human Gate tokens
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
