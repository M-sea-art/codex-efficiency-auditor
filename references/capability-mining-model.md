# Capability Mining Model

Use this reference when producing or validating a structured Codex capability audit.

## Capability Record

Record one entry for every task-relevant capability:

```json
{
  "name": "example capability",
  "relevance": "required",
  "availability": "available",
  "discovered": true,
  "usage": "used",
  "impact": 5,
  "evidence": [
    {
      "kind": "test",
      "status": "PASS",
      "summary": "The targeted regression test exited successfully.",
      "locator": "python scripts/test_score_audit.py"
    }
  ]
}
```

Allowed relevance values:

- `required`: the goal or an acceptance gate depends on it;
- `useful`: it materially improves cost, quality, reliability, or auditability;
- `irrelevant`: it does not materially affect this goal and is excluded from scoring.

Allowed usage values:

- `used`: used correctly for the relevant purpose;
- `unused`: known and available but not used;
- `misused`: invoked with the wrong timing, scope, or method;
- `not_applicable`: unavailable or irrelevant to actual execution.

## Gap Precedence

Assign at most one primary gap per relevant capability in this order:

1. `UNAVAILABLE` when a required or useful capability is confirmed absent.
2. `UNDISCOVERED` when it is available but Codex did not discover it.
3. `UNUSED` when it is available and discovered but not used.
4. `MISUSED` when it was used incorrectly.
5. `UNVERIFIED` when correct use or benefit lacks evidence.

Availability marked `unknown` produces `UNVERIFIED`, not `UNAVAILABLE`.

## Evidence-Derived Utilization

Score only available, task-relevant capabilities:

- correctly used with at least one structured `PASS` evidence item: `1.0`;
- used with no `PASS` evidence: `0.25` and `UNVERIFIED`;
- misused: `0.25`;
- unused: `0.0`.

Weight each capability by:

```text
impact × relevance multiplier
```

Use multiplier `1.0` for `required` and `0.6` for `useful`.

Report unavailable and unknown capabilities as gaps without pretending they measure utilization of an available tool.

## Upgrade Ranking

Rank a proposed upgrade using:

```text
expected leverage = task impact × evidence confidence × reuse value
                    - adoption cost - context cost - risk
```

Keep at most three. Every retained recommendation must include:

- the observed gap;
- the smallest corrective action;
- expected task-level gain;
- a concrete verification check;
- `human_gate: true|false`, plus a reason when true.

The upgrade capability and gap must exactly match a computed gap. A retained Human Gate takes decision precedence and returns `NEEDS_HUMAN_DECISION`.

Before/after verification requires the same v0.2 schema, target type, normalized goal, and immutable `(name, relevance, impact)` declarations. Changing a weight makes the comparison `INCONCLUSIVE` rather than manufacturing improvement.

Return `NO_CAPABILITY_UPGRADE_NEEDED` when there are no material relevant gaps.
