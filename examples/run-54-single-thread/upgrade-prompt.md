# Capability Upgrade Prompt

```text
Use $codex-efficiency-auditor.

Re-audit this run for task-relevant Codex capability utilization.

Required evidence:
- the actual test command and output;
- branch, status, and diff evidence;
- the same goal and acceptance criteria as the baseline audit.

Classify gaps only as UNAVAILABLE, UNDISCOVERED, UNUSED, MISUSED, or UNVERIFIED.
Recommend no more than three upgrades.
If the current stack is sufficient, return NO_CAPABILITY_UPGRADE_NEEDED.
```
