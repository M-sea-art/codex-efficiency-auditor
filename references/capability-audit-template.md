# Capability Audit Template

Use this reference only when the user explicitly asks for a one-time project capability scan, such as "Audit my available Codex plugins and app capabilities", "项目插件能力审计", "Codex 能力盘点", or "推荐本项目可用插件".

This is a read-only recommendation mode. It is not part of every Goal Contract, Task Card, periodic audit, or final audit.

## Guardrails

- Do not install, enable, disable, authenticate, publish, push, deploy, create automations, submit forms, comment externally, or mutate files.
- Do not read `auth.json`, secrets, tokens, OAuth material, private email lists, credential stores, or payment data.
- Do not call write-capable plugin actions just to test availability.
- Do not claim a cloud/plugin marketplace item is available unless it is visible in the current session, local cache, or configuration.
- Use compact mode by default. Use full inventory only when the user asks for `full inventory` or `完整清单`.
- If `scripts/audit_codex_capabilities.py` is available, run it before writing the report and pass user/project hints with `--context`. If it cannot be run, state the reason and mark the report `Scan basis: manual-only` or `Scan basis: transcript-only`.

## Evidence Sources

Prefer these sources in order:

1. Current session tools and skills exposed to Codex.
2. Local Codex config plugin entries and MCP server entries.
3. Local plugin definitions such as `.codex-plugin/plugin.json`.
4. Local plugin app/MCP manifests such as `.app.json` and `.mcp.json`.
5. Local plugin skill folders such as `plugins/cache/**/skills/*/SKILL.md`.
6. Local user skill folders and `SKILL.md` frontmatter.
7. User-provided project context.

Status labels:

- `enabled`: explicitly enabled in local config or currently callable.
- `available-in-session`: exposed in the current Codex session as a skill, app, or MCP tool.
- `installed-not-exposed`: present in local cache or skill directory but not clearly exposed in the current session.
- `missing-or-unknown`: not detected locally, or only inferable from project needs.

Inventory scope labels:

- `installed plugin`: detected from `.codex-plugin/plugin.json`.
- `plugin skill`: detected from a cached plugin's `skills/*/SKILL.md`.
- `enabled plugin`: detected from local config or currently callable tools.
- `not installed`: do not claim this from local evidence alone; use `missing-or-unknown` unless a reliable plugin catalog API is available.

Confidence labels:

- `confirmed`: direct evidence from current tools, skills, or config.
- `best-effort`: inferred from local cache, naming, or project context.
- `unknown`: not enough reliable evidence.

Risk labels:

- `low`: read-only local inspection or local-only report generation.
- `medium`: may create files, browser artifacts, designs, generated media, or external drafts.
- `high-human-gate`: can affect external accounts, credentials, repositories, PRs, publishing, deployment, billing, destructive changes, outbound comments, or user-visible remote state.

## Compact Report

```markdown
Project Capability Scan: COMPACT
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | UNKNOWN
Scope: one-time read-only recommendation
Scan basis: script-run | manual-only | transcript-only
Status note: `installed-not-exposed` means detected locally, but current-session callable exposure is not confirmed.

Best capabilities for this project:
| Rank | Capability | Status | Best for | Useful mention | Risk | Notes |
|---:|---|---|---|---|---|---|
| 1 |  | enabled / available-in-session / installed-not-exposed / missing-or-unknown |  | `$skill` or @mention | low / medium / high-human-gate |  |

Suggested usage order:
1. ...
2. ...
3. ...

Risk boundaries:
| Capability | Human Gate needed before | Safe read-only use |
|---|---|---|
|  |  |  |

Missing or recommended:
- ...

Inventory note:
- Compact mode only. Ask for `full inventory` / `完整清单` to list every detected plugin, app, skill, MCP server, plugin definition, and plugin skill.
- Marketplace-wide not-installed plugins are unavailable unless Codex exposes a reliable plugin catalog API.
```

## Full Inventory Report

Use only when requested.

