# Task State Pack Template

Use this when a Codex goal is long-running, resumed across threads, delegated across agents, or likely to need periodic audit. A Task State Pack keeps the durable state outside chat history so progress can be audited, resumed, and handed off without relying on conversation memory.

This is a protocol template, not a runtime. Do not create global automation, background daemons, or external services from this reference.

## Directory Shape

```text
ops/tasks/<TASK_ID>/
  task_spec.md
  progress.json
  findings.jsonl
  directions_tried.json
  iteration_log.jsonl
  gates.json
  evidence/
  rollback.md
```

Use a project-appropriate root if `ops/tasks/` conflicts with local conventions. The final Task Card must name the chosen state pack path.

## Required Files

`task_spec.md`:

```markdown
# <TASK_ID>

Goal:
Non-goals:
Allowed paths:
Forbidden paths:
Shared locks:
Metric, if any:
Gates:
Success criteria:
Pause conditions:
Human gates:
Final report:
```

`progress.json`:

```json
{
  "task_id": "TASK_ID",
  "status": "AUTHORIZED_GOAL",
  "iteration": 0,
  "stale_count": 0,
  "last_progress_at": "2026-06-19T00:00:00Z",
  "last_evidence": "initial task spec",
  "last_failure_signature": null,
  "next_safe_action": "run preflight audit"
}
```

Allowed `status` values:

```text
AUTHORIZED_GOAL
PREFLIGHT_AUDIT
TASK_CARD_READY
AUTONOMOUS_WORK
PERIODIC_AUDIT
STALE_PROGRESS
REPEATED_FAILURE
RECOVERY_NEEDED
NEEDS_HUMAN_DECISION
READY_FOR_FINAL_AUDIT
BLOCKED
VERSION_CLOSED
```

`findings.jsonl`:

```jsonl
{"iteration":1,"kind":"evidence","summary":"targeted test passed","source":"pytest tests/test_x.py","status":"PASS"}
```

`directions_tried.json`:

```json
{
  "directions": [
    {
      "id": "D1",
      "hypothesis": "one concrete direction",
      "result": "unknown",
      "evidence": "not tried yet"
    }
  ]
}
```

`iteration_log.jsonl`:

```jsonl
{"iteration":1,"action":"implemented focused change","result":"new evidence","commands":["pytest tests/test_x.py"],"next":"periodic audit"}
```

`gates.json`:

```json
{
  "gates": [
    {
      "id": "G1_LOCAL_TEST",
      "type": "command",
      "command": "pytest tests/test_x.py",
      "pass_condition": "exit code 0",
      "required": true
    }
  ],
  "human_gates": ["G1_PUSH", "G2_PUBLISH"]
}
```

`evidence/`:

Store or reference bounded evidence: command logs, screenshots, exported reports, PR/check URLs, or artifact paths. Avoid secrets, tokens, personal contact data, and large generated files.

`rollback.md`:

```markdown
# Rollback

Branch/worktree cleanup:
Revert strategy:
Generated files to remove:
External state touched:
Human gate status:
```

## Audit Requirements

A valid Task State Pack must:

- name the authorized goal and allowed write scope
- define forbidden paths and shared locks
- keep `progress.json` parseable and current
- keep `stale_count` numeric
- append evidence rather than overwrite history
- list real gates, not decorative checks
- include a rollback path
- preserve human gates for push, publish, deploy, destructive changes, credentials, paid services, account changes, and outbound comments

## Use In Reports

Long-running audit reports should include:

```text
Task State Pack:
- Path:
- Status:
- Iteration:
- stale_count:
- Last evidence:
- Last failure signature:
- Next safe action:
- Gate status:
- Rollback readiness:
```
