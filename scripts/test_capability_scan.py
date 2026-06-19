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


def test_generic_context_prefers_github() -> None:
    ranked = _compact_ranked(_sample_items(), "")
    assert ranked[0].name == "GitHub", ranked[0].name


def test_game_context_promotes_game_studio() -> None:
    context = "game GitHub repo UI/browser testing release gate"
    ranked = _compact_ranked(_sample_items(), context)
    assert ranked[0].name == "game-studio", ranked[0].name

    markdown = _markdown(_sample_items(), False, context)
    assert "@game-studio" in markdown
    assert "$game-studio:game-playtest" in markdown
    assert "installed-not-exposed" in markdown


def test_json_output_shape() -> None:
    payload = _json_payload(_sample_items(), False, "game")
    assert payload["scan"] == "COMPACT"
    assert payload["audit_mutation_status"] == "NO_FILES_MODIFIED_BY_AUDIT"
    assert payload["scan_basis"] == "script-run"
    assert payload["best_capabilities"][0]["name"] == "game-studio"
    assert "installed-not-exposed" in payload["status_descriptions"]


def main() -> int:
    test_generic_context_prefers_github()
    test_game_context_promotes_game_studio()
    test_json_output_shape()
    print("capability scan regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
