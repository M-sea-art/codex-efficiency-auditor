#!/usr/bin/env python3
"""Cross-platform validation for repository JSON fixtures and documented decisions."""

from __future__ import annotations

import json
from pathlib import Path

from migrate_audit import migrate_audit
from score_audit import analyze_audit, compare_audits


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict), relative
    return value


def test_json_and_privacy() -> None:
    forbidden = ("C:\\Users\\", "/home/", "auth.json", "SUPER_SECRET_TOKEN")
    for path in [*ROOT.glob("schemas/*.json"), *ROOT.glob("examples/**/*.json")]:
        raw = path.read_text(encoding="utf-8")
        json.loads(raw)
        for marker in forbidden:
            assert marker not in raw, f"private marker {marker!r} in {path.relative_to(ROOT)}"


def test_documented_decisions() -> None:
    for relative in (
        "examples/run-54-single-thread/audit-scores.json",
        "examples/run-82-worktree-review/audit-scores.json",
    ):
        analyze_audit(load(relative))

    isolated = analyze_audit(load("examples/real-world/read-only-state-isolation/audit.json"))
    assert isolated["decision"] == "NO_CAPABILITY_UPGRADE_NEEDED"
    assert isolated["scope_conformance"] == "PASS"

    visual = analyze_audit(load("examples/real-world/visual-proof-human-gate/audit.json"))
    assert visual["decision"] == "NEEDS_HUMAN_DECISION"
    assert {item["gap"] for item in visual["gaps"]} == {"MISUSED", "UNVERIFIED"}

    before = load("examples/real-world/registered-disabled-fresh-process/before.json")
    after = load("examples/real-world/registered-disabled-fresh-process/after.json")
    assert analyze_audit(before)["decision"] == "CAPABILITY_REPLAN_NEEDED"
    assert analyze_audit(after)["decision"] == "NO_CAPABILITY_UPGRADE_NEEDED"
    comparison = compare_audits(before, after)
    assert comparison["capability_upgrade_verification"] == "PROVEN"
    assert comparison["outcome_improvements"] == ["fresh-process-capability-call"]

    migrated = migrate_audit(load("examples/migration/v0.2-audit.json"))
    assert analyze_audit(migrated)["capability_utilization_score"] == 0
    assert migrated["scope_conformance"]["status"] == "UNKNOWN"
    assert migrated["run_evidence"] is None


def main() -> int:
    test_json_and_privacy()
    test_documented_decisions()
    print("repository example and privacy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
