# Stall And Pivot Rules

Use this when a goal-mode run is repeatedly failing, has stale evidence, loops over similar fixes, or keeps asking for the same missing decision. The rule is simple: repeated activity is not progress unless it creates fresh evidence.

This reference extends `goal-mode-recovery-stale-work.md`.

## Progress Signals

Fresh progress means at least one of these changed since the last audit:

- a required gate moved from `UNKNOWN` or `FAIL` to `PASS`
- a failing command produced a new failure signature
- a new authoritative source clarified the next action
- a changed file moved the run closer to the authorized goal and validation was rerun
- a blocker was narrowed to a human decision, missing credential, missing dependency, or explicit out-of-scope item

Activity without one of those signals is stale.

## stale_count Policy

```text
stale_count = 0: continue within the current Task Card.
stale_count = 1: allow one focused fix if based on fresh logs or docs.
stale_count = 2: pivot; change the evidence source, decomposition, test strategy, or implementation approach.
stale_count = 3: stop implementation and produce a recovery snapshot or docs-only diagnosis.
stale_count >= 4: mark NEEDS_HUMAN_DECISION or BLOCKED.
```

Increment `stale_count` when:

- the same command, test, or approach fails twice with the same signature
- the run reports confidence but no new evidence
- the agent retries with paraphrased prompts instead of new facts
- the next action depends on missing authority or forbidden-path expansion
- validation remains unavailable after one discovery pass

Reset `stale_count` to 0 only after fresh evidence materially changes the path forward.

## Pivot Types

Use a structural pivot, not a cosmetic retry:

- switch from implementation to minimal reproduction
- switch from broad tests to the smallest failing command
- switch from code search to CodeGraph or authoritative docs
- split a shared-scope task into smaller Task Cards
- downgrade to read-only diagnosis when write authority is unclear
- request a Human Gate when the next step touches risk boundaries

## Hard Stops

Stop immediately and report `NEEDS_HUMAN_DECISION` or `BLOCKED` when:

- a forbidden path or shared lock must be changed
- push, publish, deploy, delete, reset, account change, credentials, or paid services are required
- a gate is failing and the agent proposes ignoring it
- an experiment improves a metric while failing a required gate
- the run cannot show fresh validation evidence
- ownership, copyright, legal, medical, or financial judgment is required

## Periodic Audit Add-On

```text
Stall/Pivot Check:
- Recent fresh evidence:
- Repeated failure signature:
- stale_count:
- Directions already tried:
- Proposed pivot:
- Human gate needed:
- Recovery verdict: CONTINUE / STALE_PROGRESS / REPEATED_FAILURE / RECOVERY_NEEDED / SCOPE_DRIFT / BLOCKED
```
