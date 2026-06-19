#!/usr/bin/env python3
"""Read-only Codex plugin/app/skill capability scanner.

This script intentionally avoids auth files and credential stores. It reports
local configuration, plugin cache manifests, plugin definitions, MCP manifests,
and skill names.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


HIGH_RISK_PATTERNS = [
    "github",
    "git-workflow",
    "yeet",
    "browser",
    "chrome",
    "computer",
    "canva",
    "pencil",
    "open-design",
    "automation",
    "security",
    "deploy",
    "publish",
    "release",
    "atlassian",
    "linear",
    "slack",
    "teams",
    "gmail",
    "mail",
    "calendar",
    "drive",
    "notion",
    "lark",
    "account",
    "billing",
    "game-studio",
]

PROJECT_RECOMMENDATIONS = [
    ("GitHub repo", ["github", "git-workflow", "code-review", "codex-security"]),
    ("local development", ["shell", "CodeGraph", "tdd-workflow", "refactoring"]),
    ("UI/browser testing", ["browser-use", "browser:control-in-app-browser", "Chrome/Browser", "Playwright"]),
    ("Figma/design work", ["Canva", "Pencil", "Open Design", "frontend-design", "Figma missing-or-unknown"]),
    ("PR review", ["GitHub", "code-review", "codex-security:security-diff-scan", "project-supervisor"]),
    ("release gate", ["project-supervisor", "codex-security", "GitHub checks", "git-workflow"]),
    ("game development", ["Game Studio", "game-playtest", "three-webgl-game", "sprite-pipeline", "frontend-design", "browser testing"]),
]

GENERAL_PREFERRED = [
    "github",
    "git-workflow",
    "code-review",
    "codex-security",
    "project-supervisor",
    "codegraph",
    "browser",
    "browser-use",
    "frontend-design",
    "imagegen",
    "canva",
    "pencil",
    "open-design",
    "game-studio",
]

GAME_PREFERRED = [
    "game-studio",
    "game-playtest",
    "three-webgl-game",
    "sprite-pipeline",
    "web-game-foundations",
    "phaser-2d-game",
    "react-three-fiber-game",
    "web-3d-asset-pipeline",
]

DESIGN_PREFERRED = [
    "open-design",
    "product-design",
    "canva",
    "pencil",
    "frontend-design",
]

PLUGIN_SKILL_PREFIXES = {
    "game-studio": "game-studio",
    "github": "github",
    "canva": "canva",
    "codex-security": "codex-security",
    "data-analytics": "data-analytics",
    "hyperframes": "hyperframes",
    "documents": "documents",
    "pdf": "pdf",
    "presentations": "presentations",
    "spreadsheets": "spreadsheets",
}

STATUS_DESCRIPTIONS = {
    "enabled": "Explicitly enabled in local config or currently callable.",
    "available-in-session": "Exposed in the current Codex session as a skill, app, or MCP tool.",
    "installed-not-exposed": "Detected locally in config/cache/skills, but current-session callable exposure is not confirmed.",
    "missing-or-unknown": "Not detected locally, or only inferable from project needs.",
}


@dataclass
class Capability:
    name: str
    kind: str
    source: str
    status: str
    confidence: str
    mention: str = ""
    risk: str = "low"
    best_for: str = ""
    definition: str = ""
    plugin: str = ""
    capabilities: list[str] = field(default_factory=list)
    child_mentions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


def _risk_for(name: str) -> str:
    lowered = name.casefold()
    if any(pattern in lowered for pattern in HIGH_RISK_PATTERNS):
        return "high-human-gate"
    return "low"


def _codex_home(raw: str | None) -> Path:
    if raw:
        return Path(raw).expanduser()
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".codex"


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _enabled_plugin_names(config_data: dict[str, Any]) -> set[str]:
    enabled: set[str] = set()
    plugins = config_data.get("plugins", {})
    if not isinstance(plugins, dict):
        return enabled
    for name, value in plugins.items():
        if isinstance(value, dict) and value.get("enabled") is True:
            raw = str(name)
            enabled.add(raw.casefold())
            enabled.add(raw.split("@", 1)[0].casefold())
    return enabled


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    if tomllib is not None:
        try:
            return tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return {}

    # Minimal fallback for [plugins."name"] enabled = true.
    plugins: dict[str, dict[str, Any]] = {}
    current_plugin: str | None = None
    section_re = re.compile(r'^\s*\[plugins\."(?P<name>[^"]+)"\]\s*$')
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    for line in lines:
        match = section_re.match(line)
        if match:
            current_plugin = match.group("name")
            plugins.setdefault(current_plugin, {})
            continue
        if current_plugin and re.match(r"^\s*enabled\s*=\s*true\s*$", line, re.IGNORECASE):
            plugins[current_plugin]["enabled"] = True
    return {"plugins": plugins}


def _redacted_source(path: Path, codex_home: Path) -> str:
    try:
        relative = path.relative_to(codex_home)
        return str(relative).replace("\\", "/")
    except ValueError:
        return path.name


def _add_capability(items: dict[str, Capability], capability: Capability) -> None:
    key = f"{capability.kind}:{capability.name}".casefold()
    existing = items.get(key)
    if existing is None:
        items[key] = capability
        return
    status_rank = {"enabled": 3, "available-in-session": 2, "installed-not-exposed": 1, "missing-or-unknown": 0}
    if status_rank.get(capability.status, 0) > status_rank.get(existing.status, 0):
        existing.status = capability.status
    if capability.evidence:
        existing.evidence.extend(e for e in capability.evidence if e not in existing.evidence)
    if not existing.mention and capability.mention:
        existing.mention = capability.mention
    if capability.child_mentions:
        existing.child_mentions.extend(m for m in capability.child_mentions if m not in existing.child_mentions)
    if capability.capabilities:
        existing.capabilities.extend(c for c in capability.capabilities if c not in existing.capabilities)
    if not existing.definition and capability.definition:
        existing.definition = capability.definition


def _scan_config(codex_home: Path, items: dict[str, Capability], config_data: dict[str, Any]) -> None:
    config_path = codex_home / "config.toml"
    plugins = config_data.get("plugins", {})
    if isinstance(plugins, dict):
        for name, value in plugins.items():
            enabled = isinstance(value, dict) and value.get("enabled") is True
            status = "enabled" if enabled else "installed-not-exposed"
            _add_capability(
                items,
                Capability(
                    name=str(name),
                    kind="plugin",
                    source="config.toml",
                    status=status,
                    confidence="confirmed",
                    risk=_risk_for(str(name)),
                    evidence=["config.toml plugin entry"],
                ),
            )

    mcp_servers = config_data.get("mcp_servers", {})
    if isinstance(mcp_servers, dict):
        for name in mcp_servers:
            _add_capability(
                items,
                Capability(
                    name=str(name),
                    kind="mcp",
                    source="config.toml",
                    status="enabled",
                    confidence="confirmed",
                    mention=f"mcp:{name}",
                    risk=_risk_for(str(name)),
                    evidence=["config.toml mcp server entry"],
                ),
            )


def _plugin_status(plugin_name: str, enabled_plugins: set[str]) -> str:
    return "enabled" if plugin_name.casefold() in enabled_plugins else "installed-not-exposed"


def _plugin_skill_mention(plugin_name: str, skill_name: str) -> str:
    prefix = PLUGIN_SKILL_PREFIXES.get(plugin_name.casefold())
    if prefix:
        return f"${prefix}:{skill_name}"
    return f"${skill_name}"


def _scan_plugin_definition(plugin_manifest: Path, codex_home: Path, enabled_plugins: set[str], items: dict[str, Capability]) -> None:
    data = _safe_json(plugin_manifest)
    plugin_name = str(data.get("name") or plugin_manifest.parent.parent.name)
    interface = data.get("interface", {})
    display_name = ""
    description = str(data.get("description") or "")
    capabilities: list[str] = []
    if isinstance(interface, dict):
        display_name = str(interface.get("displayName") or "")
        description = str(interface.get("longDescription") or interface.get("shortDescription") or description)
        raw_capabilities = interface.get("capabilities", [])
        if isinstance(raw_capabilities, list):
            capabilities = [str(item) for item in raw_capabilities if str(item).strip()]

    skill_mentions: list[str] = []
    skills_dir = plugin_manifest.parent.parent / "skills"
    if skills_dir.is_dir():
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            skill_name = skill_file.parent.name
            skill_mentions.append(_plugin_skill_mention(plugin_name, skill_name))
            _add_capability(
                items,
                Capability(
                    name=skill_name,
                    kind="plugin-skill",
                    source=_redacted_source(skill_file, codex_home),
                    status=_plugin_status(plugin_name, enabled_plugins),
                    confidence="best-effort",
                    mention=_plugin_skill_mention(plugin_name, skill_name),
                    risk=_risk_for(f"{plugin_name} {skill_name}"),
                    best_for=_best_for(f"{plugin_name} {skill_name}"),
                    definition=description,
                    plugin=plugin_name,
                    evidence=["local plugin skill SKILL.md"],
                ),
            )

    _add_capability(
        items,
        Capability(
            name=plugin_name,
            kind="plugin",
            source=_redacted_source(plugin_manifest, codex_home),
            status=_plugin_status(plugin_name, enabled_plugins),
            confidence="best-effort",
            mention=f"@{plugin_name}",
            risk=_risk_for(plugin_name),
            best_for=_best_for(plugin_name),
            definition=description,
            plugin=plugin_name,
            capabilities=capabilities,
            child_mentions=skill_mentions,
            evidence=["local .codex-plugin/plugin.json"],
        ),
    )
    if display_name and display_name != plugin_name:
        _add_capability(
            items,
            Capability(
                name=display_name,
                kind="plugin-alias",
                source=_redacted_source(plugin_manifest, codex_home),
                status=_plugin_status(plugin_name, enabled_plugins),
                confidence="best-effort",
                mention=f"@{plugin_name}",
                risk=_risk_for(plugin_name),
                best_for=_best_for(plugin_name),
                definition=description,
                plugin=plugin_name,
                capabilities=capabilities,
                child_mentions=skill_mentions,
                evidence=["local .codex-plugin/plugin.json displayName"],
            ),
        )


def _scan_plugin_cache(codex_home: Path, items: dict[str, Capability], enabled_plugins: set[str]) -> None:
    cache_dir = codex_home / "plugins" / "cache"
    if not cache_dir.is_dir():
        return

    for plugin_manifest in cache_dir.rglob(".codex-plugin/plugin.json"):
        _scan_plugin_definition(plugin_manifest, codex_home, enabled_plugins, items)

    for app_manifest in cache_dir.rglob(".app.json"):
        data = _safe_json(app_manifest)
        apps = data.get("apps", {})
        if isinstance(apps, dict):
            for name in apps:
                _add_capability(
                    items,
                    Capability(
                        name=str(name),
                        kind="app",
                        source=_redacted_source(app_manifest, codex_home),
                        status="installed-not-exposed",
                        confidence="best-effort",
                        mention=f"@{name}",
                        risk=_risk_for(str(name)),
                        evidence=["local .app.json"],
                    ),
                )

    for mcp_manifest in cache_dir.rglob(".mcp.json"):
        data = _safe_json(mcp_manifest)
        servers = data.get("mcpServers", {})
        if isinstance(servers, dict):
            for name in servers:
                _add_capability(
                    items,
                    Capability(
                        name=str(name),
                        kind="mcp",
                        source=_redacted_source(mcp_manifest, codex_home),
                        status="installed-not-exposed",
                        confidence="best-effort",
                        mention=f"mcp:{name}",
                        risk=_risk_for(str(name)),
                        evidence=["local .mcp.json"],
                    ),
                )


def _frontmatter_name(text: str, fallback: str) -> str:
    match = re.search(r"^name:\s*(?P<name>.+)$", text, flags=re.MULTILINE)
    if not match:
        return fallback
    return match.group("name").strip().strip('"')


def _scan_skills(codex_home: Path, items: dict[str, Capability]) -> None:
    roots = [codex_home / "skills", Path.home() / ".agents" / "skills"]
    for root in roots:
        if not root.is_dir():
            continue
        for skill_file in root.rglob("SKILL.md"):
            if "plugins/cache" in str(skill_file).replace("\\", "/"):
                continue
            try:
                text = skill_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            name = _frontmatter_name(text, skill_file.parent.name)
            _add_capability(
                items,
                Capability(
                    name=name,
                    kind="skill",
                    source="skills",
                    status="installed-not-exposed",
                    confidence="best-effort",
                    mention=f"${name}",
                    risk=_risk_for(name),
                    evidence=["local SKILL.md"],
                ),
            )


def _best_for(name: str) -> str:
    lowered = name.casefold()
    if "game-studio" in lowered:
        return "browser game architecture, prototype planning, gameplay loop, playtesting"
    if "game-playtest" in lowered:
        return "gameplay QA, playtest checklist, interaction and feel validation"
    if "sprite-pipeline" in lowered:
        return "sprite sheets, pixel-art pipeline, asset normalization and previews"
    if "three-webgl" in lowered or "react-three-fiber" in lowered or "web-3d" in lowered:
        return "3D browser game stack, WebGL debugging, asset loading and performance"
    if "phaser" in lowered or "web-game" in lowered or "game-ui" in lowered:
        return "2D browser game foundations, HUD, controls, and UI implementation"
    if "github" in lowered or "gh-" in lowered or "yeet" in lowered:
        return "GitHub repo, PR review, CI, push/release workflow"
    if "security" in lowered:
        return "security review, release gate, diff/scan validation"
    if "browser" in lowered or "chrome" in lowered:
        return "UI/browser testing and visual/runtime validation"
    if "canva" in lowered or "pencil" in lowered or "design" in lowered:
        return "design work, visual iteration, product/design assets"
    if "project-supervisor" in lowered:
        return "acceptance gates, completion reports, release gate"
    if "frontend" in lowered:
        return "frontend UI and game interface implementation"
    if "imagegen" in lowered:
        return "asset generation when visual output is required"
    if "codegraph" in lowered:
        return "structural code navigation and impact review"
    return "project-specific Codex capability"


def _context_text(values: list[str] | None) -> str:
    return " ".join(values or []).casefold()


def _preferred_for_context(context: str) -> list[str]:
    preferred: list[str] = []
    if any(token in context for token in ("game", "godot", "phaser", "three", "webgl", "playable", "interactive")):
        preferred.extend(GAME_PREFERRED)
    if any(token in context for token in ("design", "figma", "open design", "canva", "pencil", "prototype", "visual")):
        preferred.extend(DESIGN_PREFERRED)
    preferred.extend(GENERAL_PREFERRED)

    deduped: list[str] = []
    for token in preferred:
        if token not in deduped:
            deduped.append(token)
    return deduped


def _rank(items: list[Capability], context: str = "") -> list[Capability]:
    preferred = _preferred_for_context(context)

    def score(item: Capability) -> tuple[int, int, str]:
        name = item.name.casefold()
        priority = next((index for index, token in enumerate(preferred) if token in name), len(preferred))
        status_bonus = {"enabled": 0, "available-in-session": 1, "installed-not-exposed": 2, "missing-or-unknown": 3}.get(item.status, 3)
        return (priority, status_bonus, item.name)

    return sorted(items, key=score)


def _family_key(item: Capability) -> str:
    name = item.name.casefold()
    plugin = item.plugin.casefold()
    if plugin:
        return plugin
    for token in (
        "github",
        "codex-security",
        "game-studio",
        "browser",
        "chrome",
        "computer-use",
        "canva",
        "pencil",
        "open-design",
        "codegraph",
        "project-supervisor",
        "frontend-design",
        "imagegen",
    ):
        if token in name:
            return token
    return name


def _compact_ranked(items: list[Capability], context: str = "", limit: int = 8) -> list[Capability]:
    ranked = _rank(items, context)
    grouped: dict[str, Capability] = {}
    for item in ranked:
        key = _family_key(item)
        if key not in grouped:
            grouped[key] = item
            continue
        existing = grouped[key]
        if item.kind in {"plugin", "plugin-alias"} and existing.kind not in {"plugin", "plugin-alias"}:
            item.child_mentions.extend(m for m in existing.child_mentions if m not in item.child_mentions)
            if existing.mention and existing.mention not in item.child_mentions and existing.mention != item.mention:
                item.child_mentions.append(existing.mention)
            grouped[key] = item
            existing = item
        if item.mention and item.mention not in existing.child_mentions and item.mention != existing.mention:
            existing.child_mentions.append(item.mention)
        if item.child_mentions:
            existing.child_mentions.extend(m for m in item.child_mentions if m not in existing.child_mentions and m != existing.mention)
        if item.capabilities:
            existing.capabilities.extend(c for c in item.capabilities if c not in existing.capabilities)
    return list(grouped.values())[:limit]


def _prepare_items(items: list[Capability]) -> list[Capability]:
    for item in items:
        item.best_for = item.best_for or _best_for(item.name)
    return items


def _selected_items(items: list[Capability], full: bool, context: str) -> tuple[list[Capability], list[Capability]]:
    _prepare_items(items)
    ranked = _rank(items, context)
    selected = ranked if full else _compact_ranked(items, context)
    return ranked, selected


def _capability_dict(item: Capability) -> dict[str, Any]:
    mention = item.mention or ""
    extra_mentions = [m for m in item.child_mentions if m != mention]
    return {
        "name": item.name,
        "kind": item.kind,
        "source": item.source,
        "status": item.status,
        "status_description": STATUS_DESCRIPTIONS.get(item.status, ""),
        "confidence": item.confidence,
        "mention": mention,
        "child_mentions": extra_mentions,
        "risk": item.risk,
        "best_for": item.best_for,
        "definition": item.definition,
        "plugin": item.plugin,
        "capabilities": item.capabilities,
        "evidence": item.evidence,
    }


def _json_payload(items: list[Capability], full: bool, context: str) -> dict[str, Any]:
    ranked, selected = _selected_items(items, full, context)
    payload: dict[str, Any] = {
        "scan": "FULL_INVENTORY" if full else "COMPACT",
        "audit_mutation_status": "NO_FILES_MODIFIED_BY_AUDIT",
        "scope": "one-time read-only recommendation",
        "scan_basis": "script-run",
        "context": context or "generic",
        "status_descriptions": STATUS_DESCRIPTIONS,
        "best_capabilities": [_capability_dict(item) for item in selected],
        "project_recommendations": [
            {"context": label, "capabilities": names}
            for label, names in PROJECT_RECOMMENDATIONS
        ],
    }
    if full:
        payload["full_inventory"] = [_capability_dict(item) for item in ranked]
    return payload


def _markdown(items: list[Capability], full: bool, context: str) -> str:
    ranked, selected = _selected_items(items, full, context)

    lines = [
        f"Project Capability Scan: {'FULL_INVENTORY' if full else 'COMPACT'}",
        "Audit mutation status: NO_FILES_MODIFIED_BY_AUDIT",
        "Scope: one-time read-only recommendation",
        f"Scan basis: script-run; context={context or 'generic'}",
        "Status note: `installed-not-exposed` means detected locally, but current-session callable exposure is not confirmed.",
        "",
        "Best capabilities for this project:",
        "| Rank | Capability | Status | Best for | Useful mention | Risk | Notes |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(selected, start=1):
        mention = item.mention or ""
        extra_mentions = [m for m in item.child_mentions if m != mention][:3]
        mention_text = ", ".join([mention, *extra_mentions]).strip(", ")
        notes = f"{item.kind}; {item.confidence}"
        if item.capabilities:
            notes += f"; capabilities={','.join(item.capabilities[:3])}"
        lines.append(f"| {index} | {item.name} | {item.status} | {item.best_for} | `{mention}` | {item.risk} | {notes} |")
        if extra_mentions:
            lines[-1] = lines[-1].replace(f"`{mention}`", f"`{mention_text}`")

    lines.extend(["", "Suggested usage order:"])
    for index, (context, names) in enumerate(PROJECT_RECOMMENDATIONS[:7], start=1):
        lines.append(f"{index}. {context}: {', '.join(names)}")

    lines.extend(
        [
            "",
            "Risk boundaries:",
            "| Capability | Human Gate needed before | Safe read-only use |",
            "|---|---|---|",
            "| GitHub / git-workflow | push, merge, auto-merge, PR/issue comments, release | inspect repo, PR checks, diffs, CI status |",
            "| Browser / Chrome / Computer Use | form submission, purchase, upload, account changes | open pages, screenshot, inspect UI behavior |",
            "| Design tools | publishing, sharing, overwriting remote designs, exports to external systems | inspect design context and recommend workflow |",
            "| Automation | create, update, delete, or wake recurring jobs | suggest bounded automation prompt |",
            "| Security tools | external ticket/comment creation or account changes | local/diff scan recommendations |",
            "",
            "Missing or recommended:",
            "- Figma is `missing-or-unknown` unless a Figma connector/tool is visible in the current session.",
            "- Marketplace-wide uninstalled plugins are `missing-or-unknown` unless Codex exposes a plugin inventory API.",
            "- Local plugin definitions come from `.codex-plugin/plugin.json`; plugin skills come from cached plugin `skills/*/SKILL.md`.",
        ]
    )

    if full:
        lines.extend(
            [
                "",
                "Full inventory:",
                "| Capability | Kind | Status | Confidence | Source |",
                "|---|---|---|---|---|",
            ]
        )
        for item in ranked:
            lines.append(f"| {item.name} | {item.kind} | {item.status} | {item.confidence} | {item.source} |")
        lines.extend(
            [
                "",
                "Plugin definitions:",
                "| Plugin | Definition | Capabilities | Child mentions |",
                "|---|---|---|---|",
            ]
        )
        plugin_defs: dict[str, Capability] = {}
        for item in ranked:
            plugin_name = item.plugin or item.name if item.kind == "plugin" else item.plugin
            if not plugin_name:
                continue
            existing = plugin_defs.get(plugin_name)
            if existing is None or item.kind in {"plugin", "plugin-alias"}:
                if existing is not None:
                    item.child_mentions.extend(m for m in existing.child_mentions if m not in item.child_mentions)
                    item.capabilities.extend(c for c in existing.capabilities if c not in item.capabilities)
                plugin_defs[plugin_name] = item
            else:
                existing.child_mentions.extend(m for m in item.child_mentions if m not in existing.child_mentions)
                if item.mention and item.mention not in existing.child_mentions:
                    existing.child_mentions.append(item.mention)

        for plugin_name, item in plugin_defs.items():
            definition = (item.definition or "").replace("|", "/")[:180]
            capabilities = ", ".join(item.capabilities[:6])
            child_mentions = ", ".join(item.child_mentions[:8])
            lines.append(f"| {plugin_name} | {definition} | {capabilities} | `{child_mentions}` |")
    else:
        lines.extend(["", "Inventory note:", "- Compact mode only. Ask for `full inventory` or complete inventory to list every detected item."])

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Read-only Codex capability scan.")
    parser.add_argument("--codex-home", help="Override Codex home directory. Defaults to CODEX_HOME or ~/.codex.")
    parser.add_argument("--context", action="append", help="Project context hints such as game, GitHub repo, UI testing, design, PR review, release gate.")
    parser.add_argument("--full", action="store_true", help="Print full inventory instead of compact recommendations.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print machine-readable JSON instead of Markdown.")
    args = parser.parse_args(argv[1:])

    codex_home = _codex_home(args.codex_home)
    context = _context_text(args.context)
    items: dict[str, Capability] = {}
    config_data = _load_toml(codex_home / "config.toml")
    enabled_plugins = _enabled_plugin_names(config_data)

    _scan_config(codex_home, items, config_data)
    _scan_plugin_cache(codex_home, items, enabled_plugins)
    _scan_skills(codex_home, items)

    capabilities = list(items.values())
    if args.json_output:
        print(json.dumps(_json_payload(capabilities, args.full, context), ensure_ascii=False, indent=2))
    else:
        print(_markdown(capabilities, args.full, context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
