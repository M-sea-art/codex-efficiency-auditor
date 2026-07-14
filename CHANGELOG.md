# Changelog

All notable user-visible changes will be documented here. This project has not yet published a tagged stable release.

## Unreleased

### Changed

- Migrated the pre-release audit contract to strict `schema_version: "0.2"` structured evidence without a legacy string-evidence compatibility layer.
- Required exact upgrade-to-gap matching, explicit Human Gates, and immutable declarations for comparable before/after scoring.
- Distinguished configured, disabled, installed, and explicitly current-session capabilities in the read-only scanner.
- Added Unicode-aware Chinese context ranking and Chinese Human Gate risk terms.

### Fixed

- Disabled MCP servers are no longer reported as enabled.
- Non-PASS claims no longer receive full utilization credit.
- Reweighting a capability can no longer manufacture a `PROVEN` comparison.
- `NEEDS_HUMAN_DECISION` is now reachable through a retained Human Gate.

### Added

- Evidence-derived capability scoring for task-relevant Codex capabilities.
- Gap classification: `UNAVAILABLE`, `UNDISCOVERED`, `UNUSED`, `MISUSED`, and `UNVERIFIED`.
- Deterministic before/after comparison for proposed capability upgrades.
- Read-only local capability inventory.
- JSON schema, example fixtures, regression checks, and GitHub Actions CI.
- Bilingual project introduction and 30-second quickstart.
- Public contribution, adoption-reporting, and release-readiness guidance.
- Three sanitized, reproducible real-world workflow fixtures for disabled registration, read-only state isolation, and screenshot/Human Gate boundaries.

## Release Policy

A tagged release should be created from `main` only when:

- CI passes on the release commit;
- the CLI and audit schema changes are documented;
- example fixtures reproduce the documented decisions;
- the README quickstart is current;
- no credential or private environment data is included;
- the release notes distinguish verified behavior from planned work.
