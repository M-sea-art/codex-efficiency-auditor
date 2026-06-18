# Goal Mode Contract Template

Use this when converting a user idea, project request, or automation proposal into a bounded Codex goal-mode contract.

The executable command prefix must be `/goal`. For Chinese users, keep the body in Chinese by default. Do not use `/目标` unless the current client explicitly documents that alias.

## Recommended Chinese Contract

```text
推荐执行版（中文，可直接复制）

/goal <把用户意图改写成一个具体、可验证、可停止的目标结果>。

验证：<列出命令、日志、截图、浏览器检查、CI、文件产物、PR 状态或其他能证明完成的证据；如果命令未知，先读取项目脚本、文档和 CI 配置再选择最小相关检查>。
约束：<列出不得改变的行为、公开接口、数据结构、风格、分支规则、账号状态、发布状态或外部系统>。
边界：<列出允许写入路径、禁止路径、共享锁、只读区域，以及是否允许创建 worktree 或分支>。
迭代策略：<一次做一个聚焦改动，每次有意义改动后重跑相关检查；同一问题连续失败 2 次后必须换证据来源；默认最多 3 轮聚焦改进后报告剩余风险>。
完成条件：<列出哪些证据出现后必须停止，例如检查通过、核心流程跑通、截图无重叠、PR 检查通过或缺失配置被明确报告>。
暂停条件：<需要凭证、付费、生产数据、破坏性操作、公开发布、外部账号变更、法律/医疗/金融判断、版权素材、所有权不清或范围扩张时暂停>。
轮询审计：<仅在用户授权此目标后启用；短中任务使用当前线程 heartbeat，长任务可建议目标专属 cron/worktree automation；职责只限只读审计、总结、漂移检测、阻塞识别和下一步 prompt>。
人工介入触发：<列出必须请用户决定的事件，例如修改 forbidden paths、扩大目标、失败证据不足、验证无法运行、需要外部权限或准备发布>。
最终报告格式：<要求报告状态机阶段、目标完成证据、文件变更、命令结果、验证缺口、风险、是否 READY_FOR_FINAL_AUDIT / NEEDS_HUMAN_DECISION / BLOCKED，以及下一条可复制 prompt>。
```

## English-Compatible Mirror

Use this only when the user asks for English, when a bilingual handoff is useful, or when the output will be pasted into an English-heavy toolchain.

```text
Goal Draft (English-compatible)

/goal <Rewrite the user intent as one concrete, verifiable, stoppable outcome>.

Verification: <commands, logs, screenshots, browser checks, CI, artifacts, PR status, or other completion evidence; if commands are unknown, inspect project scripts, docs, and CI config before choosing the smallest relevant checks>.
Constraints: <behaviors, public interfaces, data shapes, style, branch rules, account state, release state, or external systems that must not change>.
Boundaries: <allowed write paths, forbidden paths, shared locks, read-only areas, and whether worktrees or branches may be created>.
Iteration policy: <make one focused change at a time, rerun checks after meaningful changes, switch evidence source after the same issue fails twice, and default to at most 3 focused improvement rounds before reporting residual risk>.
Stop when: <evidence that proves completion, such as checks passing, core workflow proven, screenshots clean, PR checks passing, or missing configuration explicitly reported>.
Pause if: <credentials, payments, production data, destructive actions, public release, external account changes, legal/medical/financial judgment, copyrighted assets, unclear ownership, or scope expansion is required>.
Polling audit: <enabled only after the user authorizes this goal; use current-thread heartbeat for short or medium tasks, suggest goal-scoped cron/worktree automation only for long tasks, and keep duties read-only: audit, summarize, detect drift, identify blockers, and generate the next prompt>.
Human intervention triggers: <events requiring user decisions, such as forbidden-path changes, scope expansion, insufficient evidence, unavailable validation, external permissions, or release readiness>.
Final report format: <state machine stage, completion evidence, changed files, command results, validation gaps, risks, READY_FOR_FINAL_AUDIT / NEEDS_HUMAN_DECISION / BLOCKED, and the next copy-ready prompt>.
```

## State Machine

```text
AUTHORIZED_GOAL
-> PREFLIGHT_AUDIT
-> TASK_CARD_READY
-> AUTONOMOUS_WORK
-> PERIODIC_AUDIT
-> NEEDS_HUMAN_DECISION | READY_FOR_FINAL_AUDIT | BLOCKED
-> FINAL_REVIEW
-> VERSION_CLOSED
```

## Contract Quality Bar

A goal-mode contract is acceptable only when it:

- starts with `/goal`
- defines a concrete outcome rather than an activity
- names verification evidence
- protects unrelated behavior and external state
- defines allowed writes and forbidden paths
- uses bounded iteration
- defines both completion and pause conditions
- defines the polling audit role without granting implementation authority
- says when a human must intervene
- specifies the final report shape

Revise the contract before execution if any of these are missing.
