# Capability Upgrade Prompt

```text
Use $codex-efficiency-auditor.

Re-audit this run using the v0.3 evidence loop.

Required evidence:
- the same operation contract and scope-conformance evidence;
- strict metadata-only run evidence from the Codex rollout JSONL;
- the actual test command and output;
- branch, status, and diff evidence;
- the same goal, capability declarations, outcomes, and efficiency thresholds as the baseline audit.

Classify gaps only as UNAVAILABLE, UNDISCOVERED, UNUSED, MISUSED, or UNVERIFIED.
Recommend no more than three upgrades.
Give every upgrade one shortest-safe route and one smallest useful check.
Do not return PROVEN unless a task outcome or declared efficiency metric also improves without regression.
If the current stack is sufficient, return NO_CAPABILITY_UPGRADE_NEEDED.
```