```markdown
Project Capability Scan: FULL_INVENTORY
Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT | UNKNOWN
Scan basis: script-run | manual-only | transcript-only
Status note: `installed-not-exposed` means detected locally, but current-session callable exposure is not confirmed.

Installed plugins:
| Plugin | Source | Status | Confidence |
|---|---|---|---|

Enabled plugins:
| Plugin | Evidence | Risk |
|---|---|---|

Available but disabled or not exposed:
| Capability | Evidence | Recommendation |
|---|---|---|

Available skills and useful mentions:
| Mention | Best for | Risk |
|---|---|---|

MCP/app capabilities:
| Capability | Source | Best for | Risk |
|---|---|---|---|

Plugin definitions:
| Plugin | Definition | Capabilities | Child mentions |
|---|---|---|---|

Project-specific recommendations:
| Context | Recommended capabilities | Reason |
|---|---|---|
```

## Machine-Readable Output

When downstream automation needs structured data, run:

```text
python scripts/audit_codex_capabilities.py --json --context "<project hints>"
```

Use Markdown by default for user-facing reports. Use `--json` only for automation, tests, or follow-on tooling.

## Project Context Recommendations

Use these defaults when the user gives the matching project context:

- GitHub repo: `github:github`, `github:gh-fix-ci`, `github:yeet`, `git-workflow`, `code-review`, `codex-security:security-diff-scan`.
- Local development: shell, CodeGraph, `refactoring`, `tdd-workflow`, project build/test commands.
- UI/browser testing: `browser-use`, `browser:control-in-app-browser`, Chrome/Browser plugin, Playwright or existing browser test tooling.
- Figma/design work: Canva, Pencil, Open Design, `frontend-design`; if Figma is not detected, mark it `missing-or-unknown`.
- PR review: GitHub plugin, `code-review`, `codex-security:security-diff-scan`, `project-supervisor`.
- Release gate: `project-supervisor`, `codex-security:security-scan`, GitHub checks, `git-workflow`.
- Game development: `@game-studio`, `$game-studio:game-studio`, `$game-studio:game-playtest`, `$game-studio:three-webgl-game`, `$game-studio:sprite-pipeline`, `frontend-design`, browser testing, `imagegen`, Three.js workflow, asset validation.

## Domain Plugin Promotion

- If project context includes game, playable, gameplay, Godot, Phaser, Three.js, WebGL, sprite, playtest, level design, or interactive prototype, and Game Studio is detected in the current session, local config, local plugin cache, or cached plugin skills, compact output must include `@game-studio` or a `$game-studio:*` skill in the top 5-8 recommendations.
- If project context includes visual design, product design, Figma, Open Design, Canva, Pencil, prototype, UX, UI, or visual smoke test, compact output must include the strongest detected design capability.
- If project context includes PR review, CI, release gate, GitHub repo, security review, or publish readiness, compact output must include the strongest detected GitHub, code-review, project-supervisor, and security capabilities that are visible locally.
- Do not let duplicate app/MCP/plugin-skill entries push out a domain plugin. Collapse related entries into a capability family and show child mentions in the notes or useful mention column.
- If a domain plugin is detected only in cache, mark it `installed-not-exposed` and still recommend it when the project context clearly matches its domain. Include the Human Gate boundary before write-capable use.

## Risk Boundaries

Always mark these as `high-human-gate`:

- GitHub write actions: push, merge, auto-merge, PR comments, issue comments, repository settings.
- Browser/Chrome/Computer Use actions that submit forms, purchase, post, upload, delete, or change accounts.
- Design tools that publish, share, overwrite, export externally, or edit user-owned remote designs.
- Game Studio write workflows that create or refactor major game architecture, replace engines, introduce large dependencies, or generate asset pipelines.
- Security tools that create external findings, tickets, comments, or account changes.
- Automation tools that create, update, delete, or wake recurring jobs.
- Any credential, OAuth, billing, deployment, release, destructive file operation, or external account change.

Safe recommendation language:

- "Useful for..." is allowed.
- "Use after Human Gate..." is allowed.
- "Installed locally but not exposed in this session" is allowed when evidence supports it.
- "Available in marketplace" is not allowed unless verified by a current source.
- "Not installed" is not allowed unless a reliable plugin catalog was checked; prefer `missing-or-unknown`.
