# Capability Mining Smells

Use this reference when a Codex run appears successful but may have left relevant capability unused or unverified.

## Orientation Smells

- The goal or acceptance criteria are missing.
- The audit lists tools before identifying task needs.
- Irrelevant capabilities are treated as mandatory.

## Discovery Smells

- Codex searches manually while a relevant exposed capability is visible.
- Project rules, existing commands, Skills, Plugins, or MCP servers are not inspected.
- Installed capability is assumed to be callable without session evidence.
- A missing capability is claimed without checking the current stack.

## Usage Smells

- A relevant, discovered capability is not used and no reason is given.
- A tool is invoked after the decision it should have informed.
- The wrong scope, target, or mode is used.
- More tools are invoked without improving the task result.

## Evidence Smells

- Tool use is claimed without a tool call or output.
- Tests are claimed without command results.
- Screenshots are used to prove behavior they cannot establish.
- Plans, generated assets, TODOs, or static placeholders are counted as completion.
- Before-and-after comparisons change the goal or capability set.

## Upgrade Smells

- More than three upgrades are recommended.
- A recommendation is not tied to an observed gap.
- An external dependency is preferred without net-gain evidence.
- The current Codex stack is sufficient, but an upgrade is still forced.
- Verification is missing or cannot falsify the recommendation.

## codex-efficiency-auditor Response

Classify each material issue as `UNAVAILABLE`, `UNDISCOVERED`, `UNUSED`, `MISUSED`, or `UNVERIFIED`. Score only task-relevant capabilities, recommend at most three upgrades, and return one of:

```text
NO_CAPABILITY_UPGRADE_NEEDED
MINOR_CAPABILITY_GAPS
CAPABILITY_UPGRADE_RECOMMENDED
CAPABILITY_REPLAN_NEEDED
NEEDS_HUMAN_DECISION
```
