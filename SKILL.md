---
name: codex-efficiency-auditor
description: "Codexcavator is an evidence-driven Codex capability and execution-efficiency auditor. Use it to audit a Codex thread, repository, worktree, pull request, transcript, or agent run; collect strict metadata-only run evidence; distinguish session availability from installed or disabled capability; identify unavailable, undiscovered, unused, misused, or unverified capability; choose the shortest safe upgrade route; and prove whether task outcomes or declared efficiency metrics improved. Trigger for Codex capability audits, Codex efficiency reviews, underused tools or plugins, weak validation, repeated failure, scope drift, or requests to improve how Codex works."
---

# Codexcavator

## Purpose

Determine which Codex capabilities materially affect the current goal, whether Codex used them within the authorized scope, and what smallest evidence-backed upgrade improves the task.

Do not maximize tool count. Do not recommend capabilities because they are installed, popular, or novel. If the current stack already satisfies the goal, return `NO_CAPABILITY_UPGRADE_NEEDED`.

Codexcavator owns Codex execution quality and capability utilization. It does not replace `project-supervisor`, which owns product completion, Definition of Done, and release gates.

## Start Here

For the default path, the user only needs to say:

```text
Use $codex-efficiency-auditor to audit this run. Keep the audit read-only unless I authorized changes.
```

Infer no missing authority. Lead with the v0.3 header, surface warnings, and end with exactly one concrete next action. Load the detailed rules below internally instead of asking the user to paste the full contract.

## Default v0.3 Workflow

1. **Orient**
   - Identify the target, goal, task mode, local mutation scope, external-action policy, constraints, Human Gates, and outcome criteria.
   - Mark missing contract facts `unknown`; do not infer authority.
2. **Collect**
   - For a Codex rollout JSONL, run `scripts/collect_run_evidence.py --input <rollout.jsonl>`.
   - The collector emits only strict metadata, hashes, tool names, counts, timing, token totals, and parse coverage. It never emits messages, reasoning, arguments, output, commands, paths, or raw IDs.
   - Fail closed on malformed or unknown event structures. `--allow-partial` is diagnostic only and can never support `PROVEN`.
3. **Discover**
   - Inspect current-session tools first, then project rules, local skills, plugins, MCP servers, CLIs, and validation commands.
   - Run `scripts/audit_codex_capabilities.py` for an explicit local inventory when local access is available.
   - Keep these states distinct: `available_in_session`, `installed_not_exposed`, `disabled`, `unavailable`, and `unknown`.
4. **Observe**
   - Record v0.3 evidence as `{kind, status, claim_scope, summary, locator?}`.
   - Only `capability_use + PASS` earns full capability-utilization credit.
   - Keep `capability_use`, `functional`, `visual`, `domain`, `integrity`, `human_acceptance`, `authorization`, `efficiency`, and `other` claims separate. A screenshot proves only visible state; an Agent cannot self-issue Human acceptance.
5. **Classify**
   - Assign at most one primary gap per relevant capability: `UNAVAILABLE`, `UNDISCOVERED`, `UNUSED`, `MISUSED`, or `UNVERIFIED`.
6. **Upgrade**
   - Rank no more than three upgrades by task impact, evidence confidence, reuse value, adoption cost, context cost, and risk.
   - Every upgrade must name the capability and exact gap, select one route, and define one falsifiable `smallest_useful_check`.
7. **Verify**
   - Re-audit the same target, normalized goal, operation contract, capability declarations, outcome declarations, and efficiency-metric thresholds.
   - Return `PROVEN` only when utilization improves, a real gap closes, and either a task outcome reaches `PASS` or a predeclared efficiency metric meets its threshold without regression.

## Shortest Safe Upgrade Routes

Use one route per retained upgrade:

- `REUSE`: use an existing project helper, command, test, workflow, or pattern.
- `NATIVE`: use Codex, the platform, standard library, framework, or host-native capability.
- `INSTALLED`: use an already-installed and appropriately exposed dependency, Skill, Plugin, app, MCP server, or local tool.
- `BUILD`: make the smallest necessary new implementation after the earlier routes fail.
- `DISCOVER_FIRST`: gather bounded evidence before choosing implementation.
- `HUMAN_GATE`: stop before credentials, billing, destructive work, production changes, public release, external-account changes, or outbound messages.

