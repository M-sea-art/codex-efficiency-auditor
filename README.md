# Codex Efficiency Auditor

English | [中文](#中文)

A Codex skill for auditing whether a Codex thread, project, worktree, pull request, or agent run is using Codex capabilities effectively.

It helps evaluate planning quality, multi-agent readiness, worktree isolation, CodeGraph usage, GitHub/PR flow, validation depth, reporting quality, and concrete upgrade opportunities.

The skill can be used after a run, but it is most useful as part of a Codex engineering loop: goal contract, preflight split check, worker guardrails, read-only review, periodic audit, paste-back prompt, and finalizer handoff.

The goal-mode layer is inspired by the strong `/goal` contract principles in [joeseesun/qiaomu-goal-meta-skill](https://github.com/joeseesun/qiaomu-goal-meta-skill): every durable Codex goal should have an outcome, verification, constraints, boundaries, iteration policy, stop conditions, and pause conditions. This project extends that idea into goal supervision, multi-agent/worktree orchestration, polling audit, and version closure.

The autoresearch-loop layer adapts public workflow ideas from Deli_AutoResearch, Scientific Paper Writing Skill Group, and evo into lightweight Codex audit templates. It does not install evo, modify Codex hooks, add telemetry, create dashboards, or run autonomous optimization runtimes.

## Three-Layer Model

- **Goal Compiler**: turns vague requests into paste-ready `/goal` contracts.
- **Goal Supervisor**: supervises authorized goals through preflight audit, Task Cards, worktree/agent split decisions, periodic audit, drift stops, and final closure.
- **Efficiency Auditor**: scores running or completed Codex work for capability utilization, risk isolation, validation depth, and handoff quality.

Cross-cutting controls:

- **Task State Pack**: durable state files for long-running goals.
- **Stall/Pivot Rules**: stop repeated low-evidence retries and force structural pivots.
- **Experiment Lane**: metric-driven variants only when required gates pass.
- **Ideator/Verifier Loop**: separate proposal generation, implementation, and read-only verification.

## Use Cases

- Audit a Codex thread id for capability utilization.
- Review a project or worktree before promoting a Codex workflow.
- Produce a final reviewer prompt for an in-progress Codex run.
- Convert a vague request into a bounded `/goal` contract.
- Supervise an authorized goal-mode run without creating global daily automation.
- Detect scope drift, missing validation, blockers, and human-decision points during a run.
- Run read-only final audits with explicit mutation status and Git evidence, so Codex UI file cards are not confused with audit-time edits.
- Add Human Gates, Done Gates, Evidence Bundles, handoff matrices, and recovery snapshots to long-running Codex work.
- Add Task State Packs, stale-count pivot rules, Experiment Lane preflights, and Ideator/Verifier prompts for long-running or self-improving goals.
- Score whether a task should have used subagents, CodeGraph, Browser, GitHub, Cloud, or stronger validation.
- Standardize Codex run handoffs across projects.
- Generate task cards, multi-worktree orchestration prompts, and paste-back prompts for improving future runs.

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

Create a goal-mode contract:

```text
Use $codex-efficiency-auditor as a Goal Compiler.
Turn this request into a bounded Codex /goal contract:
<request>
```

Supervise an authorized goal:

```text
Use $codex-efficiency-auditor as a goal-mode supervisor.
Perform a read-only periodic audit of this run against the authorized /goal contract.
```

Run a protected read-only final audit:

```text
Use $codex-efficiency-auditor and load references/read-only-audit-guard.md.
Perform a read-only final audit for commit <commit>.
Report Audit mutation status, Git evidence, UI file card provenance, validation evidence, residual risks, and verdict.
```

Evaluate an experiment-style goal:

```text
Use $codex-efficiency-auditor and load references/evo-style-experiment-lane.md.
Run a read-only Experiment Lane Preflight for this metric-driven goal.
```

Create a long-run state protocol:

```text
Use $codex-efficiency-auditor and load references/task-state-pack-template.md.
Create a Task State Pack proposal for this authorized /goal.
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
- `references/autoresearch-adoption-notes.md`: what is adopted or rejected from AutoResearch, paper-writing skill groups, and evo
- `references/read-only-audit-guard.md`: protected read-only audit rules, mutation status, Git evidence, and UI file card disambiguation
- `references/task-state-pack-template.md`: durable state pack protocol for long-running Codex goals
- `references/stall-and-pivot-rules.md`: stale-count and structural pivot rules
- `references/evo-style-experiment-lane.md`: metric/gate experiment-lane preflight and audit rules
- `references/ideator-verifier-loop.md`: role split for candidate generation and false-progress verification
- `references/report-templates.md`: output templates and final reviewer prompts
- `references/goal-mode-contract-template.md`: bounded `/goal` contract template
- `references/goal-mode-default-strategy.md`: conservative defaults, risk classification, discovery-first goals, and automation boundaries
- `references/goal-mode-audit-prompts.md`: goal-mode start, preflight, periodic audit, drift stop, human-decision, and closure prompts
- `references/goal-mode-human-gates.md`: explicit approval/rejection gates for push, publish, deploy, destructive work, account changes, credentials, paid services, and outbound comments
- `references/goal-mode-done-gate.md`: deterministic completion gate for contract, scope, evidence, pause scan, and next-task checks
- `references/goal-mode-evidence-bundle.md`: final proof index for commands, artifacts, screenshots, CI/PR status, scans, gates, and risks
- `references/goal-mode-handoff-matrix.md`: required handoff fields for workers, reviewers, auditors, finalizers, threads, and worktrees
- `references/goal-mode-recovery-stale-work.md`: stale progress, repeated failure, recovery, compaction, and drift status templates
- `references/task-card-template.md`: bounded worker task card template
- `references/multi-worktree-orchestration-template.md`: preflight split and worktree orchestration template
- `references/paste-back-prompts.md`: prompts for worker, reviewer, auditor, and finalizer handoffs
- `scripts/score_audit.py`: helper for totaling category scores
- `scripts/lint_goal_mode_contract.py`: helper for validating goal-mode contracts
- `scripts/lint_task_state_pack.py`: helper for validating Task State Pack directories
- `scripts/lint_experiment_lane.py`: helper for validating Experiment Lane contracts
- `agents/openai.yaml`: Codex UI metadata

## Notes

This skill is intentionally lightweight. It does not call external services by itself and does not require runtime dependencies beyond Python for the optional scoring helper.

---

# 中文

[English](#codex-efficiency-auditor) | 中文

`codex-efficiency-auditor` 是一个 Codex Skill，用来审计一个 Codex 线程、项目、worktree、PR 或 agent run 是否充分利用了 Codex 的能力边界。

它关注的不是单次回答是否好看，而是整个执行过程是否具备清晰规划、合理并行、风险隔离、验证闭环、可审计报告和可升级空间。

它可以在任务结束后复盘，也可以放进 Codex 多线工程闭环中：先生成目标合同，开工前判断是否值得拆分，执行中检查 worker 是否跑偏，周期审计验证缺口和阻塞，完成后生成审计报告和可回填到原线程的升级 prompt。

目标模式层参考了 [joeseesun/qiaomu-goal-meta-skill](https://github.com/joeseesun/qiaomu-goal-meta-skill) 的强 `/goal` 合同思想：长期任务应该有目标结果、验证、约束、边界、迭代策略、完成条件和暂停条件。本项目在此基础上扩展为目标监督、多 agent/worktree 编排、轮询审计和版本闭环。

自动研究闭环层吸收了 Deli_AutoResearch、Scientific Paper Writing Skill Group 和 evo 的公开工作流思想，并转译成轻量 Codex 审计模板。它不会安装 evo，不会修改 Codex hooks，不会加入 telemetry、dashboard 或外部优化运行器。

## 三层模型

- **Goal Compiler**：把模糊想法转成可复制的 `/goal` 合同。
- **Goal Supervisor**：目标授权后执行 preflight audit、Task Card、多 agent/worktree 拆分建议、周期审计、漂移暂停和最终闭环。
- **Efficiency Auditor**：审计运行中或已完成的 Codex 工作，评估能力利用、风险隔离、验证深度和交接质量。

横向控制：

- **Task State Pack**：用持久状态文件承载长任务上下文。
- **Stall/Pivot Rules**：用 stale_count 阻止低证据重复尝试，并要求结构性转向。
- **Experiment Lane**：只有 metric 和 gate 都明确时，才允许多方案实验。
- **Ideator/Verifier Loop**：把候选方向、实现和只读验证分开。

## 适用场景

- 审计一个 Codex thread id 的能力利用率。
- 评估某个项目或 worktree 是否适合升级为多 agent / worktree / Cloud 并行流程。
- 为进行中的 Codex 任务生成最终只读审查 prompt。
- 把模糊需求转换成受边界保护的 `/goal` 合同。
- 在用户授权目标后监督 goal-mode run，而不是创建全局每日自动化。
- 在运行中识别范围漂移、缺失验证、阻塞点和人工决策点。
- 执行受保护的只读最终审计，明确输出 mutation status 和 Git 证据，避免把 Codex UI 文件卡片误判成审计时改文件。
- 为长任务加入 Human Gate、Done Gate、Evidence Bundle、交接矩阵和恢复快照。
- 为长期或自我优化目标加入 Task State Pack、stale-count 转向规则、Experiment Lane preflight 和 Ideator/Verifier prompt。
- 判断任务是否应该使用 subagents、CodeGraph、Browser、GitHub、Cloud 或更强验证链路。
- 为多个项目沉淀统一的 Codex 执行复盘与交接标准。
- 生成 Task Card、多 worktree 编排 prompt、worker/reviewer/auditor/finalizer 回填 prompt。

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

也可以生成目标模式合同：

```text
Use $codex-efficiency-auditor as a Goal Compiler.
把这个请求转换成受边界保护的 Codex /goal 合同：
<request>
```

或监督一个已授权目标：

```text
Use $codex-efficiency-auditor as a goal-mode supervisor.
只读审计当前 run 是否仍符合已授权 /goal 合同，并输出下一条可复制 prompt。
```

也可以执行受保护的只读最终审计：

```text
Use $codex-efficiency-auditor and load references/read-only-audit-guard.md.
对 commit <commit> 执行只读最终审计。
报告 Audit mutation status、Git evidence、UI file card provenance、validation evidence、residual risks 和 verdict。
```

也可以审计实验式目标：

```text
Use $codex-efficiency-auditor and load references/evo-style-experiment-lane.md.
对这个 metric-driven goal 执行只读 Experiment Lane Preflight。
```

也可以为长任务建立状态协议：

```text
Use $codex-efficiency-auditor and load references/task-state-pack-template.md.
为这个已授权 /goal 创建 Task State Pack 提案。
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
- `references/autoresearch-adoption-notes.md`：说明本项目从 AutoResearch、论文写作 skill group 和 evo 采用/拒绝了哪些思想
- `references/read-only-audit-guard.md`：受保护只读审计规则、mutation status、Git 证据和 UI 文件卡片来源判断
- `references/task-state-pack-template.md`：长任务 Codex 目标的持久状态包协议
- `references/stall-and-pivot-rules.md`：stale_count 和结构性转向规则
- `references/evo-style-experiment-lane.md`：metric/gate 实验 lane 的 preflight 和审计规则
- `references/ideator-verifier-loop.md`：候选生成与伪进展验证的角色分工
- `references/report-templates.md`：报告模板与最终审查 prompt
- `references/goal-mode-contract-template.md`：受边界保护的 `/goal` 合同模板
- `references/goal-mode-default-strategy.md`：保守默认值、风险分类、发现优先目标和自动化边界
- `references/goal-mode-audit-prompts.md`：目标启动、开工前审计、周期审计、漂移暂停、人工决策和最终闭环 prompt
- `references/goal-mode-human-gates.md`：push、publish、deploy、破坏性操作、账号变更、凭证、付费服务和对外评论的人类批准/拒绝门禁
- `references/goal-mode-done-gate.md`：围绕合同、范围、证据、暂停扫描和下一任务检查的确定性完成门
- `references/goal-mode-evidence-bundle.md`：命令、产物、截图、CI/PR 状态、扫描、门禁和风险的最终证据索引
- `references/goal-mode-handoff-matrix.md`：worker、reviewer、auditor、finalizer、线程和 worktree 的必要交接字段
- `references/goal-mode-recovery-stale-work.md`：陈旧进展、重复失败、恢复、上下文压缩和漂移状态模板
- `references/task-card-template.md`：受限 worker 任务卡模板
- `references/multi-worktree-orchestration-template.md`：开工前任务拆分与多 worktree 编排模板
- `references/paste-back-prompts.md`：worker、reviewer、auditor、finalizer 回填 prompt
- `scripts/score_audit.py`：评分汇总辅助脚本
- `scripts/lint_goal_mode_contract.py`：目标模式合同校验脚本
- `scripts/lint_task_state_pack.py`：Task State Pack 目录校验脚本
- `scripts/lint_experiment_lane.py`：Experiment Lane 合同校验脚本
- `agents/openai.yaml`：Codex UI 元数据

## 说明

这个 skill 保持轻量设计。它本身不会调用外部服务，也没有额外运行时依赖；可选评分脚本只需要 Python。
