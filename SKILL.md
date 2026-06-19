---
name: codex-efficiency-auditor
description: "Codexcavator / Codex efficiency expert / Codex \u6316\u6398\u673a / Codex \u6548\u7387\u4e13\u5bb6 for auditing and upgrading Codex threads, projects, PRs, worktrees, agent runs, goal-mode workflows, acceptance gates, completion reports, Definition of Done, and one-time project capability scans. Use when the user says Codexcavator, Codex \u6316\u6398\u673a, \u6548\u7387\u5ba1\u8ba1, \u9a8c\u6536\u95e8\u7981, \u9632\u865a\u5047\u5b8c\u6210, completion report, \u5ba1\u8ba1\u5f53\u524d\u4f1a\u8bdd, \u8bc4\u6d4b\u8fd9\u4e2a\u9879\u76ee, Codex \u7528\u5f97\u597d\u4e0d\u597d, \u80fd\u529b\u8fb9\u754c, \u9879\u76ee\u63d2\u4ef6\u80fd\u529b\u5ba1\u8ba1, Codex \u80fd\u529b\u76d8\u70b9, \u63a8\u8350\u672c\u9879\u76ee\u53ef\u7528\u63d2\u4ef6, Audit my available Codex plugins and app capabilities, \u591a\u667a\u80fd\u4f53\u7f16\u6392, \u591a agent, worktree, \u76ee\u6807\u6a21\u5f0f, /goal, \u76ee\u6807\u5408\u540c, \u81ea\u52a8\u5316\u95ed\u73af, \u5468\u671f\u5ba1\u8ba1, \u6700\u7ec8\u5ba1\u8ba1, READY_FOR_HUMAN_REVIEW, NEEDS_FIX, or asks to convert an idea into a bounded Codex goal, supervise progress, detect scope drift or stale work, prevent unsupported completion claims, audit available Codex capabilities, and produce paste-back prompts or reports."
---

# Codexcavator / Codex Efficiency Auditor

## Purpose

Assess whether a Codex run used the available Codex capability boundary well: planning, subagents, worktrees, CodeGraph, GitHub/PRs, Browser, Cloud, tests, audits, reports, durable project memory, and goal-mode contracts.

Position the project as Codexcavator: an agent-run auditor. CI checks code; Codexcavator checks agent workflow.

Be an evaluator and upgrader, not a second implementer. Prefer read-only inspection unless the user explicitly asks to apply changes.

For any read-only review, final audit, commit audit, PR audit, goal-mode periodic audit, or Done Gate, load `references/read-only-audit-guard.md` and report whether the audit itself modified files.

For long-running, self-improving, multi-candidate, or repeated-failure goals, route through Task State Pack, Stall/Pivot, Experiment Lane, and Ideator/Verifier references before recommending more execution.

## Operating Modes

This skill has three layers:

1. **Goal Compiler**: turn a vague or complex request into a paste-ready `/goal` contract with outcome, verification, constraints, boundaries, iteration policy, completion conditions, pause conditions, polling audit, human intervention triggers, and final report format.
2. **Goal Supervisor**: after the user authorizes a goal, supervise the run with preflight audit, Task Cards, worktree or agent split decisions, periodic audit, drift stops, and final closure.
3. **Efficiency Auditor**: audit a running or completed thread, repo, worktree, PR, transcript, or final report for Codex capability utilization and upgrade opportunities.

Cross-cutting controls:

- **Task State Pack**: use durable state files for long tasks instead of relying on chat memory.
- **Stall/Pivot Rules**: stop repeated low-evidence retries and force structural pivots.
- **Experiment Lane**: allow metric-driven variants only when required gates protect correctness and scope.
- **Ideator/Verifier Loop**: separate proposal generation from implementation and read-only verification.
- **Project Supervisor Bridge**: coordinate with `$project-supervisor` for acceptance gates, completion reports, and fake/placeholder completion checks.
- **Capability Scan**: run an explicit one-time, read-only project capability scan for available plugins, apps, skills, MCP tools, useful mentions, risk boundaries, and project-specific recommendations.
- **Agent Run Smells**: detect weak planning, execution, validation, audit, and handoff signals even when the final diff looks plausible.

