# Report Templates

## Thread Audit

```markdown
Codex Capability Utilization: NN/100
Verdict: READY_FOR_HUMAN_REVIEW | NEEDS_FIX | BLOCKED | INTERIM_ONLY
Status: active | idle | completed | unknown

Summary:
[One or two sentences about what happened and whether it used Codex well.]

Evidence-backed strengths:
- ...

Capability gaps:
- ...

Risks:
- ...

Recommended paste-back prompt:
```text
...
```

Next action:
[Single concrete next step.]
```

## Project Audit

```markdown
Codex Project Efficiency Score: NN/100
Verdict: STRONG | UNDER_LEVERAGED | NEEDS_PROCESS | RISKY

Project state:
- Path:
- Branch:
- Git status:
- PR/CI:
- Existing Codex assets:

Assessment:
- Planning:
- Parallelism:
- Tooling:
- Validation:
- Reporting:

Upgrade plan:
1. ...
2. ...
3. ...
```

## Final Reviewer Prompt

```text
Please act as a read-only Final Reviewer for this Codex run.
Do not modify files or continue feature work unless a blocker makes the run unsafe.

Check:
1. Goal, scope, owned paths, forbidden paths, shared locks, and done criteria.
2. Final Git state: branch, commit, changed files, clean/dirty status.
3. Validation evidence: targeted tests, full tests, audits, CI/PR status.
4. Risk boundaries: generated files, external source boundaries, state ownership, forbidden paths.
5. Missing Codex leverage: subagents, worktree, CodeGraph, Browser, GitHub/PR, Cloud.

Output:
- Codex capability utilization score out of 100
- Evidence-backed strengths and gaps
- Must-fix issues before human review
- Suggested process upgrades
- Verdict: READY_FOR_HUMAN_REVIEW / NEEDS_FIX / BLOCKED
```

