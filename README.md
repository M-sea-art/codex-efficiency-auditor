<div align="center">
  <img width="100%" alt="Codexcavator — Codex capability miner" src="https://github.com/user-attachments/assets/38c0a4c0-b754-4929-84d2-ce09043cc984" />
  <h1>Codexcavator</h1>
  <h3>Evidence-driven capability and execution-efficiency audits for Codex</h3>
  <p>Find the capability that matters, stay inside the authorized scope, and prove that the upgrade improved the task.</p>
  <p>
    <a href="https://github.com/M-sea-art/codex-efficiency-auditor/actions/workflows/codexcavator-audit.yml"><img alt="Codexcavator Audit" src="https://github.com/M-sea-art/codex-efficiency-auditor/actions/workflows/codexcavator-audit.yml/badge.svg" /></a>
    <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg" /></a>
  </p>
  <p><a href="#choose-your-path">English</a> · <a href="#选择你的路径">中文</a></p>
</div>

> CI checks the code. Codexcavator checks whether Codex used the right capability, respected the operation contract, and produced measurable gain.

Codexcavator is an unofficial open-source Codex Skill and deterministic audit toolkit. It audits a thread, repository, worktree, pull request, transcript, or agent run for task-relevant capability that is unavailable, undiscovered, unused, misused, or unverified.

It does not reward tool volume. It does not turn an inventory into an install list. If the current Codex stack already does the job, the correct result is `NO_CAPABILITY_UPGRADE_NEEDED`.

## Choose Your Path

### Use the installed Codex Skill

Paste one sentence into Codex:

```text
Use $codex-efficiency-auditor to audit this run. Keep the audit read-only unless I authorized changes.
```

Codexcavator will declare the operation contract, keep evidence scopes separate, recommend at most three upgrades, and return one next action. It will not return `PROVEN` unless a real outcome or declared efficiency metric also improves.

If the Skill is not installed, ask Codex to install it from this repository and verify it in a fresh process. Installation is a separate action; an audit never installs or authenticates by itself.

### Try the CLI without reading the Schema

Run one safe bundled example:

```bash
python scripts/codexcavator.py audit examples/real-world/read-only-state-isolation/audit.json
```

The result includes warnings and exactly one next action. Use `--json` when another program consumes the result.

### Start from a Codex rollout JSONL

```bash
python scripts/codexcavator.py collect --input examples/quickstart/minimal-rollout.jsonl
python scripts/codexcavator.py collect --input path/to/rollout.jsonl --output run-evidence.json
```

### Compare before and after

```bash
python scripts/codexcavator.py compare --before examples/real-world/registered-disabled-fresh-process/before.json --after examples/real-world/registered-disabled-fresh-process/after.json
```

### Migrate or inspect availability

```bash
python scripts/codexcavator.py migrate --input examples/migration/v0.2-audit.json --output audit-v0.3.json
python scripts/codexcavator.py inventory --context "the actual task goal and constraints"
```

The original `collect_run_evidence.py`, `score_audit.py`, `migrate_audit.py`, and `audit_codex_capabilities.py` entrypoints remain supported for automation compatibility.

Expected audit header:

```text
Schema version: 0.3
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN
Scope conformance: PASS | FAIL | UNKNOWN
```

## Why This Exists

Capability availability does not guarantee effective use. A Skill, Plugin, MCP server, CLI, browser, test path, or subagent workflow may be installed but not exposed in the current session, discovered too late, used outside the authorized scope, or credited without evidence.

Earlier audit contracts could also prove only that capability utilization improved. That is not enough: a busier agent is not necessarily a better agent.

The v0.3 evidence loop asks four separate questions:

1. Was the capability callable in this session?
2. Was it used correctly and within the declared operation contract?
3. Did a real capability gap close?
4. Did a task outcome reach `PASS`, or did a predeclared efficiency metric improve?

Only that full chain returns `PROVEN`.

## Evidence Loop

```text
Orient operation contract
  -> collect strict run metadata
  -> discover session-relevant capability
  -> separate evidence claim scopes
  -> classify one gap per capability
  -> choose at most three shortest-safe routes
  -> re-audit the same declarations
  -> prove outcome or cost gain
```

### Capability states

| State | Meaning |
|---|---|
| `available_in_session` | Explicitly exposed in the audited session. |
| `installed_not_exposed` | Present locally, but callable session exposure is not proven. |
| `disabled` | Explicitly disabled in local configuration. |
| `unavailable` | Confirmed absent for the audited run. |
| `unknown` | Evidence is insufficient. |

