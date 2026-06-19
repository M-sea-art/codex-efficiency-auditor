# Evo-Style Experiment Lane

Use this when a Codex goal asks for measurable optimization, multiple candidate variants, or autonomous self-improvement. This lane borrows the metric/gate discipline of evo without installing evo, modifying hooks, creating telemetry, or running a separate optimization runtime.

## Entry Criteria

A goal may enter Experiment Lane only when all are true:

- there is a concrete metric
- the metric direction is declared as `max` or `min`
- at least one pass/fail gate protects correctness, safety, or scope
- allowed paths, forbidden paths, and shared locks are explicit
- rollback is documented
- human gates are declared for high-risk actions
- the final decision is based on metric plus gates, not metric alone

If any entry criterion is missing, run Experiment Lane Preflight and stop at `NEEDS_FIX`.

## Suitable Tasks

Good candidates:

- test, lint, typecheck, or build pass-rate improvements
- performance work with stable benchmark evidence
- schema, payload, localization, or data validation coverage
- prompt library deduplication with measurable duplication/coverage metrics
- documentation/template completeness with explicit checklist gates
- artifact extraction or report generation with deterministic output checks

Poor candidates:

- visual taste, brand feel, game feel, or subjective quality
- product direction or prioritization
- legal, medical, financial, compliance, or ownership claims
- public release, deployment, repo visibility, or account changes
- tasks where the only signal is "looks good" or "user likes it"
- optimization without a gate

## Minimal Contract

```text
Experiment Lane:
- Objective:
- Metric:
- Direction: max | min
- Baseline:
- Candidate directions:
- Gates:
- Allowed paths:
- Forbidden paths:
- Shared locks:
- Human gates:
- Rollback:
- Decision rule:
```

Decision rule pattern:

```text
Keep a candidate only if it improves the metric and all required gates pass.
Discard or revise a candidate if any required gate fails, even when the metric improves.
Escalate to human review before push, publish, deploy, destructive work, credentials, paid services, account changes, or outbound comments.
```

## Frontier Strategy Lite

For a lightweight Codex workflow, use these non-runtime strategy labels:

- `argmax`: deepen the current best candidate.
- `top_k`: keep the best few candidates in play.
- `epsilon_greedy`: mostly deepen the best candidate but reserve one branch for exploration.
- `pareto_per_task`: keep candidates that improve different task slices, not just aggregate score.

These are planning labels only. Do not imply evo is installed or running.

## Experiment Lane Preflight Prompt

```text
Use $codex-efficiency-auditor and load references/evo-style-experiment-lane.md.

Run a read-only Experiment Lane Preflight.

Report:
- Objective
- Metric and direction
- Baseline evidence
- Required gates
- Allowed paths / forbidden paths / shared locks
- Human gates
- Whether the task is suitable for Experiment Lane
- Missing criteria
- Verdict: EXPERIMENT_LANE_READY / NEEDS_FIX / NOT_SUITABLE / NEEDS_HUMAN_DECISION
```

## Audit Questions

- Did the candidate improve a declared metric?
- Did every required gate pass?
- Was the baseline fresh and comparable?
- Did the task avoid subjective or high-risk optimization?
- Were failed candidates recorded instead of retried blindly?
- Did a verifier audit false progress before final review?
