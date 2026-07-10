# Codexcavator / Codex 挖掘机

> Mine the Codex capability that matters. Do not maximize tool count.

Codexcavator is an unofficial Codex Skill for finding capability that Codex could have used better in a thread, repository, worktree, pull request, transcript, or agent run.

It answers one question:

> Which task-relevant Codex capability is unavailable, undiscovered, unused, misused, or unverified—and what is the smallest evidence-backed upgrade?

Codexcavator does not replace Codex, install a collection of tools, or reward using every available plugin. If the current Codex stack already satisfies the goal, it returns `NO_CAPABILITY_UPGRADE_NEEDED`.

## Capability Mining Loop

```text
Orient
  → Discover task-relevant capabilities
  → Observe actual use and evidence
  → Classify capability gaps
  → Recommend at most three upgrades
  → Verify the result
```

## Five Gap Types

| Gap | Meaning |
|---|---|
| `UNAVAILABLE` | A required or useful capability is confirmed absent. |
| `UNDISCOVERED` | The capability exists, but Codex did not find it. |
| `UNUSED` | The capability is relevant and known, but was not used. |
| `MISUSED` | The capability was used with the wrong timing, scope, or method. |
| `UNVERIFIED` | Correct use or benefit was claimed without sufficient evidence. |

## What It Audits

- task goal and acceptance criteria;
- current-session tools and actual tool calls;
- project rules, Skills, Plugins, MCP servers, CLIs, and validation commands;
- commands, logs, tests, traces, screenshots, artifacts, and Git evidence;
- whether a proposed external addition creates net gain over the current Codex stack.

Only task-relevant capabilities are scored. Missing an irrelevant tool is not a defect.

## Quickstart

Paste this into Codex:

```text
Use $codex-efficiency-auditor.

Audit this Codex run for task-relevant capability utilization.
Classify gaps only as UNAVAILABLE, UNDISCOVERED, UNUSED, MISUSED, or UNVERIFIED.
Recommend no more than three evidence-backed upgrades.
If the current Codex stack is sufficient, return NO_CAPABILITY_UPGRADE_NEEDED.
```

Expected output:

```text
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN
```

The report then lists relevant capabilities, evidence, classified gaps, at most three upgrades, and one concrete next action.

## Evidence-Derived Scoring

Codexcavator scores only available capabilities marked `required` or `useful` for the current goal.

| Usage | Value |
|---|---:|
| Correctly used with evidence | 1.0 |
| Used without evidence | 0.25 |
| Misused | 0.25 |
| Unused | 0.0 |

Required capabilities receive their full impact weight. Useful capabilities receive a reduced weight. Irrelevant capabilities are excluded.

Run a structured audit:

```bash
python scripts/score_audit.py --json path/to/audit.json
```

The input format is defined in `schemas/audit-report.schema.json`.

Verify an upgrade against a comparable baseline:

```bash
python scripts/score_audit.py \
  --baseline path/to/before.json \
  --json path/to/after.json
```

The goal and task-relevant capability set must match. Otherwise the result is `INCONCLUSIVE`.

## Capability Inventory

The read-only scanner inventories locally visible Codex Skills, Plugins, MCP servers, and related manifests:

```bash
python scripts/audit_codex_capabilities.py \
  --context "the actual task goal and constraints"
```

For machine-readable output:

```bash
python scripts/audit_codex_capabilities.py \
  --context "the actual task goal and constraints" \
  --json
```

Inventory presence does not prove task relevance, correct use, or net benefit. Continue to a focused capability audit before recommending adoption.

## Native Capability Rule

The current Codex stack is the default solution.

- Prefer better use of existing capabilities before adding dependencies.
- Do not adopt a repository, library, plugin, MCP server, CLI, or workflow because it is novel or popular.
- Require task-level evidence of material net gain.
- Count integration, maintenance, context, permission, and supply-chain cost.
- Prefer a focused hybrid improvement over adopting an entire external system.

## Repository Contents

- `SKILL.md`: concise routing and capability-mining workflow.
- `references/capability-mining-model.md`: capability record, gap precedence, scoring, and upgrade ranking.
- `references/audit-rubric.md`: evidence and decision rules.
- `references/capability-audit-template.md`: focused report template.
- `references/read-only-audit-guard.md`: mutation and Git evidence protection.
- `scripts/audit_codex_capabilities.py`: read-only local capability inventory.
- `scripts/score_audit.py`: deterministic capability-utilization scoring.
- `schemas/audit-report.schema.json`: machine-readable audit contract.
- `examples/`: weak and strong audit fixtures.

Additional references are remediation strategies. Codexcavator loads them only when the mining loop identifies the matching gap; they are not separate product modes.

## Safety

Read-only audits do not install, authenticate, publish, push, deploy, comment externally, or mutate project files. Credentials, billing, destructive actions, production changes, public releases, external account changes, and outbound comments require a Human Gate.

The scanner avoids authentication files and credential stores. Review full inventory output before sharing it publicly because it may contain local environment metadata.

## Install

```powershell
git clone https://github.com/M-sea-art/codex-efficiency-auditor.git "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

## Development Checks

```bash
python -m py_compile scripts/*.py
python scripts/test_capability_scan.py
python scripts/test_score_audit.py
python scripts/score_audit.py --json examples/run-54-single-thread/audit-scores.json
python scripts/score_audit.py --json examples/run-82-worktree-review/audit-scores.json
python scripts/score_audit.py --baseline before.json --json after.json
```

## Disclaimer

Codexcavator is an independent, unofficial open-source project. It is not affiliated with, endorsed by, or sponsored by OpenAI.

---

## 中文简介

Codexcavator（Codex 挖掘机）只做一件事：挖出当前任务中尚未发挥的 Codex 能力。

它不会因为工具装得多就给高分，也不会为了体现价值而强行推荐插件。它只评估与当前目标真正相关的能力，依据实际命令、测试、日志、Git、截图、轨迹和产物证据，判断能力是缺失、未发现、未使用、误用，还是缺少验证。

每次最多给出三个升级建议。如果当前 Codex 组合已经足够，它会明确返回：

```text
NO_CAPABILITY_UPGRADE_NEEDED
```
