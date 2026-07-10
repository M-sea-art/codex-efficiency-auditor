#!/usr/bin/env python3
"""Regression checks for the read-only capability scanner."""

from __future__ import annotations

from audit_codex_capabilities import Capability, _compact_ranked, _json_payload, _markdown


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


def test_generic_inventory_prefers_enabled_capability() -> None:
    ranked = _compact_ranked(_sample_items(), "")
    assert ranked[0].name == "GitHub", ranked[0].name


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


def test_json_output_shape() -> None:
    payload = _json_payload(_sample_items(), False, "")
    assert payload["scan"] == "COMPACT"
    assert payload["audit_mutation_status"] == "NO_FILES_MODIFIED_BY_AUDIT"
    assert payload["scan_basis"] == "script-run"
    assert payload["relevant_capabilities"][0]["name"] == "GitHub"
    assert "installed-not-exposed" in payload["status_descriptions"]
    assert "project_recommendations" not in payload


def main() -> int:
    test_generic_inventory_prefers_enabled_capability()
    test_context_ranking_uses_capability_evidence()
    test_json_output_shape()
    print("capability scan regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
