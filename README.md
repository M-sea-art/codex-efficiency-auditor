# Codex Efficiency Auditor

A Codex skill for auditing whether a Codex thread, project, worktree, pull request, or agent run is using Codex capabilities effectively.

It helps evaluate planning quality, multi-agent readiness, worktree isolation, CodeGraph usage, GitHub/PR flow, validation depth, reporting quality, and concrete upgrade opportunities.

## Use Cases

- Audit a Codex thread id for capability utilization.
- Review a project or worktree before promoting a Codex workflow.
- Produce a final reviewer prompt for an in-progress Codex run.
- Score whether a task should have used subagents, CodeGraph, Browser, GitHub, Cloud, or stronger validation.
- Standardize Codex run handoffs across projects.

## Install

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

Or clone it directly into the skills directory:

```powershell
git clone https://github.com/M-sea-art/codex-efficiency-auditor.git "$env:USERPROFILE\.codex\skills\codex-efficiency-auditor"
```

## Invoke

Use the skill explicitly:

```text
Use $codex-efficiency-auditor to audit this Codex thread: <thread-id>
```

```text
Use $codex-efficiency-auditor to evaluate this project for Codex capability utilization: <repo-path>
```

## What It Scores

The audit is scored out of 100:

- Goal and scope clarity
- Task decomposition and ownership
- Codex capability utilization
- Context and memory management
- Risk isolation and Git hygiene
- Verification and audit coverage
- Reporting and handoff quality
- Upgrade leverage

Verdict bands:

- `90-100`: exemplary Codex-native execution
- `75-89`: strong execution with clear upgrade opportunities
- `60-74`: useful but under-leveraged Codex run
- `40-59`: mostly single-thread execution with weak auditability
- `<40`: risky, unclear, or not meaningfully auditable

## Output Example

```text
Codex Capability Utilization: 82/100
Verdict: strong execution with clear upgrade opportunities

Evidence-backed strengths:
- Used a dedicated patch workspace.
- Ran targeted tests, full tests, state audit, and version audit.

Capability gaps:
- No explicit Task Card.
- No subagent reviewer.
- CodeGraph MCP was not initialized.

Recommended paste-back prompt:
...
```

## Repository Contents

- `SKILL.md`: core skill instructions
- `references/audit-rubric.md`: scoring rubric
- `references/report-templates.md`: output templates and final reviewer prompts
- `scripts/score_audit.py`: helper for totaling category scores
- `agents/openai.yaml`: Codex UI metadata

## Notes

This skill is intentionally lightweight. It does not call external services by itself and does not require runtime dependencies beyond Python for the optional scoring helper.
