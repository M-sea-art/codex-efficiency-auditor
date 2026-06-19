# Goal Mode Handoff Matrix

Use this when a goal-mode run has multiple roles, threads, worktrees, reviewers, auditors, or finalizers.

The matrix defines what each role must receive and return. It prevents lost context during handoff and keeps agents from inventing new scope.

## Role Matrix

| From | To | Required fields |
|---|---|---|
| Goal Compiler | Orchestrator | authorized /goal, risk level, allowed paths, forbidden paths, validation evidence, pause conditions |
| Orchestrator | Worker | Task Card, owned paths, forbidden paths, shared locks, validation commands, done criteria, final report format |
| Orchestrator | Reviewer | authorized /goal, diff scope, changed files, validation evidence, known risks, forbidden paths |
| Worker | Finalizer | files changed, commands run, tests passed/failed, evidence, risks, blockers, git status |
| Reviewer | Finalizer | blocking findings, residual risks, missing validation, suggested gate or done verdict |
| Auditor | Main Thread | score, state machine stage, drift status, missing evidence, next copy-ready prompt |
| Finalizer | User | evidence bundle, done gate verdict, human gate needs, final risk review, next action |

## Worker Handoff Template

```text
Worker Handoff:
- Role:
- Authorized /goal:
- Task Card ID:
- Owned paths:
- Forbidden paths:
- Shared locks:
- Files changed:
- Commands run:
- Evidence:
- Tests passed:
- Tests failed:
- Blockers:
- Pause conditions encountered:
- Git status:
- Suggested next prompt:
```

## Reviewer Handoff Template

```text
Reviewer Handoff:
- Review scope:
- Authorized /goal:
- Changed files reviewed:
- Blocking findings:
- Missing validation:
- Scope or shared-lock risks:
- Human gate needs:
- Done Gate recommendation:
- Residual risks:
```

## Finalizer Handoff Template

```text
Finalizer Handoff:
- Integrated workers:
- Conflicts resolved:
- Shared locks touched:
- Final validation:
- Evidence Bundle Index:
- Done Gate verdict:
- Human Gate tokens:
- Final verdict:
- Next prompt:
```

## Invalid Handoffs

- Worker directly to final approval without reviewer or done gate when risky changes exist.
- Reviewer expanding feature scope instead of reporting findings.
- Auditor acting as worker unless the user explicitly authorized execution.
- Finalizer publishing, pushing, deploying, deleting, or changing accounts without a human gate token.
- Any handoff that omits authorized goal, scope, evidence, or risks.
