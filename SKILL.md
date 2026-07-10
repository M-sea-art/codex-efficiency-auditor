---
name: codex-efficiency-auditor
description: "Codexcavator is a Codex capability miner. Use it to audit a Codex thread, repository, worktree, pull request, transcript, or agent run; identify task-relevant Codex capabilities that are unavailable, undiscovered, unused, misused, or unverified; rank at most three evidence-backed upgrades; and verify whether the upgrades improved capability utilization. Trigger for Codex capability audits, Codex efficiency reviews, underused tools or plugins, project capability scans, weak validation, repeated agent failure, or requests to improve how Codex works."
---

# Codexcavator

## Purpose

Mine underused Codex capability. Determine which capabilities matter to the current goal, whether Codex used them effectively, and what smallest evidence-backed upgrade would improve the run.

Do not maximize tool count. Do not recommend capabilities merely because they are installed, popular, or novel. If the current Codex stack is sufficient, return `NO_CAPABILITY_UPGRADE_NEEDED`.

## Capability Mining Loop

1. **Orient**
   - Identify the audited target and its goal, constraints, state, and acceptance criteria.
   - Mark missing information as unknown. Do not invent evidence.
2. **Discover**
   - Identify only capabilities relevant to the goal.
   - Inspect current-session tools first, then project rules, local skills, plugins, MCP servers, CLIs, and existing validation commands.
   - Run `scripts/audit_codex_capabilities.py` for an explicit local capability inventory when local access is available.
3. **Observe**
   - Record whether each relevant capability was available, discovered, used correctly, and supported by evidence.
   - Prefer commands, logs, Git state, test output, traces, screenshots, artifacts, and tool calls over narrative claims.
4. **Classify**
   - Assign at most one primary gap to each relevant capability:
     - `UNAVAILABLE`: required capability is not present.
     - `UNDISCOVERED`: capability is present but Codex did not find it.
     - `UNUSED`: capability is relevant and known but not used.
     - `MISUSED`: capability was used at the wrong time, scope, or method.
     - `UNVERIFIED`: use or benefit was claimed without sufficient evidence.
5. **Upgrade**
   - Rank upgrades by task impact, evidence confidence, and reuse value minus adoption cost, context cost, and risk.
   - Recommend no more than three upgrades.
   - Prefer using the current Codex stack better before adding an external dependency.
   - When an external repository, library, plugin, MCP server, CLI, or workflow is considered, require evidence that it creates material net gain over the current stack.
6. **Verify**
   - Define a concrete check for every recommendation.
   - Re-audit after the change when evidence is available.
   - Retain an upgrade only when the relevant capability score or a required acceptance gate improves without unacceptable regression.

## Relevance Rule

Score only capabilities that materially affect the current goal. Never deduct points for an irrelevant tool, absent parallelism on a tightly coupled task, or a specialized plugin outside its domain.

Use `required`, `useful`, or `irrelevant` relevance labels. Exclude `irrelevant` capabilities from scoring and recommendations.

## Native Capability Rule

Treat the current Codex capability stack as the default solution. External additions must earn adoption.

- Prefer `NO_CAPABILITY_UPGRADE_NEEDED` when the current stack already meets the goal reliably.
- Prefer a focused hybrid improvement over adopting an entire external system.
- Reject additions whose expected gain does not exceed integration, maintenance, context, permission, or supply-chain cost.
- Do not install, authenticate, publish, push, deploy, or change external state during a read-only audit.

## Evidence and Scoring

Use `references/audit-rubric.md` and `scripts/score_audit.py` for structured capability-utilization scoring.

High-quality evidence includes:

- an actual tool call or command and its output;
- a test, build, CI, trace, screenshot, or runtime result;
- Git status, diff, commit, or pull-request evidence;
- an artifact whose provenance is clear;
- a before-and-after result tied to the same goal and acceptance criteria.

Narrative claims without corroborating evidence classify as `UNVERIFIED`.

## Output Contract

Lead with:

```text
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN
```

Then report:

1. task-relevant capabilities and evidence;
2. classified gaps;
3. at most three upgrades, each with expected gain and verification;
4. one concrete next action.

Do not produce generic plugin lists, broad transformation roadmaps, or multiple parallel plans unless the user explicitly asks for full inventory or long-form analysis.

## Read-Only Safety

For a read-only, final, commit, pull-request, or periodic audit, load `references/read-only-audit-guard.md`. Report whether the audit modified files.

Pause at `NEEDS_HUMAN_DECISION` before credentials, billing, destructive work, production changes, public release, external account changes, or outbound comments.

## Conditional Strategies

Load these only after the mining loop identifies the matching capability gap:

- unclear goal or acceptance criteria: `references/goal-mode-contract-template.md`
- weak task ownership or useful independent work: `references/task-card-template.md` and `references/multi-worktree-orchestration-template.md`
- stale or repeated failure: `references/stall-and-pivot-rules.md`
- measurable candidate comparison: `references/evo-style-experiment-lane.md`
- weak completion evidence: `references/goal-mode-evidence-bundle.md` and `references/goal-mode-done-gate.md`
- handoff failure: `references/goal-mode-handoff-matrix.md`
- long or resumed run: `references/task-state-pack-template.md`
- suspicious final claim: `references/agent-run-smells.md`

These are remediation strategies, not separate product modes.

## Stop Rules

- Stop discovery when the current Codex stack already satisfies the goal and evidence is sufficient.
- Do not recommend more than three upgrades.
- Do not recommend parallelism when work is small, ambiguous, or tightly coupled.
- Do not recommend a capability without explaining its task relevance and verification.
- Do not confuse unavailable evidence with failed implementation.
- Do not mark an upgrade successful without post-change evidence.
