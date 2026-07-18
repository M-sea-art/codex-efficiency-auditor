# Contributing to Codexcavator

Thank you for helping improve evidence-based capability audits for Codex.

## Good Contributions

- A reproducible audit that reveals an `UNAVAILABLE`, `UNDISCOVERED`, `UNUSED`, `MISUSED`, or `UNVERIFIED` capability.
- A regression fixture for an incorrect score or recommendation.
- A small compatibility improvement for a real Codex workflow.
- Documentation that makes an existing behavior easier to verify.

Please do not submit invented adoption claims, synthetic community activity presented as real usage, credential material, or environment dumps containing private paths or secrets.

## Development Checks

Run from the repository root:

```bash
python -m compileall -q scripts
python scripts/test_capability_scan.py
python scripts/test_score_audit.py
python scripts/test_run_evidence.py
python scripts/test_migrate_audit.py
python scripts/test_examples.py
python scripts/score_audit.py --json examples/run-54-single-thread/audit-scores.json
python scripts/score_audit.py --json examples/run-82-worktree-review/audit-scores.json
git diff --check
```

## Pull Requests

1. Keep the change focused.
2. Describe the observed problem and expected outcome.
3. Add or update a fixture when behavior changes.
4. Record user-visible changes under `Unreleased` in `CHANGELOG.md`.
5. Include the commands and results used for validation.

The maintainer reviews scope, evidence quality, backwards compatibility, and whether the change creates a measurable gain without unnecessary capability expansion.

## Reporting Real-World Use

Use the adoption issue template when Codexcavator helped on a real task. Include only shareable data and enough detail for another maintainer to understand the goal, audit decision, evidence, and outcome.
