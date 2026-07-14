# Capability Mining Rubric

Score Codex only on capabilities that materially affect the audited goal. Do not reward tool volume or penalize irrelevant capabilities.

## Required Inputs

For each task-relevant capability, record:

- `relevance`: `required`, `useful`, or `irrelevant`;
- `availability`: `available`, `unavailable`, or `unknown`;
- `discovered`: whether Codex found the capability;
- `usage`: `used`, `unused`, `misused`, or `not_applicable`;
- `impact`: integer from 1 to 5;
- `evidence`: v0.2 objects with `kind`, `status`, `summary`, and optional `locator`.

Use `references/capability-mining-model.md` for gap precedence and weighting.

## Evidence Rules

Strong evidence:

- tool calls or commands with output;
- tests, builds, CI, traces, screenshots, or runtime state;
- Git state, diffs, commits, or pull-request checks;
- artifacts with clear provenance;
- comparable before-and-after results.

Weak evidence:

- narrative claims without output;
- a plan that was not executed;
- a tool mentioned but not called;
- a screenshot used to claim behavior it cannot prove;
- an installed capability assumed to be available in the current session.

Classify claims supported only by weak evidence as `UNVERIFIED`. Only an evidence item with `status: PASS` earns full utilization credit; `PARTIAL`, `FAIL`, and `NOT_EVALUATED` remain visible without proving completion.

## Utilization Score

Include only `required` and `useful` capabilities that are confirmed `available`.

Usage value:

- used correctly with at least one `PASS` evidence item: `1.0`;
- used without a `PASS` evidence item: `0.25`;
- misused: `0.25`;
- unused: `0.0`.

Weight:

- `required`: `impact × 1.0`;
- `useful`: `impact × 0.6`;
- `irrelevant`: excluded.

Formula:

```text
score = round(100 × weighted usage value / weighted available capability total)
```

Unavailable and unknown capabilities remain visible as gaps but do not masquerade as utilization of an available capability.

## Decisions

- `NO_CAPABILITY_UPGRADE_NEEDED`: no material gaps and score is at least 90.
- `MINOR_CAPABILITY_GAPS`: score is at least 85, with no required gap.
- `CAPABILITY_UPGRADE_RECOMMENDED`: score is at least 50 and material gaps remain.
- `CAPABILITY_REPLAN_NEEDED`: score is below 50 or a required capability is unavailable.
- `NEEDS_HUMAN_DECISION`: the next action crosses a Human Gate.

## Upgrade Rules

- Recommend at most three upgrades.
- Tie every upgrade to an observed gap.
- Require an exact capability/gap match, a boolean `human_gate`, and a non-empty reason when that gate is true.
- State the smallest corrective action, expected gain, and verification.
- Prefer better use of current Codex capabilities over external additions.
- Return no upgrade when evidence shows the current stack is sufficient.

The deterministic scorer checks the audit declaration and consistency. It is not a substitute for investigating the underlying command, artifact, screenshot, runtime, or human claim.
