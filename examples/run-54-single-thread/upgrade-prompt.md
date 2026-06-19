# Upgrade Prompt

```text
Use $codex-efficiency-auditor as Codexcavator.

Perform a read-only audit of this run.
Do not modify files.

Before any READY_FOR_HUMAN_REVIEW verdict, collect:
- original goal
- changed files
- commands run
- validation output
- git status --short --branch
- git diff --name-status
- known risks
- final handoff

Output:
- score /100
- verdict
- Decision: GO / GO_WITH_MINOR_FIXES / GO_WITH_REQUIRED_FIXES / NO_GO / NEEDS_REPLAN
- evidence-backed strengths
- capability gaps
- required fixes
- next-run upgrade prompt
```
