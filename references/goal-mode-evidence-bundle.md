# Goal Mode Evidence Bundle

Use this when a final report, release-readiness review, public-share review, or long goal handoff needs traceable proof.

An evidence bundle is an index of proof. It does not need to copy every log or artifact into the report, but it must identify what was checked, where the evidence lives, and what remains unverified.

## Bundle Shape

```text
Evidence Bundle:
- Goal ID:
- Authorized /goal summary:
- State machine stage:
- Audit mutation status:
- Commit/branch/worktree:
- Changed files:
- Commands:
- Test/CI evidence:
- Runtime/manual evidence:
- Screenshots or visual artifacts:
- Diff/security/privacy scans:
- Human gate tokens:
- Unverified claims:
- Known risks:
- Next prompt:
```

## Evidence Rules

- Prefer fresh command output, CI status, screenshots, logs, file paths, PR URLs, or artifact paths over prose.
- Label evidence as `PASS`, `FAIL`, `UNKNOWN`, or `NOT_APPLICABLE`.
- Keep private paths, tokens, credentials, and personal contact details out of public-ready bundles.
- Put optional caveats in risks, not in access issues or blockers.
- Treat "not run" as `UNKNOWN`, not `PASS`.
- If a human gate is used, include the exact `APPROVED:Gx` or `REJECTED:Gx` token.

## Final Closure Add-On

```text
Evidence Bundle Index:
| Evidence type | Source | Status | Notes |
|---|---|---|---|
| Goal contract | <thread/report/file> | PASS / FAIL / UNKNOWN | <summary> |
| Audit mutation status | <git status/diff evidence> | PASS / FAIL / UNKNOWN | <NO_FILES_MODIFIED_BY_AUDIT / MUTATION_DETECTED / UNKNOWN> |
| Git scope | <git status/diff> | PASS / FAIL / UNKNOWN | <changed files> |
| Validation command | <command> | PASS / FAIL / UNKNOWN | <result> |
| Runtime/manual check | <screenshot/log/artifact> | PASS / FAIL / UNKNOWN | <result> |
| Human gate | <APPROVED:Gx / REJECTED:Gx> | PASS / FAIL / UNKNOWN | <reviewed evidence> |
| Risk scan | <secret/privacy/license/diff scan> | PASS / FAIL / UNKNOWN | <result> |
```

## Auditor Checks

- Does every explicit goal requirement map to evidence?
- Are stale, missing, or skipped checks labeled honestly?
- Are generated files and artifacts named?
- Are public-share risks separated from private working evidence?
- Is the next prompt based on missing evidence rather than a generic suggestion?
