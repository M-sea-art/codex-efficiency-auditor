# Capability Mining Model v0.3

Use this reference when producing or validating a structured codex-efficiency-auditor audit.

## Availability Lifecycle

`available_in_session` is the only state that enters the utilization denominator. `installed_not_exposed`, `disabled`, and `unavailable` remain explicit `UNAVAILABLE` gaps; `unknown` becomes `UNVERIFIED`.

Do not infer current-session exposure from installation, cache, registration, configuration, or a previous process.

## Gap Precedence

Assign at most one primary gap per relevant capability:

1. `UNAVAILABLE`: installed but not exposed, disabled, or confirmed absent.
2. `UNDISCOVERED`: session-available but not found.
3. `UNUSED`: discovered but unused.
4. `MISUSED`: used at the wrong time, scope, or method.
5. `UNVERIFIED`: correct use or availability lacks scoped evidence.

## Operation and Evidence Contracts

Keep operation authority separate from capability scoring. Scope `FAIL` forces replanning; scope `UNKNOWN` blocks proof.

Evidence declares one `claim_scope`. Capability evidence, task outcomes, Human acceptance, authorization, and efficiency are separate claims. A PASS item closes only a matching scope.

## Shortest Safe Route

For each retained upgrade choose the earliest route supported by evidence:

1. `REUSE`
2. `NATIVE`
3. `INSTALLED`
4. `DISCOVER_FIRST`
5. `BUILD`
6. `HUMAN_GATE` when authority is required

Every route includes one `smallest_useful_check`. Do not save time by cutting validation, privacy, security, data-loss prevention, accessibility, Git hygiene, release gates, or Human Gates.

## Outcome-Aware Verification

Before/after verification freezes:

- schema, target type, and normalized goal;
- task mode and authority contract;
- `(name, relevance, impact)` capability declarations;
- outcome IDs, descriptions, required flags, and claim scopes;
- efficiency metric names, directions, and thresholds.

The capability score is diagnostic. `PROVEN` additionally requires either a new outcome PASS or a declared metric improvement, with complete strict run evidence and no regression.

Migrated v0.2 audits keep individual score semantics but remain `INCONCLUSIVE` for comparison until new scope and run evidence is supplied.
