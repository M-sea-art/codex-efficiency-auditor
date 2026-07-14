#!/usr/bin/env python3
"""Validate and score task-relevant Codex capability evidence."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.2"
RELEVANCE_MULTIPLIER = {"required": 1.0, "useful": 0.6, "irrelevant": 0.0}
AVAILABILITY_TYPES = {"available", "unavailable", "unknown"}
USAGE_TYPES = {"used", "unused", "misused", "not_applicable"}
TARGET_TYPES = {"thread", "repo", "worktree", "pr", "agent_run", "transcript"}
MUTATION_STATUSES = {"NO_FILES_MODIFIED_BY_AUDIT", "MUTATION_DETECTED", "UNKNOWN"}
GAP_TYPES = {"UNAVAILABLE", "UNDISCOVERED", "UNUSED", "MISUSED", "UNVERIFIED"}
EVIDENCE_KINDS = {
    "command", "test", "build", "ci", "git", "trace", "runtime", "screenshot", "artifact", "human", "other"
}
EVIDENCE_STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_EVALUATED"}
GAP_SEVERITY = {None: 0, "UNVERIFIED": 1, "MISUSED": 2, "UNUSED": 3, "UNDISCOVERED": 4, "UNAVAILABLE": 5}

TOP_LEVEL_REQUIRED = {"schema_version", "audit_id", "target_type", "goal", "mutation_status", "capabilities", "upgrades"}
CAPABILITY_REQUIRED = {"name", "relevance", "availability", "discovered", "usage", "impact", "evidence"}
EVIDENCE_REQUIRED = {"kind", "status", "summary"}
EVIDENCE_OPTIONAL = {"locator"}
UPGRADE_REQUIRED = {"capability", "gap", "action", "expected_gain", "verification", "human_gate"}
UPGRADE_OPTIONAL = {"human_gate_reason"}


def _normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _enum_string(value: Any, allowed: set[str] | dict[str, float], label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{label} contains an unknown value")
    return value


def _exact_keys(item: dict[str, Any], required: set[str], optional: set[str], label: str) -> None:
    missing = sorted(required - item.keys())
    unknown = sorted(item.keys() - required - optional)
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{label} contains unknown fields: {', '.join(unknown)}")


def validate_audit(data: dict[str, Any]) -> None:
    _exact_keys(data, TOP_LEVEL_REQUIRED, set(), "audit")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    _nonempty_string(data["audit_id"], "audit_id")
    _nonempty_string(data["goal"], "goal")
    _enum_string(data["target_type"], TARGET_TYPES, "target_type")
    _enum_string(data["mutation_status"], MUTATION_STATUSES, "mutation_status")

    capabilities = data["capabilities"]
    if not isinstance(capabilities, list) or not capabilities:
        raise ValueError("capabilities must be a non-empty array")
    seen_capabilities: set[str] = set()
    for index, capability in enumerate(capabilities):
        label = f"capabilities[{index}]"
        if not isinstance(capability, dict):
            raise ValueError(f"{label} must be an object")
        _exact_keys(capability, CAPABILITY_REQUIRED, set(), label)
        name = _nonempty_string(capability["name"], f"{label}.name")
        normalized_name = _normalize_text(name)
        if normalized_name in seen_capabilities:
            raise ValueError(f"duplicate capability name: {name}")
        seen_capabilities.add(normalized_name)
        _enum_string(capability["relevance"], RELEVANCE_MULTIPLIER, f"{label}.relevance")
        _enum_string(capability["availability"], AVAILABILITY_TYPES, f"{label}.availability")
        if type(capability["discovered"]) is not bool:
            raise ValueError(f"{label}.discovered must be a boolean")
        _enum_string(capability["usage"], USAGE_TYPES, f"{label}.usage")
        if type(capability["impact"]) is not int or not 1 <= capability["impact"] <= 5:
            raise ValueError(f"{label}.impact must be an integer between 1 and 5")
        evidence_items = capability["evidence"]
        if not isinstance(evidence_items, list):
            raise ValueError(f"{label}.evidence must be an array")
        for evidence_index, evidence in enumerate(evidence_items):
            evidence_label = f"{label}.evidence[{evidence_index}]"
            if not isinstance(evidence, dict):
                raise ValueError(f"{evidence_label} must be an object")
            _exact_keys(evidence, EVIDENCE_REQUIRED, EVIDENCE_OPTIONAL, evidence_label)
            _enum_string(evidence["kind"], EVIDENCE_KINDS, f"{evidence_label}.kind")
            _enum_string(evidence["status"], EVIDENCE_STATUSES, f"{evidence_label}.status")
            _nonempty_string(evidence["summary"], f"{evidence_label}.summary")
            if "locator" in evidence:
                _nonempty_string(evidence["locator"], f"{evidence_label}.locator")

    upgrades = data["upgrades"]
    if not isinstance(upgrades, list):
        raise ValueError("upgrades must be an array")
    if len(upgrades) > 3:
        raise ValueError("upgrades must contain at most three items")
    seen_upgrades: set[str] = set()
    for index, upgrade in enumerate(upgrades):
        label = f"upgrades[{index}]"
        if not isinstance(upgrade, dict):
            raise ValueError(f"{label} must be an object")
        _exact_keys(upgrade, UPGRADE_REQUIRED, UPGRADE_OPTIONAL, label)
        capability_name = _nonempty_string(upgrade["capability"], f"{label}.capability")
        normalized_name = _normalize_text(capability_name)
        if normalized_name in seen_upgrades:
            raise ValueError(f"duplicate upgrade capability: {capability_name}")
        seen_upgrades.add(normalized_name)
        _enum_string(upgrade["gap"], GAP_TYPES, f"{label}.gap")
        for field in ("action", "expected_gain", "verification"):
            _nonempty_string(upgrade[field], f"{label}.{field}")
        if type(upgrade["human_gate"]) is not bool:
            raise ValueError(f"{label}.human_gate must be a boolean")
        if upgrade["human_gate"] and "human_gate_reason" not in upgrade:
            raise ValueError(f"{label}.human_gate_reason is required when human_gate is true")
        if "human_gate_reason" in upgrade:
            _nonempty_string(upgrade["human_gate_reason"], f"{label}.human_gate_reason")


def has_passing_evidence(capability: dict[str, Any]) -> bool:
    return any(item["status"] == "PASS" for item in capability["evidence"])


def classify_gap(capability: dict[str, Any]) -> str | None:
    if capability["relevance"] == "irrelevant":
        return None
    if capability["availability"] == "unavailable":
        return "UNAVAILABLE"
    if capability["availability"] == "unknown":
        return "UNVERIFIED"
    if not capability["discovered"]:
        return "UNDISCOVERED"
    if capability["usage"] in {"unused", "not_applicable"}:
        return "UNUSED"
    if capability["usage"] == "misused":
        return "MISUSED"
    if capability["usage"] == "used" and not has_passing_evidence(capability):
        return "UNVERIFIED"
    return None


def utilization_value(capability: dict[str, Any]) -> float:
    if capability["availability"] != "available" or not capability["discovered"]:
        return 0.0
    if capability["usage"] == "used":
        return 1.0 if has_passing_evidence(capability) else 0.25
    if capability["usage"] == "misused":
        return 0.25
    return 0.0


def decision(score: int, gaps: list[dict[str, Any]], upgrades: list[dict[str, Any]]) -> str:
    if any(upgrade["human_gate"] for upgrade in upgrades):
        return "NEEDS_HUMAN_DECISION"
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


def _validate_upgrade_matches(upgrades: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> None:
    actual = {gap["capability"]: gap["gap"] for gap in gaps}
    for upgrade in upgrades:
        name = upgrade["capability"]
        if name not in actual:
            raise ValueError(f"upgrade capability has no actual gap: {upgrade['capability']}")
        if upgrade["gap"] != actual[name]:
            raise ValueError(
                f"upgrade gap does not match actual gap for {upgrade['capability']}: "
                f"expected {actual[name]}, got {upgrade['gap']}"
            )


def analyze_audit(data: dict[str, Any]) -> dict[str, Any]:
    validate_audit(data)
    numerator = 0.0
    denominator = 0.0
    gaps: list[dict[str, Any]] = []
    relevant_count = 0

    for capability in data["capabilities"]:
        relevance = capability["relevance"]
        if relevance == "irrelevant":
            continue
        relevant_count += 1
        weight = capability["impact"] * RELEVANCE_MULTIPLIER[relevance]
        if capability["availability"] == "available":
            denominator += weight
            numerator += weight * utilization_value(capability)
        gap = classify_gap(capability)
        if gap:
            gaps.append(
                {
                    "capability": capability["name"],
                    "gap": gap,
                    "relevance": relevance,
                    "impact": capability["impact"],
                    "evidence": capability["evidence"],
                }
            )

    score = round(100 * numerator / denominator) if denominator else (100 if relevant_count == 0 else 0)
    gaps.sort(key=lambda item: (item["relevance"] != "required", -item["impact"], item["capability"]))
    _validate_upgrade_matches(data["upgrades"], gaps)
    result = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": data["audit_id"],
        "capability_utilization_score": score,
        "decision": decision(score, gaps, data["upgrades"]),
        "relevant_capability_count": relevant_count,
        "gaps": gaps,
        "recommended_upgrades": data["upgrades"],
    }
    if gaps and not data["upgrades"]:
        result["warning"] = "Capability gaps exist but no evidence-backed upgrade was supplied."
    return result


def _declarations(audit: dict[str, Any]) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        sorted((item["name"], item["relevance"], item["impact"]) for item in audit["capabilities"])
    )


def compare_audits(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_result = analyze_audit(baseline)
    candidate_result = analyze_audit(candidate)
    comparable_schema = baseline["schema_version"] == candidate["schema_version"] == SCHEMA_VERSION
    comparable_target_type = baseline["target_type"] == candidate["target_type"]
    comparable_goal = _normalize_text(baseline["goal"]) == _normalize_text(candidate["goal"])
    comparable_declarations = _declarations(baseline) == _declarations(candidate)
    comparable = comparable_schema and comparable_target_type and comparable_goal and comparable_declarations

    baseline_gaps = {item["capability"]: item for item in baseline_result["gaps"]}
    candidate_gaps = {item["capability"]: item for item in candidate_result["gaps"]}
    resolved_gap_count = sum(1 for name in baseline_gaps if name not in candidate_gaps)
    relevance_by_name = {item["name"]: item["relevance"] for item in baseline["capabilities"]}
    required_gap_regression = any(
        GAP_SEVERITY[candidate_gaps.get(name, {}).get("gap")] > GAP_SEVERITY[baseline_gaps.get(name, {}).get("gap")]
        for name, _, _ in _declarations(baseline)
        if relevance_by_name[name] == "required"
    )
    score_delta = candidate_result["capability_utilization_score"] - baseline_result["capability_utilization_score"]
    if not comparable:
        verification = "INCONCLUSIVE"
    elif score_delta < 0 or required_gap_regression:
        verification = "REGRESSION"
    elif score_delta > 0 and resolved_gap_count > 0:
        verification = "PROVEN"
    else:
        verification = "NOT_PROVEN"

    return {
        "schema_version": SCHEMA_VERSION,
        "capability_upgrade_verification": verification,
        "baseline_score": baseline_result["capability_utilization_score"],
        "candidate_score": candidate_result["capability_utilization_score"],
        "score_delta": score_delta,
        "baseline_gaps": len(baseline_result["gaps"]),
        "candidate_gaps": len(candidate_result["gaps"]),
        "resolved_gap_count": resolved_gap_count,
        "required_gap_regression": required_gap_regression,
        "comparable_schema": comparable_schema,
        "comparable_target_type": comparable_target_type,
        "comparable_goal": comparable_goal,
        "comparable_declarations": comparable_declarations,
    }


def load_audit(path: str | None) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and score a Codexcavator v0.2 capability audit.")
    parser.add_argument("json_file", nargs="?", help="Audit JSON path. Reads stdin if omitted.")
    parser.add_argument("--baseline", help="Optional baseline audit JSON for before-and-after verification.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    try:
        audit = load_audit(args.json_file)
        result = compare_audits(load_audit(args.baseline), audit) if args.baseline else analyze_audit(audit)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.baseline:
        print(f"Schema Version: {result['schema_version']}")
        print(f"Capability Upgrade Verification: {result['capability_upgrade_verification']}")
        print(f"Score: {result['baseline_score']} -> {result['candidate_score']} ({result['score_delta']:+d})")
        print(f"Gaps: {result['baseline_gaps']} -> {result['candidate_gaps']}")
    else:
        print(f"Schema Version: {result['schema_version']}")
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
