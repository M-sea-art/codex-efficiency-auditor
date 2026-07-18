# Read-Only State Isolation

Sanitized workflow fixture using temporary state, protected-file hashes, and cleanup evidence.

Expected results:

- decision: `NO_CAPABILITY_UPGRADE_NEEDED`;
- audit mutation status: `NO_FILES_MODIFIED_BY_AUDIT`.
- scope conformance: `PASS`, backed by protected-file integrity evidence rather than runtime metadata alone.

The fixture contains only generic goals and reproducible evidence descriptions.
