# Agent Run Smells

Use this reference when a run feels successful from the final diff but weak as an engineering process.

## Planning Smells

- No explicit goal contract.
- No acceptance criteria.
- No stop conditions or pause conditions.
- The run starts implementing before scope and ownership are clear.
- The final answer describes intent but not the authorized boundary.

## Execution Smells

- Everything happened in one long thread with no task card.
- No owned paths, forbidden paths, or shared locks.
- No worktree isolation for independent work.
- Worker, reviewer, and finalizer roles are blurred.
- The run keeps retrying the same approach without fresh evidence.

## Validation Smells

- Tests are claimed but command output is missing.
- Screenshots are treated as proof without behavior or state evidence.
- No reproduction path.
- No CI, targeted test, or manual validation summary.
- Generated assets, TODOs, dummy data, or static UI are counted as completion.

## Audit Smells

- The auditor edits files during a read-only review.
- No mutation status is reported.
- Git status and diff scope are missing.
- UI file cards are treated as proof of audit-time mutation without Git evidence.
- Security, privacy, or credential boundaries are not checked before release.

## Handoff Smells

- No changed-file summary.
- No risk register.
- No next-agent instructions.
- No final handoff.
- The next run cannot resume without rereading the whole transcript.

## Codexcavator Response

When two or more smell categories are present, report:

```text
Decision: GO_WITH_REQUIRED_FIXES | NO_GO | NEEDS_REPLAN
Required evidence before merge/release:
- goal contract
- changed files
- commands run
- validation output
- Git evidence
- known risks
- final handoff
```
