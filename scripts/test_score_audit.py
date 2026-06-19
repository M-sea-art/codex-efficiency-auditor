#!/usr/bin/env python3
"""Regression checks for audit score decisions."""

from __future__ import annotations

from score_audit import decision, verdict


def test_decision_bands() -> None:
    assert decision(95) == "GO"
    assert decision(82) == "GO_WITH_MINOR_FIXES"
    assert decision(68) == "GO_WITH_REQUIRED_FIXES"
    assert decision(54) == "NO_GO"
    assert decision(30) == "NEEDS_REPLAN"


def test_verdict_compatibility() -> None:
    assert verdict(90) == "exemplary Codex-native execution"
    assert verdict(75) == "strong execution with clear upgrade opportunities"
    assert verdict(60) == "useful but under-leveraged Codex run"
    assert verdict(40) == "mostly single-thread execution with weak auditability"


def main() -> int:
    test_decision_bands()
    test_verdict_compatibility()
    print("score audit regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
