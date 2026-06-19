# Project Supervisor Bridge

Use this reference when a Codex goal needs both efficient autonomous progress and evidence-based completion control.

This bridge coordinates `$codex-efficiency-auditor` with `$project-supervisor`. It does not vendor, merge, or replace the `project-supervisor` skill.

`$project-supervisor` is an optional companion skill. If it is not available in the current Codex environment, stop at `NEEDS_HUMAN_DECISION` and ask the user to either install/enable `$project-supervisor` or authorize the built-in fallback: create a minimal acceptance checklist using the acceptance gate prompts in this skill. Do not pretend that `$project-supervisor` ran.

## Division Of Responsibility

| Need | Primary skill | Responsibility |
|---|---|---|
| Goal contract, automation boundary, multi-agent/worktree planning, periodic audit, stale-work recovery | `$codex-efficiency-auditor` | Compile and supervise the authorized goal. |
| Acceptance matrix, Definition of Done, completion report, fake/placeholder detection, milestone gate review | `$project-supervisor` | Decide whether implementation evidence satisfies completion gates. |
| Final readiness | Both | Efficiency auditor checks Codex process and scope; project supervisor checks acceptance evidence. |

## Supervised Autopilot State Machine

```text
Goal Contract
-> Acceptance Gates
-> Task Card
-> Implementation
-> Periodic Audit
-> Completion Report
-> Final Audit
```

State responsibilities:

- `Goal Contract`: `$codex-efficiency-auditor` creates or audits the bounded `/goal`.
- `Acceptance Gates`: `$project-supervisor` initializes or audits acceptance criteria and Definition of Done.
- `Fallback Acceptance Gates`: if `$project-supervisor` is unavailable and the user authorizes fallback, `$codex-efficiency-auditor` may create a minimal acceptance checklist, but must label it as fallback and require human review before completion claims.
- `Task Card`: `$codex-efficiency-auditor` maps the goal and acceptance IDs to owned paths, forbidden paths, validation commands, and human gates.
- `Implementation`: worker agents implement only the authorized milestone or task card.
- `Periodic Audit`: `$codex-efficiency-auditor` checks drift, stale progress, missing validation, and human-gate triggers.
- `Completion Report`: `$project-supervisor` checks acceptance evidence and blocks unsupported completion claims.
- `Final Audit`: `$codex-efficiency-auditor` performs read-only closure with Git evidence, Done Gate, Evidence Bundle, and next prompt.

## AGENTS.md Snippet

```md
## Codex Efficiency + Project Supervision

When a task mentions automation, goal mode, multi-agent orchestration, project acceleration, periodic audit, stale work recovery, final readiness, acceptance gates, completion reports, or fake/placeholder completion, use `$codex-efficiency-auditor` and `$project-supervisor` together.

Default workflow:
Goal Contract -> Acceptance Gates -> Task Card -> Implementation -> Periodic Audit -> Completion Report -> Final Audit.

Rules:
- Automation must start from a bounded Goal Contract.
- Automation must not start globally or daily by default.
- Automation may only attach to a user-authorized goal.
- Any completion claim must be backed by Acceptance Matrix evidence and a Completion Report.
- Screenshots, placeholder data, static UI, TODOs, dummy JSON, comments, generated art, and unconnected buttons do not count as completion.
- Push, publish, deploy, delete, reset, credentials, billing, external account changes, outbound comments, or scope expansion require a Human Gate.
```

## Paste-Ready Autopilot Prompt

```text
Use $codex-efficiency-auditor as Goal Compiler + Goal Supervisor, and use $project-supervisor for acceptance gates and completion evidence.

Goal:
<describe the project objective or automation feature>

Run the supervised autopilot workflow:
1. Create or audit a bounded /goal contract.
2. Create or audit acceptance gates with $project-supervisor. If $project-supervisor is unavailable, stop at NEEDS_HUMAN_DECISION and ask whether to install it or use a fallback acceptance checklist.
3. Create a Task Card with owned paths, forbidden paths, validation commands, and human gates.
4. Implement only the authorized milestone if the scope is clear.
5. Run periodic audit for drift, stale progress, missing verification, and human-gate triggers.
6. Produce a completion report with acceptance IDs and evidence.
7. Run a final read-only Codex efficiency audit.

Stop before push, publish, deploy, destructive changes, credentials, billing, external account changes, outbound comments, or scope expansion.

Output:
- Goal Contract
- Acceptance gate status
- Task Card
- Validation commands
- Completion Report status
- Final audit verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / NEEDS_HUMAN_DECISION / BLOCKED
```

## Bridge Audit Questions

- Does the run have both a Goal Contract and acceptance gates?
- Does every claimed completed behavior map to evidence?
- Did the worker avoid self-approving completion?
- Did screenshots or generated assets get paired with behavior or state evidence?
- Did periodic audit catch scope drift, stale work, and missing validation?
- Did final closure include both Codex capability review and acceptance-gate status?

## Stop Conditions

Stop at `NEEDS_HUMAN_DECISION` when either skill detects:

- scope expansion beyond the authorized goal
- missing acceptance gates for claimed completion
- unsupported completion language
- skipped or unverifiable validation
- push, publish, deploy, destructive work, credentials, billing, external account changes, or outbound comments