### Evidence claim scopes

Evidence declares what it can prove: `capability_use`, `functional`, `visual`, `domain`, `integrity`, `human_acceptance`, `authorization`, `efficiency`, or `other`.

Only `capability_use + PASS` earns full utilization credit. A screenshot cannot close a functional outcome, and an Agent cannot self-issue Human acceptance.

### Upgrade routes

Every retained upgrade chooses one route: `REUSE`, `NATIVE`, `INSTALLED`, `BUILD`, `DISCOVER_FIRST`, or `HUMAN_GATE`. It must also declare one falsifiable `smallest_useful_check`.

No upgrade is the equivalent of `SKIP`; Codexcavator returns `NO_CAPABILITY_UPGRADE_NEEDED` instead of manufacturing work.

## Strict Run Evidence

Collect metadata from a Codex rollout JSONL:

```bash
python scripts/codexcavator.py collect --input path/to/rollout.jsonl
python scripts/codexcavator.py collect --input path/to/rollout.jsonl --output run-evidence.json
```

The collector retains only:

- SHA-256 source and identifier hashes;
- safe CLI/session metadata;
- task, turn, tool, MCP, search, patch, and failure counts;
- duration, time-to-first-token, and token totals;
- parser coverage and unknown event types.

It never emits messages, reasoning, arguments, tool output, commands, paths, working directories, or raw session/turn/call identifiers.

Malformed JSONL and unknown event structures fail closed with exit code `2`. `--allow-partial` emits `parse_status: PARTIAL` for diagnostics; partial evidence can never support `PROVEN`.

## Error Recovery

Unified CLI input failures return exit code `2` and leave stdout empty. Human mode writes `ERROR`, an optional safety `NOTE`, and one executable `NEXT` command to stderr. With `--json`, stderr contains the same fields as a JSON error object.

| Error code | Meaning |
|---|---|
| `FILE_NOT_FOUND` | The requested input does not exist. |
| `JSON_INVALID` | The input is not valid JSON. |
| `AUDIT_SCHEMA_INVALID` | The input does not satisfy the requested v0.3 or inventory contract. |
| `ROLLOUT_PARSE_FAILED` | JSONL is malformed, incomplete, or contains an unknown critical structure. |
| `V02_MIGRATION_REQUIRED` | A v0.2 audit must be explicitly migrated before scoring. |

Errors never echo message bodies, commands, private paths, secret values, or raw identifiers. `--allow-partial` is offered only as a diagnostic and cannot support `PROVEN`.

## Score and Compare

```bash
python scripts/codexcavator.py audit path/to/audit-v0.3.json --json
python scripts/codexcavator.py compare --before path/to/before.json --after path/to/after.json --json
```

Comparison results:

| Result | Meaning |
|---|---|
| `PROVEN` | Utilization and a real gap improve, plus a task outcome or declared metric improves without regression. |
| `UTILIZATION_IMPROVED_OUTCOME_UNPROVEN` | Capability use improved, but task benefit did not. |
| `REGRESSION` | Capability, required outcome, metric, scope, or mutation safety regressed. |
| `INCONCLUSIVE` | Declarations differ, scope is unknown, or run evidence is missing/partial. |
| `NO_CHANGE` | Comparable evidence shows no effective improvement. |

Comparable audits must preserve the target type, normalized goal, operation contract, capability declarations, outcome declarations, and efficiency-metric thresholds. Reweighting or changing the contract cannot manufacture improvement.

## Migrate v0.2 Audits

```bash
python scripts/codexcavator.py migrate --input old-v0.2.json
python scripts/codexcavator.py migrate --input old-v0.2.json --output audit-v0.3.json
```

Migration preserves the individual utilization score and gap classification. Missing operation-contract, scope, outcome, metric, and run evidence remains unknown. A migrated before/after pair cannot inherit `PROVEN` until fresh evidence is supplied.

## Capability Inventory

```bash
python scripts/codexcavator.py inventory --context "the actual task goal and constraints"
python scripts/codexcavator.py inventory --context "the actual task goal and constraints" --json
```

The inventory distinguishes enabled, disabled, installed-not-exposed, and explicitly current-session capability. Presence is not proof of relevance or benefit; continue to a focused audit before recommending adoption.

## Repository Contents

