# AutoResearch Adoption Notes

This project references public ideas from Deli_AutoResearch, Scientific Paper Writing Skill Group, and evo. It does not vendor their code, install their runtimes, or act as a wrapper around them.

## Adopted Ideas

From Deli_AutoResearch:

- durable state files instead of relying on chat history
- zero-repeat loop discipline through `stale_count`
- guardian/worker separation
- heartbeat-style periodic audit for long goals
- fresh-session or recovery-summary handoff for context-heavy work

From Scientific Paper Writing Skill Group:

- phase routing
- quality gates before integration
- weakness routing to the responsible role
- independent review driving iteration

From evo:

- metric and gate separation
- experiment worktree isolation as a pattern
- frontier strategy vocabulary
- ideator, worker, verifier, and finalizer separation
- false-progress checks

## Rejected Or Deferred Ideas

Not adopted in this skill:

- installing evo
- modifying Codex hooks
- running autonomous optimization loops without user-authorized goals
- telemetry
- remote sandboxes or provider setup
- dashboard hosting
- automatic push, publish, deploy, merge, delete, or reset

## Safety Interpretation

`codex-efficiency-auditor` should remain a lightweight planning, audit, and prompt-generation skill. It may recommend Task State Packs, Experiment Lane contracts, and verifier prompts. It should not silently become an execution engine.

## Public Attribution Language

Suggested wording:

```text
This project adapts public workflow ideas from Deli_AutoResearch and evo into lightweight Codex audit templates. It does not include or run those projects.
```
