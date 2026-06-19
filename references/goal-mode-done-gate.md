# Goal Mode Done Gate

Use this when deciding whether a goal-mode run can be marked complete, closed, or ready for human review.

The done gate separates evidence-backed completion from a useful but incomplete run. It is modeled as a deterministic checklist that should be hard to satisfy with prose alone.

Done Gate checks are read-only by default. Load `references/read-only-audit-guard.md` before running one, and include mutation status in the result.

## Done Gate Contract

```text
Done Gate:
- Contract audit: the authorized /goal still matches the work performed.
- Scope check: changed files are inside allowed paths and avoid forbidden paths/shared locks.
- Verification evidence: listed checks, commands, screenshots, logs, artifacts, or PR/CI status are fresh.
- Stop condition: the goal's completion condition is directly proven.
- Pause scan: no unresolved pause condition remains.
- Next-task check: remaining work is either absent, explicitly out of scope, or turned into a new proposed goal.
```

## Verdicts

Use one verdict only:

- `DONE_GATE_PASS`: completion evidence is sufficient and no blocking risk remains.
- `READY_FOR_FINAL_AUDIT`: likely complete, but requires a final read-only auditor pass.
- `NEEDS_FIX`: implementation or validation is incomplete inside the authorized scope.
- `NEEDS_HUMAN_DECISION`: a gate, scope expansion, credential, account, destructive action, public release, or product decision is required.
- `BLOCKED`: progress cannot continue with current access, evidence, tools, or decisions.

## Done Gate Prompt

```text
Use $codex-efficiency-auditor to run a read-only Done Gate for this authorized /goal.
Load references/read-only-audit-guard.md.

Do not implement new work, modify files, stage changes, commit, push, publish, deploy, delete, or reset.

Check:
1. Contract audit: does the work match the authorized /goal?
2. Scope check: are all changed files inside allowed paths and outside forbidden paths/shared locks?
3. Verification evidence: are commands, screenshots, logs, artifacts, PR/CI checks, or manual evidence fresh and named?
4. Stop condition: is the completion condition directly proven?
5. Pause scan: are any credentials, payments, production data, destructive actions, public release, account changes, legal/medical/financial judgments, copyright issues, or ownership questions still open?
6. Next-task check: is there any remaining task that belongs in a new goal?

Output:
- Audit mutation status
- Git evidence
- Done Gate verdict
- Evidence table
- Missing proof
- Risks
- Next copy-ready prompt
```

## Evidence Table Shape

```text
| Requirement | Evidence | Status |
|---|---|---|
| <goal clause> | <command/log/screenshot/artifact/path/PR status> | PASS / FAIL / UNKNOWN |
```

Never mark `DONE_GATE_PASS` from confidence, summaries, or old evidence alone.
