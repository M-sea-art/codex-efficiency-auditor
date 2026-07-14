# Capability Audit Template

Use this template for a focused Codex capability audit. Load `references/capability-mining-model.md` and `references/read-only-audit-guard.md` first.

## Guardrails

- Inspect only capabilities relevant to the stated goal.
- Do not equate installed with available, available with used, or used with effective.
- Do not install, authenticate, publish, push, deploy, comment externally, or mutate files during a read-only audit.
- Do not read credentials, tokens, OAuth material, billing data, or unrelated private content.
- Recommend no more than three upgrades.
- Return `NO_CAPABILITY_UPGRADE_NEEDED` when no material gap is supported by evidence.

## Evidence Order

1. Current-session tools and actual tool calls.
2. Target goal, acceptance criteria, and project rules.
3. Commands, logs, tests, traces, screenshots, artifacts, and Git evidence.
4. Local Codex config, plugin definitions, MCP manifests, and Skill metadata.
5. Narrative claims, marked unverified unless corroborated.

## Focused Report

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
|  | required / useful | available / unavailable / unknown | used / unused / misused / not_applicable |  | UNAVAILABLE / UNDISCOVERED / UNUSED / MISUSED / UNVERIFIED / none |

Highest-leverage upgrades:
1. Capability:
   - Gap:
   - Action:
   - Expected gain:
   - Verification:
   - Human Gate: true / false
   - Human Gate reason: required when true

Next action:
- ...
```

## Inventory Support

When local access is available, run:

```text
python scripts/audit_codex_capabilities.py --context "<goal and constraints>" --json
```

Treat its output as inventory evidence only. The inventory does not prove relevance, correct use, or benefit.

Use `--full` only when the user explicitly asks for a complete inventory.

## Machine-Readable Audit

Create JSON conforming to `schemas/audit-report.schema.json`, then run:

```text
python scripts/score_audit.py --json <audit.json>
```

Every evidence item must contain `kind`, `status`, and a non-empty `summary`; use `locator` for a relative path, command, public URL, or other reproducible location. Do not use a bare string claim as evidence.
