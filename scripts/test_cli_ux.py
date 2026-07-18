#!/usr/bin/env python3
"""Unified CLI compatibility, recovery, and privacy checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "codexcavator.py"
LEGACY_SCORE = ROOT / "scripts" / "score_audit.py"
LEGACY_COLLECT = ROOT / "scripts" / "collect_run_evidence.py"
LEGACY_MIGRATE = ROOT / "scripts" / "migrate_audit.py"
LEGACY_INVENTORY = ROOT / "scripts" / "audit_codex_capabilities.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=environment,
    )


def test_help_and_success_paths() -> None:
    top = run(str(CLI), "--help")
    assert top.returncode == 0, top.stderr
    for command in ("audit", "compare", "collect", "migrate", "inventory"):
        assert command in top.stdout
        help_result = run(str(CLI), command, "--help")
        assert help_result.returncode == 0, help_result.stderr

    audit_path = "examples/real-world/read-only-state-isolation/audit.json"
    legacy_audit = run(str(LEGACY_SCORE), "--json", audit_path)
    unified_audit = run(str(CLI), "audit", audit_path, "--json")
    expected_audit = (ROOT / "examples" / "compatibility" / "legacy-audit-result.json").read_text(encoding="utf-8")
    assert legacy_audit.returncode == unified_audit.returncode == 0
    assert legacy_audit.stdout == unified_audit.stdout == expected_audit

    before = "examples/real-world/registered-disabled-fresh-process/before.json"
    after = "examples/real-world/registered-disabled-fresh-process/after.json"
    legacy_compare = run(str(LEGACY_SCORE), "--baseline", before, "--json", after)
    unified_compare = run(str(CLI), "compare", "--before", before, "--after", after, "--json")
    expected_compare = (ROOT / "examples" / "compatibility" / "legacy-compare-result.json").read_text(encoding="utf-8")
    assert legacy_compare.returncode == unified_compare.returncode == 0
    assert legacy_compare.stdout == unified_compare.stdout == expected_compare

    rollout = "examples/quickstart/minimal-rollout.jsonl"
    legacy_collect = run(str(LEGACY_COLLECT), "--input", rollout)
    unified_collect = run(str(CLI), "collect", "--input", rollout)
    assert legacy_collect.returncode == unified_collect.returncode == 0
    assert legacy_collect.stdout == unified_collect.stdout
    assert json.loads(unified_collect.stdout)["parse_status"] == "PASS"

    old = "examples/migration/v0.2-audit.json"
    legacy_migrate = run(str(LEGACY_MIGRATE), "--input", old)
    unified_migrate = run(str(CLI), "migrate", "--input", old)
    assert legacy_migrate.returncode == unified_migrate.returncode == 0
    assert legacy_migrate.stdout == unified_migrate.stdout

    with tempfile.TemporaryDirectory() as directory:
        legacy_inventory = run(str(LEGACY_INVENTORY), "--codex-home", directory, "--context", "fixture", "--json")
        unified_inventory = run(str(CLI), "inventory", "--codex-home", directory, "--context", "fixture", "--json")
    assert legacy_inventory.returncode == unified_inventory.returncode == 0
    assert json.loads(legacy_inventory.stdout) == json.loads(unified_inventory.stdout)


def test_human_output_has_one_next_action() -> None:
    audit = run(str(CLI), "audit", "examples/real-world/read-only-state-isolation/audit.json")
    assert audit.returncode == 0
    assert "Warnings:" in audit.stdout
    assert audit.stdout.count("Next action:") == 1
    assert "Run evidence is absent" in audit.stdout

    comparison = run(
        str(CLI),
        "compare",
        "--before",
        "examples/real-world/registered-disabled-fresh-process/before.json",
        "--after",
        "examples/real-world/registered-disabled-fresh-process/after.json",
    )
    assert comparison.returncode == 0
    assert "Improvements:" in comparison.stdout
    assert comparison.stdout.count("Next action:") == 1

    utilization_only = run(
        str(CLI),
        "compare",
        "--before",
        "examples/real-world/registered-disabled-fresh-process/before.json",
        "--after",
        "examples/real-world/registered-disabled-fresh-process/before.json",
    )
    assert utilization_only.returncode == 0
    assert "PROVEN blockers:" in utilization_only.stdout
    assert utilization_only.stdout.count("Next action:") == 1


def _assert_json_error(result: subprocess.CompletedProcess[str], code: str) -> dict[str, object]:
    assert result.returncode == 2
    assert result.stdout == ""
    payload = json.loads(result.stderr)
    assert payload["error"]["code"] == code
    assert payload["error"]["next_action"].startswith("python scripts/codexcavator.py")
    return payload


def test_actionable_private_errors() -> None:
    missing_marker = "PRIVATE_MISSING_PATH_MARKER.json"
    missing = run(str(CLI), "audit", missing_marker, "--json")
    _assert_json_error(missing, "FILE_NOT_FOUND")
    assert missing_marker not in missing.stderr

    old = run(str(CLI), "audit", "examples/migration/v0.2-audit.json", "--json")
    _assert_json_error(old, "V02_MIGRATION_REQUIRED")
    assert "migrate --help" in old.stderr

    secret = "PRIVATE_ERROR_SENTINEL"
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        malformed = root / "private-name.json"
        malformed.write_text('{"goal": "PRIVATE_ERROR_SENTINEL"', encoding="utf-8")
        invalid = root / "invalid.json"
        invalid.write_text(json.dumps({"schema_version": "0.3", "goal": secret}), encoding="utf-8")
        rollout = root / "rollout.jsonl"
        rollout.write_text(json.dumps({"type": "event_msg", "payload": {"type": "future_event", "secret": secret}}), encoding="utf-8")
        session = root / "session.json"
        session.write_text(json.dumps({"capabilities": secret}), encoding="utf-8")

        malformed_result = run(str(CLI), "audit", str(malformed), "--json")
        _assert_json_error(malformed_result, "JSON_INVALID")
        invalid_result = run(str(CLI), "audit", str(invalid), "--json")
        _assert_json_error(invalid_result, "AUDIT_SCHEMA_INVALID")
        rollout_result = run(str(CLI), "collect", "--input", str(rollout))
        assert rollout_result.returncode == 2
        assert rollout_result.stdout == ""
        assert "ERROR [ROLLOUT_PARSE_FAILED]" in rollout_result.stderr
        assert "--allow-partial is diagnostic only" in rollout_result.stderr
        partial = run(str(CLI), "collect", "--input", str(rollout), "--allow-partial")
        assert partial.returncode == 0
        assert json.loads(partial.stdout)["parse_status"] == "PARTIAL"
        inventory = run(str(CLI), "inventory", "--codex-home", str(root), "--session-capabilities", str(session), "--json")
        _assert_json_error(inventory, "AUDIT_SCHEMA_INVALID")

    for result in (malformed_result, invalid_result, rollout_result, partial, inventory):
        assert secret not in result.stdout
        assert secret not in result.stderr
        assert "private-name.json" not in result.stderr


def main() -> int:
    test_help_and_success_paths()
    test_human_output_has_one_next_action()
    test_actionable_private_errors()
    print("unified CLI UX and compatibility checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
