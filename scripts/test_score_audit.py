#!/usr/bin/env python3
"""Regression checks for the Codexcavator v0.2 audit contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from score_audit import (
    AVAILABILITY_TYPES,
    CAPABILITY_REQUIRED,
    EVIDENCE_KINDS,
    EVIDENCE_REQUIRED,
    EVIDENCE_STATUSES,
    GAP_TYPES,
    MUTATION_STATUSES,
    RELEVANCE_MULTIPLIER,
    SCHEMA_VERSION,
    TARGET_TYPES,
    TOP_LEVEL_REQUIRED,
    UPGRADE_REQUIRED,
    USAGE_TYPES,
    analyze_audit,
    classify_gap,
    compare_audits,
)


ROOT = Path(__file__).resolve().parents[1]


def evidence(status: str = "PASS", *, kind: str = "test", summary: str = "verified result") -> dict[str, str]:
    return {"kind": kind, "status": status, "summary": summary}


def capability(name: str, **overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": name,
        "relevance": "required",
        "availability": "available",
        "discovered": True,
        "usage": "used",
        "impact": 5,
        "evidence": [evidence()],
    }
    item.update(overrides)
    return item


def audit(capabilities: list[dict[str, object]], upgrades: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_id": "fixture-audit",
        "target_type": "thread",
        "goal": "verify the same task",
        "mutation_status": "NO_FILES_MODIFIED_BY_AUDIT",
        "capabilities": capabilities,
        "upgrades": upgrades or [],
    }


def upgrade(name: str, gap: str, *, human_gate: bool = False) -> dict[str, object]:
    item: dict[str, object] = {
        "capability": name,
        "gap": gap,
        "action": "Use the capability correctly.",
        "expected_gain": "Close the measured gap.",
        "verification": "Repeat the same path and collect PASS evidence.",
        "human_gate": human_gate,
    }
    if human_gate:
        item["human_gate_reason"] = "Owner acceptance cannot be automated."
    return item


def expect_invalid(data: dict[str, object], message: str) -> None:
    try:
        analyze_audit(data)
    except ValueError as error:
        assert message in str(error), str(error)
    else:
        raise AssertionError(f"expected validation failure containing {message!r}")


def test_schema_constants_are_synchronized() -> None:
    schema = json.loads((ROOT / "schemas" / "audit-report.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert set(schema["required"]) == TOP_LEVEL_REQUIRED
    assert set(schema["properties"]["target_type"]["enum"]) == TARGET_TYPES
    assert set(schema["properties"]["mutation_status"]["enum"]) == MUTATION_STATUSES
    capability_schema = schema["properties"]["capabilities"]["items"]
    assert set(capability_schema["required"]) == CAPABILITY_REQUIRED
    assert set(capability_schema["properties"]["relevance"]["enum"]) == set(RELEVANCE_MULTIPLIER)
    assert set(capability_schema["properties"]["availability"]["enum"]) == AVAILABILITY_TYPES
    assert set(capability_schema["properties"]["usage"]["enum"]) == USAGE_TYPES
    evidence_schema = capability_schema["properties"]["evidence"]["items"]
    assert set(evidence_schema["required"]) == EVIDENCE_REQUIRED
    assert set(evidence_schema["properties"]["kind"]["enum"]) == EVIDENCE_KINDS
    assert set(evidence_schema["properties"]["status"]["enum"]) == EVIDENCE_STATUSES
    upgrade_schema = schema["properties"]["upgrades"]["items"]
    assert set(upgrade_schema["properties"]["gap"]["enum"]) == GAP_TYPES
    assert set(upgrade_schema["required"]) == UPGRADE_REQUIRED


def test_gap_precedence_and_structured_evidence() -> None:
    assert classify_gap(capability("missing", availability="unavailable")) == "UNAVAILABLE"
    assert classify_gap(capability("hidden", discovered=False)) == "UNDISCOVERED"
    assert classify_gap(capability("idle", usage="unused")) == "UNUSED"
    assert classify_gap(capability("wrong", usage="misused")) == "MISUSED"
    assert classify_gap(capability("claimed", evidence=[])) == "UNVERIFIED"
    partial = audit([capability("partial", evidence=[evidence("PARTIAL")])], [upgrade("partial", "UNVERIFIED")])
    result = analyze_audit(partial)
    assert result["capability_utilization_score"] == 25
    assert result["gaps"][0]["gap"] == "UNVERIFIED"
    invalid_string = audit([capability("claim", evidence=["claim"])])
    expect_invalid(invalid_string, "must be an object")


def test_irrelevant_capability_is_not_scored() -> None:
    result = analyze_audit(
        audit(
            [
                capability("relevant"),
                capability("irrelevant", relevance="irrelevant", usage="unused", evidence=[]),
            ]
        )
    )
    assert result["capability_utilization_score"] == 100
    assert result["decision"] == "NO_CAPABILITY_UPGRADE_NEEDED"
    assert result["relevant_capability_count"] == 1


def test_human_gate_takes_decision_precedence() -> None:
    data = audit(
        [capability("visual proof", usage="misused", evidence=[evidence("PARTIAL", kind="screenshot")])],
        [upgrade("visual proof", "MISUSED", human_gate=True)],
    )
    result = analyze_audit(data)
    assert result["decision"] == "NEEDS_HUMAN_DECISION"
    missing_reason = copy.deepcopy(data)
    del missing_reason["upgrades"][0]["human_gate_reason"]
    expect_invalid(missing_reason, "human_gate_reason is required")


def test_strict_validation_and_upgrade_matching() -> None:
    unknown_field = audit([capability("tests")])
    unknown_field["surprise"] = True
    expect_invalid(unknown_field, "unknown fields")

    duplicate = audit([capability("Tests"), capability("tests")])
    expect_invalid(duplicate, "duplicate capability name")

    wrong_enum = audit([capability("tests", availability="bogus")])
    expect_invalid(wrong_enum, "availability contains an unknown value")

    wrong_type = audit([capability("tests", discovered="yes")])
    expect_invalid(wrong_type, "discovered must be a boolean")

    mismatch = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "MISUSED")],
    )
    expect_invalid(mismatch, "does not match actual gap")

    fake = audit([capability("tests")], [upgrade("tests", "UNUSED")])
    expect_invalid(fake, "has no actual gap")

    duplicate_upgrade = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED"), upgrade("tests", "UNUSED")],
    )
    expect_invalid(duplicate_upgrade, "duplicate upgrade capability")

    too_many = audit(
        [capability(str(index), usage="unused", evidence=[]) for index in range(4)],
        [upgrade(str(index), "UNUSED") for index in range(4)],
    )
    expect_invalid(too_many, "at most three")


def test_before_after_verification() -> None:
    baseline = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
    )
    candidate = audit([capability("tests")])
    result = compare_audits(baseline, candidate)
    assert result["capability_upgrade_verification"] == "PROVEN"
    assert result["score_delta"] == 100
    assert result["resolved_gap_count"] == 1

    changed_goal = copy.deepcopy(candidate)
    changed_goal["goal"] = "a different task"
    assert compare_audits(baseline, changed_goal)["capability_upgrade_verification"] == "INCONCLUSIVE"

    changed_relevance = copy.deepcopy(candidate)
    changed_relevance["capabilities"][0]["relevance"] = "useful"
    assert compare_audits(baseline, changed_relevance)["capability_upgrade_verification"] == "INCONCLUSIVE"

    changed_impact = copy.deepcopy(candidate)
    changed_impact["capabilities"][0]["impact"] = 1
    assert compare_audits(baseline, changed_impact)["capability_upgrade_verification"] == "INCONCLUSIVE"

    regressed = audit(
        [capability("tests", availability="unavailable", usage="unused", evidence=[])],
        [upgrade("tests", "UNAVAILABLE")],
    )
    assert compare_audits(candidate, regressed)["capability_upgrade_verification"] == "REGRESSION"


def main() -> int:
    test_schema_constants_are_synchronized()
    test_gap_precedence_and_structured_evidence()
    test_irrelevant_capability_is_not_scored()
    test_human_gate_takes_decision_precedence()
    test_strict_validation_and_upgrade_matching()
    test_before_after_verification()
    print("Codexcavator v0.2 score regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
