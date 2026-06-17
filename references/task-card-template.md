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

## Validation Rules

Every task card should include at least one verification path:

- Targeted tests for the changed behavior.
- Typecheck, lint, or format check when the project uses them.
- Diff or generated-file audit when the task may touch broad surfaces.
- Browser validation for UI behavior.
- GitHub/CI validation for PR-bound work.

If no validation command exists, state the manual acceptance evidence required.

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
- Risks:
- Follow-up needed:
```

## Audit Questions

- Was the task small enough for one worker?
- Were owned paths and forbidden paths explicit?
- Did the worker stay inside its scope?
- Were shared locks respected?
- Was validation sufficient for the risk?
- Is the final report enough for a finalizer to continue?