No upgrade is the equivalent of `SKIP`: return `NO_CAPABILITY_UPGRADE_NEEDED` instead of manufacturing work.

## Evidence and Comparison Rules

Use `references/audit-rubric.md`, `schemas/audit-report.schema.json`, and `scripts/score_audit.py`.

Comparison results:

- `PROVEN`: utilization and a real gap improve, plus outcome or declared cost improves without regression.
- `UTILIZATION_IMPROVED_OUTCOME_UNPROVEN`: capability use improved, but task benefit did not.
- `REGRESSION`: capability score, required outcome, declared metric, authorization scope, or audit mutation safety regressed.
- `INCONCLUSIVE`: declarations differ, scope is unknown, or run evidence is missing or partial.
- `NO_CHANGE`: comparable evidence shows no effective improvement.

The scorer validates declarations and internal consistency. It does not independently prove that a submitted summary is truthful.

## Output Contract

Lead with:

```text
Schema version: 0.3
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN
Scope conformance: PASS | FAIL | UNKNOWN
```

Then report only:

1. task-relevant capabilities and scoped evidence;
2. classified gaps;
3. at most three route-labeled upgrades with one smallest useful check each;
4. outcome or efficiency verification status;
5. one concrete next action.

Human-readable CLI output must expose warnings and exactly one `Next action`. Machine-readable JSON remains the stable integration surface.

Do not produce generic plugin lists or broad transformation roadmaps unless the user explicitly asks for a complete inventory.

## CLI

```text
python scripts/codexcavator.py audit <audit-v0.3.json> [--json]
python scripts/codexcavator.py compare --before <before-v0.3.json> --after <after-v0.3.json> [--json]
python scripts/codexcavator.py collect --input <rollout.jsonl> [--output <run-evidence.json>] [--allow-partial]
python scripts/codexcavator.py migrate --input <v0.2.json> [--output <v0.3.json>]
python scripts/codexcavator.py inventory --context "<goal and constraints>" [--json]
```

The original per-purpose scripts remain supported. The unified CLI returns exit code `2` for input failures, keeps stdout empty, and prints a stable error code plus one safe `NEXT` command. JSON errors are emitted to stderr when `--json` is present.

Migrated v0.2 audits preserve their individual score and gaps, but keep scope and run evidence unknown. They cannot inherit a v0.2 `PROVEN` comparison without fresh outcome or efficiency evidence.

## Read-Only Safety

For a read-only, final, commit, pull-request, or periodic audit, load `references/read-only-audit-guard.md`.

- Runtime metadata cannot by itself prove that files were unchanged; require Git or protected-file integrity evidence for `scope_conformance: PASS`.
- If genuine read-only isolation is unavailable, fail closed instead of treating `danger-full-access` as read-only.
- Do not install, authenticate, publish, push, deploy, comment externally, or modify project files during a read-only audit.

## Conditional Strategies

Load only when the matching gap exists:

- unclear goal or acceptance criteria: `references/goal-mode-contract-template.md`
- weak ownership or genuinely independent work: `references/task-card-template.md` and `references/multi-worktree-orchestration-template.md`
- repeated failure: `references/stall-and-pivot-rules.md`
- measurable comparison: `references/evo-style-experiment-lane.md`
- weak completion evidence: `references/goal-mode-evidence-bundle.md` and `references/goal-mode-done-gate.md`
- handoff failure: `references/goal-mode-handoff-matrix.md`
- long or resumed run: `references/task-state-pack-template.md`
- suspicious completion claim: `references/agent-run-smells.md`

These are remediation strategies, not separate product modes.

## Stop Rules

- Stop discovery when the current stack satisfies the goal and evidence is sufficient.
- Do not recommend more than three upgrades.
- Do not recommend parallelism for small, ambiguous, or tightly coupled work.
- Do not confuse missing evidence with failed implementation.
- Do not mark utilization improvement as task improvement without outcome or efficiency proof.
