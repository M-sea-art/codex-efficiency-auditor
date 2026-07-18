#!/usr/bin/env python3
"""Regression checks for deterministic v0.2 to v0.3 migration."""

from __future__ import annotations

import copy

from migrate_audit import migrate_audit
from score_audit import analyze_audit, compare_audits


def _evidence(status: str = "PASS") -> dict[str, str]:
    return {"kind": "test", "status": status, "summary": "legacy evidence"}


def _v02(*, used: bool, human_gate: bool = False) -> dict[str, object]:
    usage = "used" if used else "unused"
    evidence = [_evidence()] if used else []
    upgrades = []
    if not used:
        upgrades = [
            {
                "capability": "tests",
                "gap": "UNUSED",
                "action": "Run tests.",
                "expected_gain": "Close the gap.",
                "verification": "The targeted test passes.",
                "human_gate": human_gate,
                **({"human_gate_reason": "Owner approval required."} if human_gate else {}),
            }
        ]
    return {
        "schema_version": "0.2",
        "audit_id": "legacy-fixture",
        "target_type": "thread",
        "goal": "verify the same task",
        "mutation_status": "NO_FILES_MODIFIED_BY_AUDIT",
        "capabilities": [
            {
                "name": "tests",
                "relevance": "required",
                "availability": "available",
                "discovered": True,
                "usage": usage,
                "impact": 5,
                "evidence": evidence,
            }
        ],
        "upgrades": upgrades,
    }


def test_migration_shape_and_score_parity() -> None:
    migrated_before = migrate_audit(_v02(used=False))
    migrated_after = migrate_audit(_v02(used=True))
    before_result = analyze_audit(migrated_before)
    after_result = analyze_audit(migrated_after)
    assert before_result["capability_utilization_score"] == 0
    assert after_result["capability_utilization_score"] == 100
    assert migrated_before["capabilities"][0]["availability"] == "available_in_session"
    assert migrated_after["capabilities"][0]["evidence"][0]["claim_scope"] == "capability_use"
    assert migrated_before["upgrades"][0]["route"] == "DISCOVER_FIRST"
    assert migrated_before["upgrades"][0]["smallest_useful_check"] == "The targeted test passes."
    comparison = compare_audits(migrated_before, migrated_after)
    assert comparison["capability_upgrade_verification"] == "INCONCLUSIVE"
    assert comparison["score_delta"] == 100


def test_human_gate_route_and_input_preservation() -> None:
    source = _v02(used=False, human_gate=True)
    baseline = copy.deepcopy(source)
    migrated = migrate_audit(source)
    assert source == baseline
    assert migrated["upgrades"][0]["route"] == "HUMAN_GATE"
    assert migrated["upgrades"][0]["human_gate"] is True


def main() -> int:
    test_migration_shape_and_score_parity()
    test_human_gate_route_and_input_preservation()
    print("v0.2 to v0.3 migration regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
