#!/usr/bin/env python3
"""Derive task-relevant Codex capability utilization from structured evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RELEVANCE_MULTIPLIER = {"required": 1.0, "useful": 0.6, "irrelevant": 0.0}
GAP_TYPES = {"UNAVAILABLE", "UNDISCOVERED", "UNUSED", "MISUSED", "UNVERIFIED"}


def classify_gap(capability: dict[str, Any]) -> str | None:
    if capability.get("relevance") == "irrelevant":
        return None
    availability = capability.get("availability", "unknown")
    if availability == "unavailable":
        return "UNAVAILABLE"
    if availability == "unknown":
        return "UNVERIFIED"
    if capability.get("discovered") is False:
        return "UNDISCOVERED"
    usage = capability.get("usage", "unused")
    if usage in {"unused", "not_applicable"}:
        return "UNUSED"
    if usage == "misused":
        return "MISUSED"
    if usage == "used" and not capability.get("evidence"):
        return "UNVERIFIED"
    return None


def utilization_value(capability: dict[str, Any]) -> float:
    if capability.get("availability") != "available":
        return 0.0
    if capability.get("discovered") is False:
        return 0.0
    usage = capability.get("usage")
    if usage == "used":
        return 1.0 if capability.get("evidence") else 0.25
    if usage == "misused":
        return 0.25
    return 0.0


def decision(score: int, gaps: list[dict[str, Any]]) -> str:
    required_gaps = [gap for gap in gaps if gap["relevance"] == "required"]
    if not gaps and score >= 90:
        return "NO_CAPABILITY_UPGRADE_NEEDED"
    if any(gap["gap"] == "UNAVAILABLE" for gap in required_gaps):
        return "CAPABILITY_REPLAN_NEEDED"
    if score >= 85 and not required_gaps:
        return "MINOR_CAPABILITY_GAPS"
    if score >= 50:
        return "CAPABILITY_UPGRADE_RECOMMENDED"
    return "CAPABILITY_REPLAN_NEEDED"


def analyze_audit(data: dict[str, Any]) -> dict[str, Any]:
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list):
        raise ValueError("capabilities must be an array")

    numerator = 0.0
    denominator = 0.0
    gaps: list[dict[str, Any]] = []
    relevant_count = 0

    for capability in capabilities:
        if not isinstance(capability, dict):
            raise ValueError("each capability must be an object")
        relevance = str(capability.get("relevance", "irrelevant"))
        if relevance not in RELEVANCE_MULTIPLIER:
            raise ValueError(f"invalid relevance: {relevance}")
        impact = int(capability.get("impact", 1))
        if impact < 1 or impact > 5:
            raise ValueError("impact must be between 1 and 5")
        if relevance == "irrelevant":
            continue
        relevant_count += 1
        weight = impact * RELEVANCE_MULTIPLIER[relevance]
        if capability.get("availability") == "available":
            denominator += weight
            numerator += weight * utilization_value(capability)
        gap = classify_gap(capability)
        if gap:
            gaps.append(
                {
                    "capability": str(capability.get("name", "unnamed")),
                    "gap": gap,
                    "relevance": relevance,
                    "impact": impact,
                    "evidence": list(capability.get("evidence") or []),
                }
            )

    score = round(100 * numerator / denominator) if denominator else (100 if relevant_count == 0 else 0)
    gaps.sort(key=lambda item: (item["relevance"] != "required", -item["impact"], item["capability"]))

    upgrades = data.get("upgrades") or []
    if not isinstance(upgrades, list):
        raise ValueError("upgrades must be an array")
    if len(upgrades) > 3:
        raise ValueError("upgrades must contain at most three items")
    for upgrade in upgrades:
        if not isinstance(upgrade, dict) or upgrade.get("gap") not in GAP_TYPES:
            raise ValueError("each upgrade must reference a valid capability gap")
        if not upgrade.get("verification"):
            raise ValueError("each upgrade must include verification")

    result = {
        "audit_id": data.get("audit_id", "unknown"),
        "capability_utilization_score": score,
        "decision": decision(score, gaps),
        "relevant_capability_count": relevant_count,
        "gaps": gaps,
        "recommended_upgrades": upgrades,
    }
    if len(gaps) > 0 and not upgrades:
        result["warning"] = "Capability gaps exist but no evidence-backed upgrade was supplied."
    return result


def compare_audits(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_goal = str(baseline.get("goal", "")).strip()
    candidate_goal = str(candidate.get("goal", "")).strip()
    baseline_names = {
        str(item.get("name"))
        for item in baseline.get("capabilities", [])
        if isinstance(item, dict) and item.get("relevance") != "irrelevant"
    }
    candidate_names = {
        str(item.get("name"))
        for item in candidate.get("capabilities", [])
        if isinstance(item, dict) and item.get("relevance") != "irrelevant"
    }
    baseline_result = analyze_audit(baseline)
    candidate_result = analyze_audit(candidate)

    if not baseline_goal or baseline_goal != candidate_goal or baseline_names != candidate_names:
        verification = "INCONCLUSIVE"
    else:
        baseline_required = sum(1 for gap in baseline_result["gaps"] if gap["relevance"] == "required")
        candidate_required = sum(1 for gap in candidate_result["gaps"] if gap["relevance"] == "required")
        score_delta = candidate_result["capability_utilization_score"] - baseline_result["capability_utilization_score"]
        if score_delta > 0 and candidate_required <= baseline_required:
            verification = "PROVEN"
        elif score_delta < 0 or candidate_required > baseline_required:
            verification = "REGRESSION"
        else:
            verification = "NOT_PROVEN"

    return {
        "capability_upgrade_verification": verification,
        "baseline_score": baseline_result["capability_utilization_score"],
        "candidate_score": candidate_result["capability_utilization_score"],
        "score_delta": candidate_result["capability_utilization_score"] - baseline_result["capability_utilization_score"],
        "baseline_gaps": len(baseline_result["gaps"]),
        "candidate_gaps": len(candidate_result["gaps"]),
        "comparable_goal": bool(baseline_goal and baseline_goal == candidate_goal),
        "comparable_capabilities": baseline_names == candidate_names,
    }


def load_audit(path: str | None) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a task-relevant Codex capability audit.")
    parser.add_argument("json_file", nargs="?", help="Audit JSON path. Reads stdin if omitted.")
    parser.add_argument("--baseline", help="Optional baseline audit JSON for before-and-after verification.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    try:
        audit = load_audit(args.json_file)
        result = compare_audits(load_audit(args.baseline), audit) if args.baseline else analyze_audit(audit)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise SystemExit(str(error)) from error

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.baseline:
        print(f"Capability Upgrade Verification: {result['capability_upgrade_verification']}")
        print(f"Score: {result['baseline_score']} -> {result['candidate_score']} ({result['score_delta']:+d})")
        print(f"Gaps: {result['baseline_gaps']} -> {result['candidate_gaps']}")
    else:
        print(f"Codex Capability Utilization: {result['capability_utilization_score']}/100")
        print(f"Decision: {result['decision']}")
        for gap in result["gaps"]:
            print(f"- {gap['gap']}: {gap['capability']} ({gap['relevance']}, impact={gap['impact']})")
        for index, upgrade in enumerate(result["recommended_upgrades"], start=1):
            print(f"{index}. {upgrade['capability']}: {upgrade['action']}")
            print(f"   Verify: {upgrade['verification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
