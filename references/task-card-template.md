# Task Card Template

Use this when preparing a worker task, auditing whether a worker was properly scoped, or converting an audit finding into a repeatable task card.

## Minimal Task Card

```text
Task ID:
Role: orchestrator | explorer | worker | reviewer | finalizer | auditor
Goal:
Non-goals:

Repo / Worktree:
Base branch or commit:
Branch name:

Owned paths:
Forbidden paths:
Shared locks:
Dependencies:

State pack path:
Metric:
Metric direction: max | min | not_applicable
Gates:
Stale detection:
Pivot rules:
Knowledge writeback:

Expected Codex capabilities:
- CodeGraph:
- Browser:
- GitHub / PR:
- Subagents:
- Cloud:

Validation commands:
Done when:
Expected final report:
Stop conditions:
```

## Ownership Rules

- Assign only one writer to each shared file or shared state surface.
- Treat dependency files, lockfiles, migrations, schemas, generated files, global config, and auth/security code as shared locks unless the task explicitly owns them.
- A worker may read outside owned paths, but should not modify outside owned paths.
- A reviewer or auditor should be read-only unless the user explicitly changes the role.
- Long-running or resumed tasks should name a Task State Pack path and keep state files current.
- Metric-driven tasks must not enter Experiment Lane unless gates, rollback, and human gates are explicit.

## Validation Rules

Every task card should include at least one verification path:

- Targeted tests for the changed behavior.
- Typecheck, lint, or format check when the project uses them.
- Diff or generated-file audit when the task may touch broad surfaces.
- Browser validation for UI behavior.
- GitHub/CI validation for PR-bound work.

If no validation command exists, state the manual acceptance evidence required.

## Stale And Pivot Rules

Every long-running task card should state what counts as fresh progress and when to pivot:

- `stale_count = 1`: one focused retry based on fresh evidence is allowed.
- `stale_count = 2`: change strategy, evidence source, decomposition, or validation approach.
- `stale_count = 3`: stop implementation and produce recovery or diagnosis.
- `stale_count >= 4`: mark `NEEDS_HUMAN_DECISION` or `BLOCKED`.

Do not repeat the same failed command, prompt, or implementation approach without new evidence.

## Experiment Lane Rules

Use Experiment Lane only when the Task Card names:

- metric and direction
- baseline evidence
- pass/fail gates
- allowed paths and forbidden paths
- rollback
- human gates for risky actions

Metric improvement never overrides a failed gate.

## Worker Final Report

Require workers to end with:

```text
Final report:
- Objective:
- Files changed:
- Commands run:
- Tests passed:
- Tests failed:
- Git status:
- State pack status:
- Metric/gate result:
- stale_count:
- Risks:
- Follow-up needed:
```

## Audit Questions

- Was the task small enough for one worker?
- Were owned paths and forbidden paths explicit?
- Did the worker stay inside its scope?
- Were shared locks respected?
- Was validation sufficient for the risk?
- If long-running, was Task State Pack state updated?
- If metric-driven, did all gates pass before treating the metric as improvement?
- Did repeated failure trigger a pivot instead of another retry?
- Is the final report enough for a finalizer to continue?
