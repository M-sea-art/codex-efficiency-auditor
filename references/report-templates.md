# Report Templates

## Thread Audit

```markdown
Codex Capability Utilization: NN/100
Verdict: READY_FOR_HUMAN_REVIEW | NEEDS_FIX | BLOCKED | INTERIM_ONLY
Status: active | idle | completed | unknown
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Summary:
[One or two sentences about what happened and whether it used Codex well.]

Evidence-backed strengths:
- ...

Capability gaps:
- ...

Risks:
- ...

Recommended paste-back prompt:
```text
...
```

Next action:
[Single concrete next step.]
```

## Project Audit

```markdown
Codex Project Efficiency Score: NN/100
Verdict: STRONG | UNDER_LEVERAGED | NEEDS_PROCESS | RISKY

Project state:
- Path:
- Branch:
- Git status:
- PR/CI:
- Existing Codex assets:

Assessment:
- Planning:
- Parallelism:
- Tooling:
- Validation:
- Reporting:

Upgrade plan:
1. ...
2. ...
3. ...
```

## Final Reviewer Prompt

```text
Please act as a read-only Final Reviewer for this Codex run.
Load references/read-only-audit-guard.md.
Do not modify files, stage changes, commit, push, publish, deploy, delete, reset, or continue feature work.

Before the verdict, collect:
- git status --short --branch
- git diff --name-status
- git diff --cached --name-status
- UI file card provenance, if Codex shows changed-file cards

Check:
1. Goal, scope, owned paths, forbidden paths, shared locks, and done criteria.
2. Final Git state: branch, commit, changed files, clean/dirty status.
3. Validation evidence: targeted tests, full tests, audits, CI/PR status.
4. Risk boundaries: generated files, external source boundaries, state ownership, forbidden paths.
5. Missing Codex leverage: subagents, worktree, CodeGraph, Browser, GitHub/PR, Cloud.

Output:
- Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN
- Git evidence
- Codex capability utilization score out of 100
- Evidence-backed strengths and gaps
- Must-fix issues before human review
- Suggested process upgrades
- Verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```

## Read-Only Audit Report

```markdown
Read-Only Audit: READY_FOR_HUMAN_REVIEW | NEEDS_FIX | BLOCKED | UNKNOWN
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Git evidence:
- Branch/status:
- Unstaged diff:
- Staged diff:
- Audited commit/diff:

UI file card provenance:
- Displayed file cards appear to belong to the audited commit/diff, not audit-time mutations.
- Displayed file cards match current working-tree changes and need follow-up.
- Displayed file card provenance is unknown because Git evidence is unavailable.

Validation evidence:
- ...

Blocking issues:
- ...

Residual risks:
- ...

Verdict:
- READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```

## Long-Run State Audit

```markdown
Long-Run State Audit: CONTINUE | STALE_PROGRESS | REPEATED_FAILURE | RECOVERY_NEEDED | SCOPE_DRIFT | BLOCKED
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Task State Pack:
- Path:
- Status:
- Iteration:
- stale_count:
- Last evidence:
- Last failure signature:
- Next safe action:

Scope:
- Authorized /goal:
- Allowed paths:
- Forbidden paths:
- Shared locks:

Stall/Pivot:
- Fresh evidence:
- Directions tried:
- Repeated failure:
- Pivot required:

Gates:
| Gate | Evidence | Status |
|---|---|---|
|  |  | PASS / FAIL / UNKNOWN |

Decision:
- CONTINUE / NEEDS_HUMAN_DECISION / READY_FOR_FINAL_AUDIT / BLOCKED

Next copy-ready prompt:
```text
...
```
```

## Experiment Lane Audit

```markdown
Experiment Lane Audit: EXPERIMENT_LANE_READY | NEEDS_FIX | NOT_SUITABLE | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Contract:
- Objective:
- Metric:
- Direction:
- Baseline:
- Decision rule:

Scope:
- Allowed paths:
- Forbidden paths:
- Shared locks:
- Human gates:

Gate Review:
| Gate | Pass condition | Evidence | Status |
|---|---|---|---|
|  |  |  | PASS / FAIL / UNKNOWN |

False Progress Review:
- Metric-only improvement risk:
- Skipped validation risk:
- Stale artifact/cache risk:
- Subjective metric risk:

Verdict:
- EXPERIMENT_LANE_READY / NEEDS_FIX / NOT_SUITABLE / NEEDS_HUMAN_DECISION
```

## Goal Mode Closure

```markdown
Goal Mode Closure: VERSION_CLOSED | READY_FOR_HUMAN_REVIEW | NEEDS_FIX | NEEDS_HUMAN_DECISION | BLOCKED
State machine stage:
Authorized /goal:
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Done Gate:
- Verdict:
- Missing proof:
- Next-task status:

Evidence Bundle Index:
| Evidence type | Source | Status | Notes |
|---|---|---|---|
| Goal contract |  | PASS / FAIL / UNKNOWN |  |
| Git scope |  | PASS / FAIL / UNKNOWN |  |
| Validation command |  | PASS / FAIL / UNKNOWN |  |
| Runtime/manual check |  | PASS / FAIL / UNKNOWN |  |
| Human gate |  | PASS / FAIL / UNKNOWN |  |
| Risk scan |  | PASS / FAIL / UNKNOWN |  |

Handoffs:
- Workers:
- Reviewers:
- Auditors:
- Finalizer:

Recovery/Stale Work:
- Status:
- Last failure signature:
- Stale evidence:

Risks:
- ...

Next copy-ready prompt:
```text
...
```
```
