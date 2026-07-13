# Changelog

All notable user-visible changes will be documented here. This project has not yet published a tagged stable release.

## Unreleased

### Added

- Evidence-derived capability scoring for task-relevant Codex capabilities.
- Gap classification: `UNAVAILABLE`, `UNDISCOVERED`, `UNUSED`, `MISUSED`, and `UNVERIFIED`.
- Deterministic before/after comparison for proposed capability upgrades.
- Read-only local capability inventory.
- JSON schema, example fixtures, regression checks, and GitHub Actions CI.
- Bilingual project introduction and 30-second quickstart.
- Public contribution, adoption-reporting, and release-readiness guidance.

## Release Policy

A tagged release should be created from `main` only when:

- CI passes on the release commit;
- the CLI and audit schema changes are documented;
- example fixtures reproduce the documented decisions;
- the README quickstart is current;
- no credential or private environment data is included;
- the release notes distinguish verified behavior from planned work.
