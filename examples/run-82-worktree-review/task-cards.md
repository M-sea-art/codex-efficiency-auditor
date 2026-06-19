# Run 82: Task Cards

## Worker A: Documentation Update

- Owned paths: `README.md`, `examples/**`
- Forbidden paths: credentials, release config, generated binaries
- Validation: `git diff --check`

## Reviewer: Read-Only Audit

- Do not edit files.
- Check changed files, validation output, and unsupported completion claims.
- Return Decision and required fixes.

## Finalizer: Handoff

- Summarize changed files.
- Include evidence commands.
- Stop before push or release unless a Human Gate is present.
