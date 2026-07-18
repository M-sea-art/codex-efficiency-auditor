# Capability Mining Rubric v0.3

Score only Codex capabilities that materially affect the audited goal. Do not reward tool volume or penalize irrelevant capability.

## Required Contract

Declare the task mode, local mutation scope, external-action policy, constraints, Human Gates, scope conformance, audit mutation status, task outcomes, and any efficiency metrics before comparing runs.

`scope_conformance: PASS` requires independent authorization evidence. Run metadata alone cannot prove that project or host state stayed unchanged.

## Capability Record

For each relevant capability record:

- `relevance`: `required`, `useful`, or `irrelevant`;
- `availability`: `available_in_session`, `installed_not_exposed`, `disabled`, `unavailable`, or `unknown`;
- `discovered`: whether Codex found it;
- `usage`: `used`, `unused`, `misused`, or `not_applicable`;
- `impact`: integer from 1 to 5;
- `evidence`: `{kind, status, claim_scope, summary, locator?}` objects.

Only `capability_use + PASS` earns full utilization credit.

## Evidence Boundaries

Strong evidence includes actual tool calls, commands and output, tests, builds, CI, traces, runtime state, Git evidence, scoped artifacts, and comparable before/after results.

Weak evidence includes narrative claims, unexecuted plans, tools that were mentioned but not called, installed capability assumed callable without session proof, screenshots used as functional proof, or Agent-authored Human acceptance.

Evidence scopes are not interchangeable:

- `visual` does not prove `functional`;
- `capability_use` does not prove a task outcome;
- `human_acceptance` requires `kind: human`;
- `authorization` evidence supports scope conformance, not product completion;
- partial or unknown run parsing cannot support `PROVEN`.

## Utilization Score

Score only `available_in_session` capabilities marked `required` or `useful`.

- correct use with scoped PASS evidence: `1.0`;
- use without scoped PASS evidence: `0.25`;
- misuse: `0.25`;
- unused: `0.0`.

Weight is `impact × 1.0` for required and `impact × 0.6` for useful capability.

## Decisions

1. Audit mutation detected or target scope `FAIL` -> `CAPABILITY_REPLAN_NEEDED`.
2. Retained Human Gate -> `NEEDS_HUMAN_DECISION`.
3. Required unavailable capability or score below 50 -> `CAPABILITY_REPLAN_NEEDED`.
4. Score at least 85 with no required gap -> `MINOR_CAPABILITY_GAPS`.
5. Score at least 50 with material gaps -> `CAPABILITY_UPGRADE_RECOMMENDED`.
6. No material gaps and score at least 90 -> `NO_CAPABILITY_UPGRADE_NEEDED`.

Unknown scope remains visible as a warning and blocks before/after `PROVEN`.

## Upgrade Rules

- Recommend at most three upgrades.
- Match every upgrade to an observed capability and exact gap.
- Select one route: `REUSE`, `NATIVE`, `INSTALLED`, `BUILD`, `DISCOVER_FIRST`, or `HUMAN_GATE`.
- State the smallest corrective action, expected gain, and one falsifiable `smallest_useful_check`.
- Prefer current Codex and project capability before external adoption.

## Before/After Proof

Comparable audits preserve schema, target type, normalized goal, operation contract, capability declarations, outcome declarations, and metric thresholds.

Return:

- `PROVEN` only when utilization rises, a real gap closes, and an outcome reaches PASS or a declared metric meets its threshold without regression;
- `UTILIZATION_IMPROVED_OUTCOME_UNPROVEN` when only utilization improves;
- `REGRESSION` for capability, required outcome, metric, scope, or mutation-safety regression;
- `INCONCLUSIVE` for incomparable declarations, unknown scope, or missing/partial run evidence;
- `NO_CHANGE` when comparable evidence shows no effective improvement.

The scorer validates declarations and consistency. It does not independently investigate whether a submitted evidence summary is true.
