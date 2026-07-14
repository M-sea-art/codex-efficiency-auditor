# Report Templates

## Focused Capability Audit

```markdown
Schema version: 0.2
Codex Capability Utilization: NN/100
Decision: NO_CAPABILITY_UPGRADE_NEEDED | MINOR_CAPABILITY_GAPS | CAPABILITY_UPGRADE_RECOMMENDED | CAPABILITY_REPLAN_NEEDED | NEEDS_HUMAN_DECISION
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | MUTATION_DETECTED | UNKNOWN

Goal:
- ...

Task-relevant capabilities:
| Capability | Relevance | Availability | Usage | Evidence | Gap |
|---|---|---|---|---|---|

Highest-leverage upgrades:
1. Capability:
   - Gap:
   - Smallest action:
   - Expected gain:
   - Verification:
   - Human Gate: true / false
   - Human Gate reason: required when true

Next action:
- ...
```

Keep upgrades to three or fewer. If no material gap exists, omit the upgrade section and return `NO_CAPABILITY_UPGRADE_NEEDED`.

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
```

## Upgrade Verification

```markdown
Capability Upgrade Verification: PROVEN | NOT_PROVEN | REGRESSION | INCONCLUSIVE

Goal and acceptance criteria:
- ...

Before:
- Capability utilization:
- Evidence:

After:
- Capability utilization:
- Evidence:

Decision:
- Retain current stack / retain focused upgrade / reject upgrade / collect more evidence
```

Comparable audits must preserve schema version, target type, normalized goal, and the full `(name, relevance, impact)` declaration set.
