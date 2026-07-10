#!/usr/bin/env python3
"""Regression checks for capability-mining audit scoring."""

from __future__ import annotations

from score_audit import analyze_audit, classify_gap, compare_audits


def capability(name: str, **overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": name,
        "relevance": "required",
        "availability": "available",
        "discovered": True,
        "usage": "used",
        "impact": 5,
        "evidence": ["verified tool output"],
    }
    item.update(overrides)
    return item


def test_gap_precedence() -> None:
    assert classify_gap(capability("missing", availability="unavailable")) == "UNAVAILABLE"
    assert classify_gap(capability("hidden", discovered=False)) == "UNDISCOVERED"
    assert classify_gap(capability("idle", usage="unused")) == "UNUSED"
    assert classify_gap(capability("wrong", usage="misused")) == "MISUSED"
    assert classify_gap(capability("claimed", evidence=[])) == "UNVERIFIED"


def test_irrelevant_capability_is_not_scored() -> None:
    result = analyze_audit(
        {
            "audit_id": "focused",
            "capabilities": [
                capability("relevant"),
                capability("irrelevant", relevance="irrelevant", usage="unused", evidence=[]),
            ],
            "upgrades": [],
        }
    )
    assert result["capability_utilization_score"] == 100
    assert result["decision"] == "NO_CAPABILITY_UPGRADE_NEEDED"
    assert result["relevant_capability_count"] == 1


def test_misuse_produces_upgrade_decision() -> None:
    result = analyze_audit(
        {
            "audit_id": "misused",
            "capabilities": [capability("browser", usage="misused", evidence=["screenshot only"])],
            "upgrades": [
                {
                    "capability": "browser",
                    "gap": "MISUSED",
                    "action": "Run the real interaction path.",
                    "expected_gain": "Runtime evidence",
                    "verification": "Capture the interaction trace and final state.",
                }
            ],
        }
    )
    assert result["capability_utilization_score"] == 25
    assert result["decision"] == "CAPABILITY_REPLAN_NEEDED"
    assert result["gaps"][0]["gap"] == "MISUSED"


def test_upgrade_limit_is_enforced() -> None:
    audit = {
        "capabilities": [capability("unused", usage="unused", evidence=[])],
        "upgrades": [
            {"capability": str(index), "gap": "UNUSED", "action": "use", "verification": "check"}
            for index in range(4)
        ],
    }
    try:
        analyze_audit(audit)
    except ValueError as error:
        assert "at most three" in str(error)
    else:
        raise AssertionError("expected upgrade limit failure")


def test_before_after_verification() -> None:
    baseline = {
        "goal": "verify the same task",
        "capabilities": [capability("tests", usage="unused", evidence=[])],
        "upgrades": [],
    }
    candidate = {
        "goal": "verify the same task",
        "capabilities": [capability("tests")],
        "upgrades": [],
    }
    result = compare_audits(baseline, candidate)
    assert result["capability_upgrade_verification"] == "PROVEN"
    assert result["score_delta"] == 100

    candidate["goal"] = "a different task"
    assert compare_audits(baseline, candidate)["capability_upgrade_verification"] == "INCONCLUSIVE"


def main() -> int:
    test_gap_precedence()
    test_irrelevant_capability_is_not_scored()
    test_misuse_produces_upgrade_decision()
    test_upgrade_limit_is_enforced()
    test_before_after_verification()
    print("capability mining score regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
