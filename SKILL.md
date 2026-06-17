---
name: codex-efficiency-auditor
description: Audit Codex threads, projects, worktrees, pull requests, and agent runs for capability utilization, orchestration quality, risk isolation, validation coverage, and upgrade opportunities. Use when the user asks to evaluate whether a Codex conversation or project used Codex well, review a thread id, score a project workflow, improve multi-agent/worktree/cloud usage, create a final reviewer prompt, or turn an ordinary Codex run into a more efficient auditable execution pattern.
---

# Codex Efficiency Auditor

## Purpose

Assess whether a Codex run used the available Codex capability boundary well: planning, subagents, worktrees, CodeGraph, GitHub/PRs, Browser, Cloud, tests, audits, reports, and durable project memory.

Be an evaluator and upgrader, not a second implementer. Prefer read-only inspection unless the user explicitly asks to apply changes.

## Inputs

Accept any of these:

- Codex thread id
- Local project path
- GitHub PR or repository URL
- Worktree path
- Build report, final answer, or pasted execution transcript

If a thread id is provided and thread tools are available, read the thread directly. If a repo path is provided, inspect Git status, project rules, build/test scripts, recent commits, PR links, and reports. If only a transcript is provided, audit from the transcript and mark unknowns.

## Audit Workflow

1. **Orient**
   - Identify the object being audited: thread, repo, PR, worktree, or transcript.
   - Determine status: running, idle, completed, blocked, PR open, PR merged, or unknown.
   - Do not grade final readiness for an in-progress run; give a stage-gated interim score.

2. **Gather evidence**
   - For threads: read recent turns and older context until the goal, plan, implementation, validation, and final report are visible.
   - For repos: inspect `AGENTS.md`, Git branch/status, recent commits, changed files, CI/PR state, test commands, and build reports.
   - For codebases with CodeGraph available and initialized: use it for structural questions before grep.
   - For UI work: check whether Browser or visual validation was used.
   - For GitHub work: check branch, PR, checks, review comments, and diff scope.

3. **Score**
   - Use `references/audit-rubric.md`.
   - Score each category with evidence, not vibes.
   - Penalize missing evidence differently from failed evidence: "unknown" is a reporting gap, not always a technical failure.

4. **Classify**
   - `90-100`: exemplary Codex-native execution
   - `75-89`: strong execution with clear upgrade opportunities
   - `60-74`: useful but under-leveraged Codex run
   - `40-59`: mostly single-thread chat execution with weak auditability
   - `<40`: risky, unclear, or not meaningfully auditable

5. **Recommend upgrades**
   - Prefer concrete next prompts the user can paste into the audited thread.
   - Separate "must fix before merge" from "efficiency upgrade."
   - Recommend subagents only when tasks are independent enough to benefit.
   - Recommend worktrees when write scopes can be separated.
   - Recommend CodeGraph initialization when structural code navigation matters and the repo lacks `.codegraph/`.
   - For orchestration upgrades, use `references/task-card-template.md` and `references/multi-worktree-orchestration-template.md`.
   - For prompt handoff, use `references/paste-back-prompts.md`.

6. **Report**
   - Use `references/report-templates.md`.
   - Lead with verdict, score, and whether the run is still active.
   - Include evidence-backed strengths, gaps, and one paste-ready upgrade prompt.

## Standard Categories

Audit these eight categories:

1. Goal and scope clarity
2. Task decomposition and ownership
3. Codex capability utilization
4. Context and memory management
5. Risk isolation and Git hygiene
6. Verification and audit coverage
7. Reporting and handoff quality
8. Upgrade leverage

Use `scripts/score_audit.py` when useful to total a category score JSON and produce a verdict band.

## Stop Rules

Do not recommend more parallelism when:

- The requirement is still ambiguous.
- Multiple agents would edit the same shared files.
- The task is mostly architecture decision-making.
- Tests are absent or unreliable enough that failures cannot be attributed.
- The current run is in-progress and already past the point where interruption would add risk.

Do not mark a run `READY_FOR_HUMAN_REVIEW` unless final validation evidence is present or the user explicitly asked for an interim review.

## Templates

Load these references only when they fit the user's request:

- `references/task-card-template.md`: Use when creating or auditing worker task cards, owned paths, shared locks, done criteria, or validation commands.
- `references/multi-worktree-orchestration-template.md`: Use when deciding whether a task should become a multi-agent/multi-worktree workflow.
- `references/paste-back-prompts.md`: Use when producing prompts that should be pasted into an original thread, worker thread, reviewer thread, or finalizer thread.

## Paste-Ready Upgrade Prompt Pattern

When a run is missing a final audit, provide a prompt like:

```text
Please perform a read-only Codex efficiency final audit for this run.
Do not expand scope or continue feature work unless you find a blocker.

Report:
- Codex capability utilization score out of 100
- Task Card: goal, owned paths, forbidden paths, shared locks, done criteria, validation commands
- Final Git state: branch, commit, changed files, clean/dirty status, generated files
- Validation evidence: targeted tests, full tests, audits, CI/PR status
- Risk review: state ownership, runtime/generated files, forbidden paths, external data/source boundaries
- Missing Codex leverage: subagents, worktree, CodeGraph, Browser, GitHub/PR, Cloud
- Verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```