Routing matrix:

| User intent | Primary route | References to load |
|---|---|---|
| vague idea, autonomous goal, or `/goal` request | Goal Compiler | `goal-mode-contract-template.md`, `goal-mode-default-strategy.md` |
| authorized goal needs execution supervision | Goal Supervisor | `task-card-template.md`, `goal-mode-audit-prompts.md`, then handoff/human-gate refs as needed |
| long-running, resumed, multi-thread, or context-heavy goal | Task State Pack | `task-state-pack-template.md`, `stall-and-pivot-rules.md` |
| measurable optimization or candidate comparison | Experiment Lane | `evo-style-experiment-lane.md`, then `ideator-verifier-loop.md` when multiple directions exist |
| acceptance gates, fake completion, Definition of Done, or completion report | Supervision bridge | `project-supervisor-bridge.md`, then `$project-supervisor` |
| project plugin/capability inventory or recommendation | Capability Scan | `capability-audit-template.md`, `read-only-audit-guard.md` |
| weak run, fake progress, missing evidence, or "what smells wrong?" | Agent Run Smells | `agent-run-smells.md`, then `audit-rubric.md` |
| repeated failure, stale progress, or scope drift | Recovery audit | `goal-mode-recovery-stale-work.md`, `stall-and-pivot-rules.md`, `read-only-audit-guard.md` |
| completed run, commit, PR, or final claim | Efficiency Auditor | `read-only-audit-guard.md`, `audit-rubric.md`, `report-templates.md` |

Default goal autonomy is `supervised-autonomous`: Codex may inspect, plan, implement inside the authorized boundary, test, and report, but must pause before scope expansion, destructive changes, public release, credentials, billing, external account changes, or irreversible operations.

Do not create daily or global automations. Automation prompts may be suggested only after a user authorizes a specific goal, and they must be scoped to auditing, summarizing, drift detection, blocker detection, and next-prompt generation.

Capability Scan is explicit-only and one-time. Do not run it automatically during every Goal Contract, Task Card, periodic audit, or final audit. Use it only when the user asks to audit or recommend available Codex plugins, apps, skills, MCP tools, or project capability mentions.

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
   - For read-only audits: use `references/read-only-audit-guard.md`, collect `git status --short --branch`, `git diff --name-status`, and `git diff --cached --name-status` when available, and distinguish audited commit/diff file cards from audit-time mutations.
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
   - For read-only audits, include `Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN`.
   - Include evidence-backed strengths, gaps, and one paste-ready upgrade prompt.

## Goal Mode Workflow

Use this workflow when the user asks for goal mode, autonomous progress, task automation, multi-agent execution, or a bounded `/goal` prompt:

1. **Compile the goal**
   - Load `references/goal-mode-contract-template.md`.
   - If the request is vague and low risk, choose conservative defaults and output the recommended `/goal` first.
   - Ask only when a decision changes cost, risk, ownership, or product direction.

2. **Choose defaults and risk stance**
   - Load `references/goal-mode-default-strategy.md`.
   - For unfamiliar or specialized domains, create a discovery-first goal instead of inventing domain rules.
   - Put credentials, payments, production data, destructive operations, public release, external account changes, legal/medical/financial judgment, copyright, and unclear ownership into pause conditions.

