#!/usr/bin/env python3
"""Regression checks for the read-only capability scanner."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from audit_codex_capabilities import (
    Capability,
    _apply_session_capabilities,
    _compact_ranked,
    _json_payload,
    _load_session_capabilities,
    _markdown,
    _risk_for,
    _scan_config,
)


def _sample_items() -> list[Capability]:
    return [
        Capability(
            name="GitHub",
            kind="plugin",
            source="fixture",
            status="enabled",
            confidence="confirmed",
            mention="@github",
            plugin="github",
        ),
        Capability(
            name="game-studio",
            kind="plugin",
            source="fixture",
            status="installed-not-exposed",
            confidence="best-effort",
            mention="@game-studio",
            plugin="game-studio",
            child_mentions=["$game-studio:game-playtest", "$game-studio:three-webgl-game"],
        ),
        Capability(
            name="project-supervisor",
            kind="skill",
            source="fixture",
            status="installed-not-exposed",
            confidence="best-effort",
            mention="$project-supervisor",
        ),
    ]


def test_generic_inventory_prefers_available_session_capability() -> None:
    items = _sample_items()
    items[2].status = "available-in-session"
    ranked = _compact_ranked(items, "")
    assert ranked[0].name == "project-supervisor", ranked[0].name


def test_context_ranking_uses_capability_evidence() -> None:
    items = _sample_items()
    items[1].definition = "browser gameplay playtest interaction testing"
    context = "browser gameplay interaction testing"
    ranked = _compact_ranked(items, context)
    assert ranked[0].name == "game-studio", ranked[0].name

    markdown = _markdown(items, False, context)
    assert "@game-studio" in markdown
    assert "$game-studio:game-playtest" in markdown
    assert "installed-not-exposed" in markdown
    assert "generic install list" in markdown


def test_disabled_mcp_is_not_reported_enabled() -> None:
    items: dict[str, Capability] = {}
    config = {
        "mcp_servers": {
            "disabled_demo": {"enabled": False, "command": "demo"},
            "default_demo": {"command": "demo"},
            "enabled_demo": {"enabled": True, "command": "demo"},
        }
    }
    _scan_config(Path("fixture"), items, config)
    assert items["mcp:disabled_demo"].status == "installed-not-exposed"
    assert items["mcp:default_demo"].status == "enabled"
    assert items["mcp:enabled_demo"].status == "enabled"


def test_session_overlay_promotes_and_adds_explicit_facts() -> None:
    items = {
        "skill:known": Capability(
            name="known", kind="skill", source="skills", status="installed-not-exposed", confidence="best-effort"
        )
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "session.json"
        path.write_text(
            json.dumps(
                {
                    "capabilities": [
                        {"kind": "skill", "name": "known"},
                        {"kind": "mcp", "name": "current-session-only"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        _apply_session_capabilities(items, _load_session_capabilities(path))
    assert items["skill:known"].status == "available-in-session"
    assert items["skill:known"].source == "session-overlay"
    assert items["mcp:current-session-only"].status == "available-in-session"
    assert items["mcp:current-session-only"].source == "session-overlay"


def test_chinese_context_and_human_gate_risk() -> None:
    items = [
        Capability(name="Alpha", kind="skill", source="fixture", status="enabled", confidence="confirmed"),
        Capability(
            name="地图工具",
            kind="skill",
            source="fixture",
            status="installed-not-exposed",
            confidence="confirmed",
            definition="地图导航与路线规划",
        ),
    ]
    ranked = _compact_ranked(items, "地图导航")
    assert ranked[0].name == "地图工具", ranked[0].name
    for phrase in ("发布", "部署", "账号", "凭据", "付费", "删除", "邮件", "日历", "云盘"):
        assert _risk_for(f"执行{phrase}操作") == "high-human-gate", phrase


def test_json_output_shape() -> None:
    payload = _json_payload(_sample_items(), False, "")
    assert payload["scan"] == "COMPACT"
    assert payload["audit_mutation_status"] == "NO_FILES_MODIFIED_BY_AUDIT"
    assert payload["scan_basis"] == "script-run"
    assert payload["relevant_capabilities"][0]["name"] == "GitHub"
    assert "installed-not-exposed" in payload["status_descriptions"]
    assert "project_recommendations" not in payload


def main() -> int:
    test_generic_inventory_prefers_available_session_capability()
    test_context_ranking_uses_capability_evidence()
    test_disabled_mcp_is_not_reported_enabled()
    test_session_overlay_promotes_and_adds_explicit_facts()
    test_chinese_context_and_human_gate_risk()
    test_json_output_shape()
    print("capability scan regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
