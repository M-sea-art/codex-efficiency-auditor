# Ideator Verifier Loop

Use this when a goal needs multiple possible directions, experiment proposals, or recovery from repeated failure. This is a role protocol, not an execution runtime.

## Roles

`Ideator`:

- proposes candidate directions only
- does not edit files
- does not run experiments
- does not verify already-run results
- records provenance and differentiation from prior attempts

`Worker`:

- implements one approved Task Card or candidate direction
- stays inside owned paths
- runs listed validation
- reports evidence and risks

`Verifier`:

- read-only
- checks false progress, missing gates, skipped validation, scope drift, and result plausibility
- returns pass/warn/fail with findings
- does not propose new work unless asked for a separate remediation prompt

`Finalizer`:

- reconciles worker outputs
- requires Done Gate and Evidence Bundle
- stops at Human Gates

## Ideator Brief Types

Use one brief per ideator:

- `failure_analysis`: group repeated failures and propose a structural fix or avoidance path.
- `literature_or_repo_scan`: use authoritative docs, papers, GitHub repos, or issue evidence to propose candidates.
- `frontier_extrapolation`: deepen a direction that already produced fresh evidence.

## Ideator Output Shape

```json
{
  "brief": "failure_analysis | literature_or_repo_scan | frontier_extrapolation",
  "title": "short candidate label",
  "hypothesis": "specific proposal",
  "based_on_evidence": ["command, file, issue, paper, or prior attempt"],
  "differentiation_from_existing": "why this is not a duplicate",
  "expected_effect": "metric, gate, or evidence expected to change",
  "cost": "small | medium | large",
  "risk": "low | medium | high",
  "human_gate_needed": false
}
```

## Verifier Output Shape

```json
{
  "phase": "pre | post | final",
  "passed": true,
  "verdict": "pass | warn | fail",
  "findings": [
    {
      "category": "scope | gates | metric | validation | evidence | false_progress | reproducibility | human_gate",
      "severity": "block | warn | note",
      "what": "one-line issue",
      "where": "file, command, report, or transcript evidence",
      "fix": "one-line next action"
    }
  ]
}
```

Rules:

- any `block` finding means `passed=false`
- `warn` can proceed only when the risk is named in the final report
- empty findings do not replace validation evidence
- verifier cannot mark public release, deployment, or destructive work approved

## False Progress Patterns

Treat these as blocking:

- metric improved by skipping work or narrowing the benchmark
- gate did not run or is decorative
- result is based on stale artifact or stale cache
- worker reports completion without fresh command, artifact, screenshot, CI, PR, or file evidence
- candidate changed forbidden paths or shared locks
- subjective quality was converted into a fake numeric score without human review

## Paste-Back Pattern

```text
Use $codex-efficiency-auditor and load references/ideator-verifier-loop.md.

Run an Ideator/Verifier split for this goal.

Ideator:
- produce 3 candidate directions: failure_analysis, literature_or_repo_scan, frontier_extrapolation
- do not edit files
- include evidence and differentiation from prior attempts

Verifier:
- audit whether the selected candidate has metric, gate, scope, validation, and human-gate coverage
- return pass/warn/fail with findings

Stop before implementation unless the selected candidate has verifier pass and stays inside the authorized /goal.
```