- `SKILL.md`: routing and evidence-loop workflow.
- `scripts/codexcavator.py`: unified human and automation entrypoint.
- `scripts/cli_support.py`: shared warnings, next actions, and privacy-bounded errors.
- `schemas/audit-report.schema.json`: strict v0.3 audit contract.
- `schemas/run-evidence.schema.json`: strict metadata-only collector output.
- `scripts/collect_run_evidence.py`: privacy-bounded Codex JSONL collector.
- `scripts/score_audit.py`: deterministic scoring and before/after verification.
- `scripts/migrate_audit.py`: deterministic v0.2-to-v0.3 migration.
- `examples/`: weak, strong, migration, and sanitized real-world fixtures.

Additional references are conditional remediation strategies, not separate product modes.

`project-supervisor` owns product-completion truth and long-running supervision. Codexcavator owns the narrower question of whether Codex discovered, used, and verified the capabilities needed for the current goal.

## Development Checks

```bash
python -m compileall -q scripts
python scripts/test_capability_scan.py
python scripts/test_score_audit.py
python scripts/test_run_evidence.py
python scripts/test_migrate_audit.py
python scripts/test_cli_ux.py
python scripts/test_docs_ux.py
python scripts/test_examples.py
python scripts/score_audit.py --json examples/run-54-single-thread/audit-scores.json
python scripts/score_audit.py --json examples/run-82-worktree-review/audit-scores.json
python scripts/score_audit.py --json examples/real-world/read-only-state-isolation/audit.json
python scripts/score_audit.py --json examples/real-world/visual-proof-human-gate/audit.json
python scripts/score_audit.py --baseline examples/real-world/registered-disabled-fresh-process/before.json --json examples/real-world/registered-disabled-fresh-process/after.json
```

## Project Status

Codexcavator is an early-stage, independently maintained project. v0.3 remains an unreleased pre-stable contract; v0.3.1 adds a non-breaking first-success experience over the same Schema and proof semantics. The project publishes schemas, deterministic checks, privacy fixtures, migration tooling, and real-world examples so claims can be reproduced.

- **Maintainer:** [M-sea-art](https://github.com/M-sea-art)
- **Contributing:** see [CONTRIBUTING.md](CONTRIBUTING.md)
- **Release history:** see [CHANGELOG.md](CHANGELOG.md)

No stable tag is published until CI, migration, privacy, schema, example, and release checks all pass.

## 中文简介

Codexcavator（Codex 挖掘机）不是让 Codex 使用更多工具，而是判断当前任务真正需要什么能力、该能力是否在本次会话可用、是否在授权范围内正确使用，以及升级后任务结果或成本是否真的改善。

### 选择你的路径

在 Codex 中直接粘贴：

```text
使用 $codex-efficiency-auditor 审计这次执行；除非我已经授权修改，否则保持只读。
```

从仓库 CLI 开始时，无需先阅读 Schema：

```bash
python scripts/codexcavator.py audit examples/real-world/read-only-state-isolation/audit.json
python scripts/codexcavator.py collect --input examples/quickstart/minimal-rollout.jsonl
python scripts/codexcavator.py compare --before examples/real-world/registered-disabled-fresh-process/before.json --after examples/real-world/registered-disabled-fresh-process/after.json
```

人类可读输出会显示 warnings 和唯一下一动作；自动化调用增加 `--json`。输入错误返回退出码 `2`、稳定错误码和安全的 `NEXT` 命令，不输出消息正文、命令、私有路径或原始标识。

v0.3 默认流程是：

```text
采集严格脱敏运行元数据
  -> 声明任务模式与权限边界
  -> 只审计相关能力
  -> 区分功能、视觉、领域、人类验收和效率证据
  -> 最多给出三条最短安全升级路线
  -> 用同一目标复验结果或成本
```

只有“能力利用改善 + 真实缺口关闭 + 结果门禁或预声明效率指标改善”才返回 `PROVEN`。如果只是工具用得更多，则返回 `UTILIZATION_IMPROVED_OUTCOME_UNPROVEN`。

采集器默认不输出对话、推理、参数、结果、命令、路径或原始标识；遇到未知结构会失败关闭。旧 v0.2 审计可迁移并保持单份分数，但不能在没有新证据时继承旧的 `PROVEN`。

## Disclaimer

Codexcavator is an independent, unofficial open-source project. It is not affiliated with, endorsed by, or sponsored by OpenAI.
