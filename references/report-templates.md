# Report Templates

## Focused Capability Audit

```markdown
Schema version: 0.3
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN
Scope conformance: PASS | FAIL | UNKNOWN

Goal:
- ...

Operation contract:
- Task mode: answer | plan | diagnose | implement | review | monitor | unknown
- Local mutation scope: none | project | host | unknown
- External actions: forbidden | human_gate | authorized | unknown
- Constraints: ...
- Human Gates: ...

Task-relevant capabilities:
| Capability | Relevance | Availability | Usage | Scoped evidence | Gap |
|---|---|---|---|---|---|

Outcomes and declared efficiency metrics:
- Outcome ID / required / claim scope / status / evidence: ...
- Metric / direction / threshold / observed value: ...

Highest-leverage upgrades:
1. Capability:
   - Gap: UNAVAILABLE | UNDISCOVERED | UNUSED | MISUSED | UNVERIFIED
   - Route: REUSE | NATIVE | INSTALLED | BUILD | DISCOVER_FIRST | HUMAN_GATE
   - Action:
   - Expected gain:
   - smallest_useful_check:
   - Human Gate and reason, when retained:

Warnings:
- ...

Next action:
- ...
```

Use availability `available_in_session`, `installed_not_exposed`, `disabled`, `unavailable`, or `unknown`. Evidence must declare `capability_use`, `functional`, `visual`, `domain`, `integrity`, `human_acceptance`, `authorization`, `efficiency`, or `other` as its claim scope.

Keep upgrades to three or fewer. If no material gap exists, omit the upgrade section and return `NO_CAPABILITY_UPGRADE_NEEDED`. End with exactly one next action.

## Inventory-Only Report

```markdown
Codex Capability Inventory: COMPACT | FULL
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | UNKNOWN
Scan basis: script-run | manual-only | transcript-only

Capabilities most relevant to the supplied context:
| Capability | Status | Evidence | Risk |
|---|---|---|---|

Interpretation:
- Inventory presence does not prove correct use or net benefit.
- Continue to a focused capability audit before recommending adoption.

Next action:
- ...
```

## Upgrade Verification

```markdown
Capability Upgrade Verification: PROVEN | UTILIZATION_IMPROVED_OUTCOME_UNPROVEN | REGRESSION | INCONCLUSIVE | NO_CHANGE

Before and after:
- Capability score and resolved gaps: ...
- Outcome improvements: ...
- Metric improvements or regressions: ...
- Scope, run-evidence, and mutation readiness: ...

PROVEN blockers:
- ...

Next action:
- Retain / revise / reject / collect evidence, then repeat the same comparison.
```

Comparable audits preserve schema version, target type, normalized goal, operation contract, capability declarations, outcome declarations, and efficiency-metric thresholds.
