# Codex Efficiency Auditor

English | [中文](#中文)

A Codex skill for auditing whether a Codex thread, project, worktree, pull request, or agent run is using Codex capabilities effectively.

It helps evaluate planning quality, multi-agent readiness, worktree isolation, CodeGraph usage, GitHub/PR flow, validation depth, reporting quality, and concrete upgrade opportunities.

## Use Cases

- Audit a Codex thread id for capability utilization.
- Review a project or worktree before promoting a Codex workflow.
- Produce a final reviewer prompt for an in-progress Codex run.
- Score whether a task should have used subagents, CodeGraph, Browser, GitHub, Cloud, or stronger validation.
- Standardize Codex run handoffs across projects.

## Install

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

Or clone it directly into the skills directory:

```powershell
git clone https://github.com/M-sea-art/codex-efficiency-auditor.git "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

## Invoke

Use the skill explicitly:

```text
Use $codex-efficiency-auditor to audit this Codex thread: <thread-id>
```

```text
Use $codex-efficiency-auditor to evaluate this project for Codex capability utilization: <repo-path>
```

## What It Scores

The audit is scored out of 100:

- Goal and scope clarity
- Task decomposition and ownership
- Codex capability utilization
- Context and memory management
- Risk isolation and Git hygiene
- Verification and audit coverage
- Reporting and handoff quality
- Upgrade leverage

Verdict bands:

- `90-100`: exemplary Codex-native execution
- `75-89`: strong execution with clear upgrade opportunities
- `60-74`: useful but under-leveraged Codex run
- `40-59`: mostly single-thread execution with weak auditability
- `<40`: risky, unclear, or not meaningfully auditable

## Output Example

```text
Codex Capability Utilization: 82/100
Verdict: strong execution with clear upgrade opportunities

Evidence-backed strengths:
- Used a dedicated patch workspace.
- Ran targeted tests, full tests, state audit, and version audit.

Capability gaps:
- No explicit Task Card.
- No subagent reviewer.
- CodeGraph MCP was not initialized.

Recommended paste-back prompt:
...
```

## Repository Contents

- `SKILL.md`: core skill instructions
- `references/audit-rubric.md`: scoring rubric
- `references/report-templates.md`: output templates and final reviewer prompts
- `scripts/score_audit.py`: helper for totaling category scores
- `agents/openai.yaml`: Codex UI metadata

## Notes

This skill is intentionally lightweight. It does not call external services by itself and does not require runtime dependencies beyond Python for the optional scoring helper.

---

# 中文

[English](#codex-efficiency-auditor) | 中文

`codex-efficiency-auditor` 是一个 Codex Skill，用来审计一个 Codex 线程、项目、worktree、PR 或 agent run 是否充分利用了 Codex 的能力边界。

它关注的不是单次回答是否好看，而是整个执行过程是否具备清晰规划、合理并行、风险隔离、验证闭环、可审计报告和可升级空间。

## 适用场景

- 审计一个 Codex thread id 的能力利用率。
- 评估某个项目或 worktree 是否适合升级为多 agent / worktree / Cloud 并行流程。
- 为进行中的 Codex 任务生成最终只读审查 prompt。
- 判断任务是否应该使用 subagents、CodeGraph、Browser、GitHub、Cloud 或更强验证链路。
- 为多个项目沉淀统一的 Codex 执行复盘与交接标准。

## 安装

把本目录复制到 Codex skills 目录：

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

也可以直接 clone 到 skills 目录：

```powershell
git clone https://github.com/M-sea-art/codex-efficiency-auditor.git "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

## 调用方式

显式调用这个 skill：

```text
Use $codex-efficiency-auditor to audit this Codex thread: <thread-id>
```

```text
Use $codex-efficiency-auditor to evaluate this project for Codex capability utilization: <repo-path>
```

也可以直接说：

```text
使用 codex-efficiency-auditor 审计这个线程：<thread-id>
```

## 评分维度

审计满分为 100 分：

- 目标与范围清晰度
- 任务拆解与路径所有权
- Codex 能力利用
- 上下文与记忆管理
- 风险隔离与 Git 卫生
- 验证与审计覆盖
- 报告与交接质量
- 后续升级价值

评分区间：

- `90-100`：典范级 Codex-native 执行
- `75-89`：执行质量强，有明确升级空间
- `60-74`：有价值，但 Codex 能力利用不足
- `40-59`：偏单线程聊天式执行，可审计性弱
- `<40`：风险高、目标不清或难以审计

## 输出示例

```text
Codex Capability Utilization: 82/100
Verdict: strong execution with clear upgrade opportunities

Evidence-backed strengths:
- 使用了独立 patch workspace。
- 跑过定向测试、全量测试、状态审计和版本审计。

Capability gaps:
- 缺少标准 Task Card。
- 没有 subagent reviewer。
- CodeGraph MCP 未初始化。

Recommended paste-back prompt:
...
```

## 仓库内容

- `SKILL.md`：核心 skill 指令
- `references/audit-rubric.md`：评分标准
- `references/report-templates.md`：报告模板与最终审查 prompt
- `scripts/score_audit.py`：评分汇总辅助脚本
- `agents/openai.yaml`：Codex UI 元数据

## 说明

这个 skill 保持轻量设计。它本身不会调用外部服务，也没有额外运行时依赖；可选评分脚本只需要 Python。