3. **Supervise execution**
   - Use Goal Contract -> Preflight Audit -> Task Card -> Worktree/Agent Split -> Periodic Audit -> Final Closure.
   - Use `references/task-card-template.md` and `references/multi-worktree-orchestration-template.md` only after the Goal Contract is concrete enough.
   - Use `references/goal-mode-audit-prompts.md` for goal-specific start, preflight, periodic audit, drift stop, human-decision, and closure prompts.
   - Use `references/task-state-pack-template.md` for long-running, resumed, context-heavy, or multi-thread goals.
   - Use `references/stall-and-pivot-rules.md` when progress is stale, failures repeat, or the run loops over similar attempts.
   - Use `references/evo-style-experiment-lane.md` only for measurable optimization with concrete metric, direction, gates, boundaries, rollback, and human gates.
   - Use `references/ideator-verifier-loop.md` when multiple candidate directions, frontier-style exploration, literature/repo scan, or false-progress verification is needed.
   - Use `references/project-supervisor-bridge.md` when a goal needs acceptance gates, Definition of Done, a completion report, or protection against fake/placeholder completion.
   - Use `references/goal-mode-human-gates.md` before push, publish, deploy, destructive work, external account changes, or outbound comments.
   - Use `references/goal-mode-done-gate.md` and `references/goal-mode-evidence-bundle.md` before final completion claims.
   - Use `references/goal-mode-handoff-matrix.md` when multiple agents, worktrees, reviewers, auditors, or finalizers exchange work.
   - Use `references/goal-mode-recovery-stale-work.md` when a goal is long-running, resumed, compacted, repeatedly failing, stale, or drifting.

4. **Validate the contract**
   - For file deliverables containing goal contracts, run `scripts/lint_goal_mode_contract.py` when useful.
   - For Task State Pack directories, run `scripts/lint_task_state_pack.py` when useful.
   - For Experiment Lane contracts, run `scripts/lint_experiment_lane.py` when useful.
   - Revise goals that lack verification, boundaries, iteration policy, stop conditions, pause conditions, polling audit, human intervention triggers, or final report format.

## AutoResearch Loop Workflow

Use this workflow when the user asks for automated task advancement, self-optimization, long-running research, multiple candidate approaches, or deeper reuse of AutoResearch/evo-style ideas:

1. Start from a bounded `/goal` contract.
2. Decide whether the goal needs a Task State Pack. Use it when the task is long-running, resumed, context-heavy, multi-agent, or needs periodic audit.
3. Decide whether Experiment Lane is allowed. It is allowed only when metric, direction, gates, boundaries, rollback, and human gates are explicit.
4. Use Ideator/Verifier split for multi-direction exploration. Ideators propose; workers implement; verifiers audit; finalizers close.
5. Apply Stall/Pivot rules during periodic audit. Do not keep retrying without fresh evidence.
6. Close with Done Gate, Evidence Bundle, Read-Only Audit Guard, and Human Gates as applicable.

Do not install evo, modify hooks, add telemetry, create remote backends, or turn this skill into an execution runtime unless the user creates a separate explicit goal for that work.

## Capability Scan Workflow

Use this workflow only when the user explicitly asks for a project plugin/capability scan, such as "Audit my available Codex plugins and app capabilities", "project plugin capability audit", "Codex capability inventory", or a Chinese equivalent already listed in the frontmatter trigger description.

1. Load `references/capability-audit-template.md` and `references/read-only-audit-guard.md`.
2. Treat the scan as read-only reporting. Do not install, enable, disable, authenticate, publish, push, deploy, create automations, submit forms, comment externally, or mutate project files.
3. Do not read `auth.json`, secrets, tokens, OAuth material, private email lists, or credential stores.
4. Prefer compact mode unless the user asks for `full inventory` or the Chinese equivalent for a complete inventory.
5. Distinguish `enabled`, `available-in-session`, `installed-not-exposed`, and `missing-or-unknown`; mark unavailable data as best-effort instead of guessing.
6. Include detected plugin definitions, plugin capabilities, and cached plugin skills when they are relevant to the project.
7. Recommend 5-8 project-relevant capability families first, then list high-risk tools and required Human Gates.
8. Do not claim marketplace-wide not-installed plugins unless a reliable plugin catalog is available; otherwise report missing recommendations as `missing-or-unknown`.
9. Include `Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / UNKNOWN` in the report.
10. When local file access is available and `scripts/audit_codex_capabilities.py` exists, run it before composing the report. Pass project hints with `--context`, for example `--context "game GitHub repo UI/browser testing release gate"`. Use `--json` only when machine-readable output is requested. If the script cannot be run, state why and include `Scan basis: manual-only` or `Scan basis: transcript-only`.
11. Preserve domain plugins in the compact top recommendations. For game, playable, Godot, Phaser, Three.js, WebGL, sprite, or playtest projects, include detected `@game-studio` / `$game-studio:*` capabilities in the 5-8 recommended items even when they are `installed-not-exposed`.

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

