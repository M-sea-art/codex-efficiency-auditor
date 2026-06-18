# Goal Mode Default Strategy

Use this when a user asks for goal mode, autonomous progress, automation during a task, multi-agent execution, or a bounded `/goal` prompt.

Reliability comes from conservative defaults, authoritative context discovery, concrete verification, bounded iteration, and hard pause rules for high-risk actions.

## Output Priority

For Chinese users, output in this order:

1. `推荐执行版（中文，可直接复制）`
2. `默认选择理由`
3. `可选调整` when choices materially change cost, risk, ownership, or direction
4. `你可以直接回复`
5. `Goal Draft (English-compatible)` when bilingual handoff is useful

Put the recommended executable goal first. Do not start with a blank template.

## Default-First Rule

When uncertainty is low risk, choose defaults and continue.

Recommended defaults:

- Existing repo: inspect project scripts, docs, CI config, and local rules before editing.
- New app/site/tool: build a local MVP first.
- No deployment request: local runtime validation only.
- No account request: no login, backend account system, cloud sync, paid service, or external account change.
- No test command known: discover scripts, Makefile targets, CI config, or project docs before inventing checks.
- No advanced feature request: implement the smallest complete user-visible workflow.
- No automation request beyond the current goal: do not create daily or global automation.

Always add one short reason:

```text
默认选择理由：先做本地可验证目标，因为它能最快证明核心价值，同时避免账号、发布和外部系统带来的额外风险。
```

## Risk Classification

Low risk:

- local prototypes
- local UI work
- docs
- toy data
- isolated scripts
- non-destructive cleanup
- generated examples

Medium risk:

- existing repo changes
- shared config
- public-facing copy
- development migrations
- browser extensions
- mobile builds
- external APIs with test-only access

High risk:

- credentials
- payments
- production data
- destructive deletion or reset
- public release
- external account ownership or state changes
- legal, medical, or financial judgment
- compliance claims
- privacy-sensitive user data
- copyrighted assets or official authorization claims

Behavior:

- Low risk: output the best copy-ready goal with conservative defaults.
- Medium risk: output defaults plus explicit boundaries, shared locks, verification, and pause conditions.
- High risk: generate a discovery-first goal or ask for a human decision before the risky action.

## Discovery-First Goals

Use discovery-first goals when the domain, project, data semantics, or external requirements are not clear.

Pattern:

```text
/goal 创建一个安全的第一版目标，先读取权威上下文，再实现最小可验证工作流，并把无法确认的领域问题列入最终报告。
验证：识别并读取项目文档、现有脚本、样例数据、运行说明或官方参考资料；运行最小相关检查；用日志、截图、导出文件、命令输出或 PR 状态证明代表性流程。
约束：不编造领域规则、合规声明、数据语义、授权状态或用户承诺；不处理生产数据；不改变未理解的公共合同。
边界：只修改第一版流程直接需要的文件；不触碰生产配置、凭证、发布设置、无关模块或共享锁。
迭代策略：先完成发现阶段并写明工作假设，再实现一个聚焦切片；失败后基于新日志、文档或最小复现调整；最多 3 轮聚焦改进后报告剩余风险。
完成条件：代表性流程在已列明假设下有证据证明可用，检查通过或缺失配置被明确报告，未解决领域问题被列出。
暂停条件：需要外部权限、凭证、付费、生产数据、破坏性操作、公开发布、合规审批、法律/医疗/金融判断或所有权确认时暂停。
轮询审计：仅在该目标被用户授权后附着运行，只读检查进展、漂移、验证缺口、阻塞和下一步 prompt。
人工介入触发：发现权威上下文不足、需要扩大目标、需要改变 forbidden paths、验证无法运行或准备进入发布动作时请求用户决定。
最终报告格式：报告状态机阶段、发现证据、实现证据、验证结果、风险、人工问题和下一条可复制 prompt。
```

## Automation Boundary

Goal-mode automation is not a project starter. It is a goal-attached supervisor.

Allowed:

- read current thread or worktree state
- compare progress against the authorized goal
- detect drift, blockers, missing validation, and stop conditions
- summarize status and generate paste-back prompts
- mark `NEEDS_HUMAN_DECISION`, `READY_FOR_FINAL_AUDIT`, or `BLOCKED`

Not allowed unless the goal explicitly grants it:

- create new goals
- expand scope
- edit files as a worker
- publish, deploy, push, delete, reset, or change account state
- use credentials or paid services
- change forbidden paths or shared locks

## Polling Cadence Defaults

Use the lightest useful cadence:

- 30-120 minute task: current-thread heartbeat every meaningful milestone or roughly every 20-30 minutes.
- Half-day or longer task: suggest goal-scoped cron/worktree automation only after explicit user authorization.
- Any high-risk task: audit before the risky boundary, not after it.

End polling when the goal reaches `VERSION_CLOSED`, `BLOCKED`, or the user stops the project.

## Numbered Adjustments

Ask only when choices materially change risk, cost, ownership, or direction.

```text
可选调整
1. 自治级别：A supervised-autonomous（默认） / B 只读规划 / C 手动逐步确认
2. 执行形态：A 单线程推进（默认） / B 多 agent + Task Cards / C 多 worktree 并行
3. 验证强度：A 最小本地检查（默认） / B 加浏览器或截图验证 / C 加 CI/PR 审计
4. 轮询方式：A 当前线程 heartbeat（默认） / B 目标专属 cron/worktree automation / C 不轮询

你可以直接回复：按默认，或回复类似 1A 2B 3C 4A。
```
