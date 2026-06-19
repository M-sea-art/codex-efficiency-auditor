# Goal Mode Human Gates

Use this when an authorized goal approaches an irreversible, external, account-level, public, or trust-sensitive action.

Human gates are explicit wait states. They are not reminders. A goal-mode run must stop at a gate until the user supplies the matching approval token or rejection token.

## Gate Tokens

Use stable token names in artifacts, prompts, and reports:

```text
APPROVED:G1 - <who approved> - <what evidence they reviewed>
REJECTED:G1 - <reason>
```

Do not invent approval. Do not treat silence, confidence, green local checks, or a successful dry run as approval.

## Default Gate Types

| Gate | Guards | Required review evidence |
|---|---|---|
| `G1_PUSH` | pushing commits or branches | `git diff`, commit list, branch, remote target |
| `G2_PUBLISH` | making a repo, package, page, or release public | privacy scan, license, secrets scan, final diff |
| `G3_DEPLOY` | deployment or external runtime change | target environment, config diff, rollback path |
| `G4_ACCOUNT` | external account, billing, credentials, permissions | account target, exact permission or billing impact |
| `G5_DESTRUCTIVE` | delete, reset, migration, overwrite, data mutation | backup, dry-run output, affected paths or records |
| `G6_EXTERNAL_COMMENT` | posting to issue, PR, social, ticket, email, or chat | exact outbound text and destination |

## Prompt Snippet

```text
Human Gate Required

State machine stage: NEEDS_HUMAN_DECISION
Gate: <G1_PUSH | G2_PUBLISH | G3_DEPLOY | G4_ACCOUNT | G5_DESTRUCTIVE | G6_EXTERNAL_COMMENT>
Blocked action: <exact action Codex must not perform yet>
Evidence for review:
- <diff, command output, target, screenshot, dry run, or destination>

To approve, reply exactly:
APPROVED:<gate-id> - <your name or role> - <evidence reviewed>

To reject, reply exactly:
REJECTED:<gate-id> - <reason>

Until an approval token is present, Codex may only continue read-only audit, local validation, or scope-narrowing work.
```

## Auditor Checks

- Did the run stop before the guarded action?
- Is the gate tied to one exact action?
- Is the required evidence concrete enough for the user to review?
- Is the approval token exact and case-stable?
- Does the final report quote the approval or rejection token?
