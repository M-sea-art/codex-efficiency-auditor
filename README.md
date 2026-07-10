<div align="center">
  <img width="100%" alt="Codexcavator — Codex capability miner" src="https://github.com/user-attachments/assets/38c0a4c0-b754-4929-84d2-ce09043cc984" />
  <h1>Codexcavator</h1>
  <h3>The evidence-driven capability miner for Codex</h3>
  <p>Find the Codex capability that matters to the task, prove how it was used, and recommend the smallest upgrade that creates real gain.</p>
  <p>
    <a href="https://github.com/M-sea-art/codex-efficiency-auditor/actions/workflows/codexcavator-audit.yml"><img alt="Codexcavator Audit" src="https://github.com/M-sea-art/codex-efficiency-auditor/actions/workflows/codexcavator-audit.yml/badge.svg" /></a>
    <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg" /></a>
  </p>
  <p><a href="#why-this-exists">English</a> · <a href="#中文简介">中文</a></p>
</div>

> CI checks the code. Codexcavator checks whether Codex used the right capabilities—and whether the evidence supports the claim.

Codexcavator is an unofficial Codex Skill for auditing a thread, repository, worktree, pull request, transcript, or agent run. It identifies task-relevant capability that is unavailable, undiscovered, unused, misused, or unverified.

It does not reward tool volume. It does not turn an inventory into an install list. If the current Codex stack already does the job well, the correct answer is `NO_CAPABILITY_UPGRADE_NEEDED`.

## Why This Exists

Codexcavator grew out of a recurring problem observed in real Codex work:

Codex may have access to many built-in tools, Skills, Plugins, MCP servers, CLIs, and open-source projects—but capability availability does not guarantee capability discovery or effective use.

A useful capability may be overlooked, invoked too late, applied incorrectly, or recommended without practical validation. Sometimes the current Codex stack is already sufficient, and adding another tool only increases complexity.

Codexcavator turns these questions into an evidence-backed capability audit:

- Was a task-relevant capability overlooked?
- Was an available capability left unused?
- Was a capability applied incorrectly?
- Was the claimed benefit actually verified?
- Is the current Codex stack already sufficient?

The goal is not to make Codex use more tools.

The goal is to help Codex use the right capability—and prove that it helped.

## Why Codexcavator

| A generic capability inventory | Codexcavator |
|---|---|
| Lists everything that exists | Filters to what materially affects this goal |
| Treats installed as useful | Separates available, discovered, used, and verified |
| Encourages more tools | Treats the current Codex stack as the default |
| Relies on narrative judgment | Scores commands, tests, traces, Git, and artifacts |
| Produces a broad roadmap | Returns no more than three verifiable upgrades |

## 30-second Quickstart

Paste into Codex:

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

The report lists only relevant capabilities, supporting evidence, classified gaps, at most three upgrades, and one concrete next action.

## What It Finds

| Gap | Meaning |
|---|---|
| `UNAVAILABLE` | A required or useful capability is confirmed absent. |
| `UNDISCOVERED` | The capability exists, but Codex did not find it. |
| `UNUSED` | The capability is relevant and known, but was not used. |
| `MISUSED` | The capability was used with the wrong timing, scope, or method. |
| `UNVERIFIED` | Correct use or benefit was claimed without sufficient evidence. |

## How It Works

```text
Orient
  → Discover task-relevant capabilities
  → Observe actual use and evidence
  → Classify capability gaps
  → Recommend at most three upgrades
  → Verify the result
```

Codexcavator examines the goal and acceptance criteria, current-session tools, project rules, Skills, Plugins, MCP servers, CLIs, validation commands, logs, tests, traces, screenshots, artifacts, and Git evidence. Only capabilities that materially affect the goal are scored.

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

### 为什么创建 Codexcavator

Codexcavator 来自长期使用 Codex 时反复遇到的一个问题：

Codex 可能已经拥有许多内置工具、Skill、插件、MCP、CLI 和开源能力，但“拥有能力”并不等于“能够主动发现并正确使用能力”。

某项能力可能被遗漏、没有使用、使用时机不对，或者在没有实际验证的情况下被推荐。有时，Codex 当前的原生组合其实已经足够，继续增加工具只会增加复杂度。

因此，Codexcavator 关注的不是“还能安装什么”，而是：

- 当前任务是否遗漏了相关能力？
- 已有能力是否没有被使用？
- 某项能力是否被错误应用？
- 所谓的提升是否有实际证据？
- 原生 Codex 组合是否已经足够？

它的目标不是让 Codex 使用更多工具。

而是让 Codex 找到正确的能力，并证明这项能力确实带来了提升。

### 它如何工作

Codexcavator（Codex 挖掘机）是一套以证据为基础的 Codex 能力挖掘 Skill。它只回答一个问题：

> 当前任务中，哪些 Codex 能力没有被发现、没有被正确使用，或者没有得到证据验证？最小的有效升级是什么？

它不是插件清单，也不是“装得越多越强”的工具推荐器。它只评估与目标真正相关的能力，依据命令、测试、日志、Git、截图、轨迹和产物，将缺口归为：不可用、未发现、未使用、误用或未验证。

- 只评分与当前目标有关的能力；
- 优先挖掘现有 Codex 组合，而不是增加依赖；
- 每次最多给出三个可验证升级；
- 如果现有组合已经足够，就不强行推荐工具。

30 秒使用：

```text
使用 $codex-efficiency-auditor 审计本次 Codex 执行。
只评估与目标相关的能力，依据实际证据分类能力缺口。
最多给出三个可验证升级；如果当前组合已经足够，返回 NO_CAPABILITY_UPGRADE_NEEDED。
```

当不需要升级时，它会明确返回：

```text
NO_CAPABILITY_UPGRADE_NEEDED
```
