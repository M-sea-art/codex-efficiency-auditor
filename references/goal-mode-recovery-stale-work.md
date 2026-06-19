# Goal Mode Recovery And Stale Work

Use this when a goal-mode run is long, repeatedly failing, context-heavy, interrupted, resumed, compacted, or showing signs of drift.

Recovery is a state decision, not a retry impulse. The supervisor should identify the failure class, preserve evidence, and choose the next safe action.

## Status Labels

| Status | Meaning | Default action |
|---|---|---|
| `CONTINUE` | progress is fresh, scoped, and evidence-backed | continue within current Task Card |
| `STALE_PROGRESS` | activity continues but evidence is old, repeated, or not closer to done | stop and request a new evidence source |
| `REPEATED_FAILURE` | same command, test, or approach failed twice | change strategy or mark blocked |
| `RECOVERY_NEEDED` | context, tool, branch, worktree, or state must be reconstructed | create a recovery snapshot before acting |
| `CONTEXT_OVERFLOW_RISK` | long run may lose goal, constraints, or evidence during compaction | write a compact resume summary |
| `SCOPE_DRIFT` | work no longer matches the authorized /goal | run Scope Drift Stop |
| `BLOCKED` | current access, tools, decisions, or evidence cannot complete the goal | stop and request human input |

## Recovery Snapshot

```text
Recovery Snapshot:
- Authorized /goal:
- Current state machine stage:
- Last known good evidence:
- Current branch/worktree:
- Changed files:
- Commands already run:
- Last failure signature:
- Repeated failures:
- Missing context:
- Forbidden paths/shared locks:
- Next safe action:
```

## Periodic Audit Add-On

```text
Recovery/Stale Work Check:
- Is recent work tied to fresh evidence?
- Has the same failure repeated twice?
- Is the next action based on logs, tests, docs, or a minimal repro?
- Is the goal still visible after compaction/resume?
- Is the run touching stale queued work or an outdated plan?
- Does the run need a recovery snapshot before continuing?

Recovery verdict:
CONTINUE / STALE_PROGRESS / REPEATED_FAILURE / RECOVERY_NEEDED / CONTEXT_OVERFLOW_RISK / SCOPE_DRIFT / BLOCKED
```

## Resume Prompt

```text
Resume this authorized goal from the Recovery Snapshot.

Rules:
- Re-read the authorized /goal before acting.
- Re-check git status and changed files.
- Do not repeat the same failed approach without new evidence.
- Preserve allowed paths, forbidden paths, shared locks, pause conditions, and human gates.
- Run the smallest verification command that proves the next step.

Report:
- What context was restored
- What evidence is still valid
- What evidence is stale or missing
- Next safe action
```

## Auditor Checks

- Did the run identify the failure signature, not just retry?
- Did repeated failure trigger a strategy change or blocker?
- Did compaction/resume preserve the goal contract?
- Did stale queued work get revalidated before execution?
- Did the final report distinguish stale evidence from fresh evidence?