Do not output a bare final verdict for a read-only audit unless the user explicitly asks for verdict-only output. Include mutation status, Git evidence, validation evidence, residual risks, and verdict.

## Templates

Load these references only when they fit the user's request:

- `references/read-only-audit-guard.md`: Use for any read-only review, final audit, commit audit, PR audit, periodic audit, Done Gate, or user prompt that says not to edit files.
- `references/agent-run-smells.md`: Use when a run looks superficially successful but may lack planning, ownership, validation, audit, or handoff evidence.
- `references/capability-audit-template.md`: Use for explicit, one-time project plugin/app/skill/MCP scans and compact project-specific capability recommendations.
- `references/autoresearch-adoption-notes.md`: Use when explaining what this project adopts or rejects from AutoResearch, paper-writing skill groups, and evo.
- `references/project-supervisor-bridge.md`: Use when combining `$codex-efficiency-auditor` with `$project-supervisor` for acceptance gates, completion reports, Definition of Done, or fake/placeholder completion control.
- `references/task-state-pack-template.md`: Use when a goal needs durable state files, recovery, handoff, or long-running audit.
- `references/stall-and-pivot-rules.md`: Use when progress is stale, repeated failures appear, or the run needs a structural pivot.
- `references/evo-style-experiment-lane.md`: Use when a task is metric-driven and may benefit from experiment-style candidate comparison.
- `references/ideator-verifier-loop.md`: Use when candidate proposal and false-progress verification should be separated.
- `references/goal-mode-contract-template.md`: Use when compiling or auditing a bounded `/goal` contract for goal mode.
- `references/goal-mode-default-strategy.md`: Use when choosing conservative defaults, risk stance, discovery-first goals, or automation boundaries.
- `references/goal-mode-audit-prompts.md`: Use when producing goal-mode start, preflight, periodic audit, drift stop, human-decision, or final closure prompts.
- `references/goal-mode-human-gates.md`: Use when high-risk actions require explicit approval or rejection tokens.
- `references/goal-mode-done-gate.md`: Use when deciding whether a run can be marked complete, ready for review, blocked, or needing fixes.
- `references/goal-mode-evidence-bundle.md`: Use when final reports need traceable proof across commands, artifacts, screenshots, CI, PRs, scans, and risks.
- `references/goal-mode-handoff-matrix.md`: Use when a goal involves worker, reviewer, auditor, finalizer, thread, or worktree handoffs.
- `references/goal-mode-recovery-stale-work.md`: Use when a run is stale, resumed, compacted, repeatedly failing, blocked, or drifting.
- `references/task-card-template.md`: Use when creating or auditing worker task cards, owned paths, shared locks, done criteria, or validation commands.
- `references/multi-worktree-orchestration-template.md`: Use when deciding whether a task should become a multi-agent/multi-worktree workflow.
- `references/paste-back-prompts.md`: Use when producing prompts that should be pasted into an original thread, worker thread, reviewer thread, or finalizer thread.

## Paste-Ready Upgrade Prompt Pattern

When a run is missing a final audit, provide a prompt like:

```text
Please perform a read-only Codex efficiency final audit for this run.
Load references/read-only-audit-guard.md.
Do not modify files, expand scope, or continue feature work.

Before the verdict, collect and report:
- git status --short --branch
- git diff --name-status
- git diff --cached --name-status
- Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN

Report:
- Codex capability utilization score out of 100
- Task Card: goal, owned paths, forbidden paths, shared locks, done criteria, validation commands
- Final Git state: branch, commit, changed files, clean/dirty status, generated files
- Validation evidence: targeted tests, full tests, audits, CI/PR status
- Risk review: state ownership, runtime/generated files, forbidden paths, external data/source boundaries
- Missing Codex leverage: subagents, worktree, CodeGraph, Browser, GitHub/PR, Cloud
- Verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```
