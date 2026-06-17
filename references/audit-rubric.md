# Audit Rubric

Score each category from 0 to its maximum. Cite evidence for every high or low score.

## 1. Goal and Scope Clarity - 15 points

- 0-5: Goal is vague or drifting.
- 6-10: Goal is understandable but lacks explicit acceptance criteria.
- 11-15: Goal, non-goals, acceptance criteria, and stop conditions are explicit.

Look for: task card, plan, user constraints, final verdict, scoped implementation notes.

## 2. Task Decomposition and Ownership - 15 points

- 0-5: Single blob of work with no ownership boundaries.
- 6-10: Some files or modules identified, but shared files are not controlled.
- 11-15: Owned paths, forbidden paths, shared locks, dependencies, and done criteria are explicit.

Look for: worktree plan, owned paths, allowlist, forbidden paths, branch/worktree split.

## 3. Codex Capability Utilization - 15 points

- 0-5: Uses Codex as a basic chat/code editor only.
- 6-10: Uses some tools such as shell, git, tests, or web search.
- 11-15: Appropriately uses subagents, CodeGraph, Browser, GitHub, Cloud, plugins, or noninteractive CLI where they materially help.

Do not require every tool. Reward the right tool for the task.

## 4. Context and Memory Management - 10 points

- 0-3: Context is implicit or lost across turns.
- 4-7: Some summaries/checkpoints exist.
- 8-10: AGENTS.md, build reports, task cards, resume checkpoints, or durable reports make the run resumable.

Look for: repo rules, build reports, checkpoint summaries, thread handoff notes.

## 5. Risk Isolation and Git Hygiene - 15 points

- 0-5: Dirty worktree, unclear branch, generated files or secrets risk.
- 6-10: Basic Git hygiene but incomplete isolation.
- 11-15: Dedicated branch/worktree, clean scope, no forbidden paths, no accidental generated/binary/secret files.

Look for: `git status`, changed files, branch, PR, allowlist, generated file handling.

## 6. Verification and Audit Coverage - 15 points

- 0-5: No meaningful validation.
- 6-10: Targeted tests or manual checks only.
- 11-15: Targeted tests, full tests or CI, diff audits, state/security checks, and final reviewer evidence.

Look for: test command names, pass/fail status, CI checks, state audit, diff check, PR review.

## 7. Reporting and Handoff Quality - 10 points

- 0-3: No final report or unclear outcome.
- 4-7: Summary exists but lacks evidence or next steps.
- 8-10: Report includes changed files, validation, risks, limitations, PR/commit state, and next action.

Look for: final answer, PR body, build report, human next step.

## 8. Upgrade Leverage - 5 points

- 0-1: No useful next-step recommendations.
- 2-3: Generic recommendations.
- 4-5: Specific paste-ready prompts or process upgrades tied to observed gaps.

## Verdict Bands

- 90-100: Exemplary Codex-native execution.
- 75-89: Strong execution with clear upgrade opportunities.
- 60-74: Useful but under-leveraged Codex run.
- 40-59: Mostly single-thread chat execution with weak auditability.
- 0-39: Risky, unclear, or not meaningfully auditable.

## Common Deductions

- In-progress run: cap final-readiness claims; do not issue final approval.
- Missing thread/repo evidence: mark unknowns and deduct from reporting/context, not necessarily implementation.
- No validation: major deduction even if implementation looks plausible.
- Parallelism not useful: do not deduct for missing subagents when the task is small or tightly coupled.
- Tool unavailable but documented fallback used: small or no deduction if the fallback is appropriate.

