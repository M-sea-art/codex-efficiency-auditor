# Registered, Disabled, Fresh Process

Sanitized workflow fixture proving that registration, enablement, and current-session availability are distinct states.

- `before.json`: expected decision `CAPABILITY_REPLAN_NEEDED`.
- `after.json`: expected decision `NO_CAPABILITY_UPGRADE_NEEDED`.
- before/after comparison: expected verification `PROVEN`.

The comparison is `PROVEN` because the capability gap closes and the declared fresh-process functional outcome changes from `FAIL` to `PASS`; a higher utilization score alone would not be sufficient.

The fixture contains no private project name, thread identifier, user path, credential, or proprietary content.
