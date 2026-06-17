# Multi-Worktree Orchestration Template

Use this when a user asks whether a Codex task should be split across multiple agents, threads, branches, or worktrees.

## Split Decision

Recommend multi-agent or multi-worktree execution only when most of these are true:

- The goal has clear acceptance criteria.
- Work can be separated by module, feature area, or file ownership.
- Each worker can have a distinct validation command.
- Shared files can be locked or assigned to one owner.
- Integration can happen in a predictable order.
- The orchestration overhead is lower than the expected parallelism benefit.

Keep the task single-threaded when:

- The scope is ambiguous.
- The task is mostly an architecture decision.
- Most edits touch the same small set of files.
- Tests are missing or too unreliable to attribute failures.
- The work is small enough to finish faster than the coordination cost.

## Orchestrator Prompt

```text
Act as the Codex orchestrator for this repository.

Do not implement yet.

First:
1. Inspect the repository structure and project rules.
2. Identify the task goal, affected areas, shared files, and risk boundaries.
3. Decide whether this should be single-threaded or split across worktrees/agents.
4. If splitting is worthwhile, create one Task Card per worker with:
   - branch name
   - worktree path
   - owned paths
   - forbidden paths
   - shared locks
   - dependencies
   - validation commands
   - expected final report
5. Identify reviewer and finalizer responsibilities.

Output only the orchestration plan and task cards.
```

## Suggested Roles

- `orchestrator`: plan, split, assign, and integrate.
- `explorer`: read-only codebase or research questions.
- `worker`: implement one bounded task in one branch/worktree.
- `reviewer`: read-only correctness, risk, and regression review.
- `auditor`: evaluate Codex capability utilization and process gaps.
- `finalizer`: merge or reconcile worker outputs, run final validation, prepare PR.

## Default Concurrency

- Read-only explorers: 4-6 when questions are independent.
- Same-repo writers: 2-3 by default, 4 only when ownership is very clear.
- Multi-repo work: one writer per repo plus a finalizer.
- Reviewers/auditors: run after enough evidence exists, or mid-run when drift risk is high.

## Worktree Naming

```text
../<repo>-codex-<task-id>
codex/<task-id>
```

Example:

```text
../app-codex-auth-tests
codex/auth-tests
```

## Integration Order

1. Merge shared-lock or schema tasks first.
2. Merge leaf implementation tasks next.
3. Merge docs/reporting tasks last unless they are needed by reviewers.
4. Run relevant validation after every merge.
5. Run full validation before PR or human review.

## Orchestration Audit Questions

- Did the plan avoid two writers touching the same shared files?
- Did every worker have a clear final report format?
- Did every worker have a validation command or manual acceptance evidence?
- Was there an independent reviewer or auditor for risky changes?
- Was final integration explicitly assigned?

