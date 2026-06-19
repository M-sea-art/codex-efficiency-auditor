# Read-Only Audit Guard

Use this reference whenever the user asks for a read-only review, final audit, commit audit, PR audit, goal-mode periodic audit, Done Gate, or any prompt that says not to edit files.

## Core Rule

A read-only audit is evidence gathering and reporting only. It must not implement fixes, reformat files, stage changes, commit, push, publish, deploy, delete, reset, or create durable project artifacts unless the user explicitly authorizes that action outside the audit.

## Required Git Checks

When the target is a Git repository and shell access is available, collect a mutation snapshot before reporting the final verdict:

```text
git status --short --branch
git diff --name-status
git diff --cached --name-status
```

For commit or PR audits, also inspect the audited object without changing the worktree:

```text
git show --stat --oneline <commit>
git show --name-status --oneline <commit>
```

If the audit itself is long-running or the agent used any command that might write generated files, collect the status/diff snapshot both before and after those commands.

## Audit Mutation Status

Every read-only audit report must include exactly one mutation status:

```text
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT
Audit mutation status: MUTATION_DETECTED
Audit mutation status: UNKNOWN
```

Use `NO_FILES_MODIFIED_BY_AUDIT` only when the working tree and index evidence supports it, or when the report is based on a transcript that clearly shows no write-capable actions.

Use `MUTATION_DETECTED` when new unstaged, staged, untracked, generated, or deleted files appear during the audit. Do not clean them up unless the user asks. Report the exact files and stop at `NEEDS_FIX` or `BLOCKED`.

Use `UNKNOWN` when the audit target is a transcript, remote page, unavailable repo, missing Git state, or when before/after evidence is incomplete.

## UI File Card Disambiguation

Codex UI may display file cards while a commit, PR, or diff is being reviewed. A file card alone is not proof that the auditor edited the file.

When file cards appear during a read-only audit, explicitly state one of:

```text
Displayed file cards appear to belong to the audited commit/diff, not audit-time mutations.
Displayed file cards match current working-tree changes and need follow-up.
Displayed file card provenance is unknown because Git evidence is unavailable.
```

Prefer repository evidence over UI wording such as "edited" when deciding whether the audit mutated files.

## Bare Verdict Rule

Do not output only `READY_FOR_HUMAN_REVIEW`, `NEEDS_FIX`, or `BLOCKED` unless the user explicitly requested a verdict-only response.

Even when the user asks for a short final audit, include:

```text
Audit mutation status:
Git evidence:
Validation evidence:
Residual risks:
Verdict:
```

## Safe Commands

Prefer read-only commands:

```text
git status --short --branch
git diff --name-status
git diff --cached --name-status
git show --stat --oneline <commit>
git log --oneline -n 5
rg --files
rg -n "<literal>"
```

Commands that may write caches, snapshots, lockfiles, generated files, browser artifacts, or build outputs require a reason and post-command mutation check.

## Stop Behavior

If a read-only audit discovers a needed code or document fix:

1. Do not apply the fix inside the audit.
2. Report the issue with evidence.
3. Output `NEEDS_FIX`.
4. Provide a separate paste-ready implementation prompt if useful.
