#!/usr/bin/env python3
"""Validate and score task-relevant Codex capability evidence."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from cli_support import render_audit, render_comparison
from audit_contract import (
    AUDIT_MUTATION_STATUSES,
    AVAILABILITY_TYPES,
    CAPABILITY_REQUIRED,
    CLAIM_SCOPES,
    CONFORMANCE_STATUSES,
    EFFICIENCY_METRIC_REQUIRED,
    EVIDENCE_KINDS,
    EVIDENCE_OPTIONAL,
    EVIDENCE_REQUIRED,
    EVIDENCE_STATUSES,
    EXTERNAL_ACTION_POLICIES,
    GAP_SEVERITY,
    GAP_TYPES,
    LOCAL_MUTATION_SCOPES,
    METRIC_DIRECTIONS,
    METRIC_NAMES,
    OPERATION_CONTRACT_REQUIRED,
    OUTCOME_REQUIRED,
    RELEVANCE_MULTIPLIER,
    RUN_CONTEXT_REQUIRED,
    RUN_EVIDENCE_REQUIRED,
    RUN_METRIC_FIELDS,
    RUN_PARSE_STATUSES,
    RUN_REDACTION_MODES,
    RUN_SESSION_REQUIRED,
    RUN_SOURCE_FORMATS,
    RUN_TOOL_USAGE_REQUIRED,
    SCHEMA_VERSION,
    SCOPE_CONFORMANCE_REQUIRED,
    TARGET_TYPES,
    TASK_MODES,
    THRESHOLD_KINDS,
    THRESHOLD_REQUIRED,
    TOP_LEVEL_OPTIONAL,
    TOP_LEVEL_REQUIRED,
    UPGRADE_OPTIONAL,
    UPGRADE_REQUIRED,
    UPGRADE_ROUTES,
    USAGE_TYPES,
)


def _normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _nullable_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, label)


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


def _string_array(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    for index, item in enumerate(value):
        _nonempty_string(item, f"{label}[{index}]")
    return value


def _nonnegative_number(value: Any, label: str, *, integer: bool = False) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be a non-negative {'integer' if integer else 'number'}")
    if integer and not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_evidence(evidence: Any, label: str, *, expected_scope: str | None = None) -> None:
    if not isinstance(evidence, dict):
        raise ValueError(f"{label} must be an object")
    _exact_keys(evidence, EVIDENCE_REQUIRED, EVIDENCE_OPTIONAL, label)
    _enum_string(evidence["kind"], EVIDENCE_KINDS, f"{label}.kind")
    _enum_string(evidence["status"], EVIDENCE_STATUSES, f"{label}.status")
    scope = _enum_string(evidence["claim_scope"], CLAIM_SCOPES, f"{label}.claim_scope")
    if expected_scope and scope != expected_scope:
        raise ValueError(f"{label}.claim_scope must be {expected_scope!r}")
    _nonempty_string(evidence["summary"], f"{label}.summary")
    if "locator" in evidence:
        _nonempty_string(evidence["locator"], f"{label}.locator")


def _validate_evidence_array(value: Any, label: str, *, expected_scope: str | None = None) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    for index, evidence in enumerate(value):
        _validate_evidence(evidence, f"{label}[{index}]", expected_scope=expected_scope)


def validate_run_evidence(data: Any, label: str = "run_evidence") -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be an object or null")
    _exact_keys(data, RUN_EVIDENCE_REQUIRED, set(), label)
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"{label}.schema_version must be {SCHEMA_VERSION!r}")
    _enum_string(data["source_format"], RUN_SOURCE_FORMATS, f"{label}.source_format")
    digest = _nonempty_string(data["source_sha256"], f"{label}.source_sha256")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"{label}.source_sha256 must be a sha256 digest")
    _enum_string(data["redaction"], RUN_REDACTION_MODES, f"{label}.redaction")
    _enum_string(data["parse_status"], RUN_PARSE_STATUSES, f"{label}.parse_status")
    _nonnegative_number(data["invalid_line_count"], f"{label}.invalid_line_count", integer=True)
    _string_array(data["unknown_event_types"], f"{label}.unknown_event_types")

    session = data["session"]
    if not isinstance(session, dict):
        raise ValueError(f"{label}.session must be an object")
    _exact_keys(session, RUN_SESSION_REQUIRED, set(), f"{label}.session")
    if session["session_id_hash"] is not None:
        session_hash = _nonempty_string(session["session_id_hash"], f"{label}.session.session_id_hash")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", session_hash):
            raise ValueError(f"{label}.session.session_id_hash must be a sha256 digest or null")
    _nullable_string(session["cli_version"], f"{label}.session.cli_version")
    _nullable_string(session["originator"], f"{label}.session.originator")
    _nonnegative_number(session["turn_count"], f"{label}.session.turn_count", integer=True)

    contexts = data["execution_contexts"]
    if not isinstance(contexts, list):
        raise ValueError(f"{label}.execution_contexts must be an array")
    seen_turns: set[str] = set()
    for index, context in enumerate(contexts):
        context_label = f"{label}.execution_contexts[{index}]"
        if not isinstance(context, dict):
            raise ValueError(f"{context_label} must be an object")
        _exact_keys(context, RUN_CONTEXT_REQUIRED, set(), context_label)
        turn_hash = _nonempty_string(context["turn_id_hash"], f"{context_label}.turn_id_hash")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", turn_hash):
            raise ValueError(f"{context_label}.turn_id_hash must be a sha256 digest")
        if turn_hash in seen_turns:
            raise ValueError(f"duplicate execution context turn hash: {turn_hash}")
        seen_turns.add(turn_hash)
        for field in ("collaboration_mode", "approval_policy", "sandbox_mode", "multi_agent_mode"):
            _nullable_string(context[field], f"{context_label}.{field}")

    metrics = data["metrics"]
    if not isinstance(metrics, dict):
        raise ValueError(f"{label}.metrics must be an object")
    _exact_keys(metrics, RUN_METRIC_FIELDS, set(), f"{label}.metrics")
    for field in RUN_METRIC_FIELDS:
        _nonnegative_number(metrics[field], f"{label}.metrics.{field}", integer=True)
    if metrics["turns_completed"] + metrics["turns_aborted"] > metrics["turns_started"]:
        raise ValueError(f"{label}.metrics completed and aborted turns cannot exceed started turns")
    if metrics["failed_tool_calls"] > metrics["tool_calls"]:
        raise ValueError(f"{label}.metrics.failed_tool_calls cannot exceed tool_calls")
    if metrics["failed_mcp_calls"] > metrics["mcp_calls"]:
        raise ValueError(f"{label}.metrics.failed_mcp_calls cannot exceed mcp_calls")
    if metrics["failed_patch_calls"] > metrics["patch_calls"]:
        raise ValueError(f"{label}.metrics.failed_patch_calls cannot exceed patch_calls")

    tool_usage = data["tool_usage"]
    if not isinstance(tool_usage, list):
        raise ValueError(f"{label}.tool_usage must be an array")
    seen_tools: set[str] = set()
    for index, item in enumerate(tool_usage):
        item_label = f"{label}.tool_usage[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{item_label} must be an object")
        _exact_keys(item, RUN_TOOL_USAGE_REQUIRED, set(), item_label)
        name = _nonempty_string(item["name"], f"{item_label}.name")
        normalized = _normalize_text(name)
        if normalized in seen_tools:
            raise ValueError(f"duplicate tool_usage name: {name}")
        seen_tools.add(normalized)
        count = _nonnegative_number(item["count"], f"{item_label}.count", integer=True)
        failures = _nonnegative_number(item["failures"], f"{item_label}.failures", integer=True)
        if failures > count:
            raise ValueError(f"{item_label}.failures cannot exceed count")
    if sum(item["count"] for item in tool_usage) != metrics["tool_calls"]:
        raise ValueError(f"{label}.tool_usage counts must equal metrics.tool_calls")
    if sum(item["failures"] for item in tool_usage) != metrics["failed_tool_calls"]:
        raise ValueError(f"{label}.tool_usage failures must equal metrics.failed_tool_calls")


def validate_audit(data: dict[str, Any]) -> None:
    _exact_keys(data, TOP_LEVEL_REQUIRED, TOP_LEVEL_OPTIONAL, "audit")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    _nonempty_string(data["audit_id"], "audit_id")
    _nonempty_string(data["goal"], "goal")
    _enum_string(data["target_type"], TARGET_TYPES, "target_type")
    _enum_string(data["audit_mutation_status"], AUDIT_MUTATION_STATUSES, "audit_mutation_status")

    contract = data["operation_contract"]
    if not isinstance(contract, dict):
        raise ValueError("operation_contract must be an object")
    _exact_keys(contract, OPERATION_CONTRACT_REQUIRED, set(), "operation_contract")
    _enum_string(contract["task_mode"], TASK_MODES, "operation_contract.task_mode")
    _enum_string(contract["local_mutation_scope"], LOCAL_MUTATION_SCOPES, "operation_contract.local_mutation_scope")
    _enum_string(contract["external_actions"], EXTERNAL_ACTION_POLICIES, "operation_contract.external_actions")
    _string_array(contract["constraints"], "operation_contract.constraints")
    _string_array(contract["human_gates"], "operation_contract.human_gates")

    conformance = data["scope_conformance"]
    if not isinstance(conformance, dict):
        raise ValueError("scope_conformance must be an object")
    _exact_keys(conformance, SCOPE_CONFORMANCE_REQUIRED, set(), "scope_conformance")
    status = _enum_string(conformance["status"], CONFORMANCE_STATUSES, "scope_conformance.status")
    _validate_evidence_array(conformance["evidence"], "scope_conformance.evidence", expected_scope="authorization")
    if status == "PASS" and not any(item["status"] == "PASS" for item in conformance["evidence"]):
        raise ValueError("scope_conformance PASS requires PASS authorization evidence")

    if data["run_evidence"] is not None:
        validate_run_evidence(data["run_evidence"])

    outcomes = data["outcomes"]
    if not isinstance(outcomes, list):
        raise ValueError("outcomes must be an array")
    seen_outcomes: set[str] = set()
    for index, outcome in enumerate(outcomes):
        label = f"outcomes[{index}]"
        if not isinstance(outcome, dict):
            raise ValueError(f"{label} must be an object")
        _exact_keys(outcome, OUTCOME_REQUIRED, set(), label)
        outcome_id = _nonempty_string(outcome["id"], f"{label}.id")
        normalized_id = _normalize_text(outcome_id)
        if normalized_id in seen_outcomes:
            raise ValueError(f"duplicate outcome id: {outcome_id}")
        seen_outcomes.add(normalized_id)
        _nonempty_string(outcome["description"], f"{label}.description")
        if type(outcome["required"]) is not bool:
            raise ValueError(f"{label}.required must be a boolean")
        outcome_scope = _enum_string(outcome["claim_scope"], CLAIM_SCOPES, f"{label}.claim_scope")
        if outcome_scope in {"capability_use", "authorization"}:
            raise ValueError(f"{label}.claim_scope must describe a task outcome")
        _enum_string(outcome["status"], EVIDENCE_STATUSES, f"{label}.status")
        _validate_evidence_array(outcome["evidence"], f"{label}.evidence")
        if outcome["status"] == "PASS":
            matching = [
                item for item in outcome["evidence"]
                if item["status"] == "PASS" and item["claim_scope"] == outcome_scope
            ]
            if not matching:
                raise ValueError(f"{label} PASS requires PASS evidence with the same claim_scope")
            if outcome_scope == "human_acceptance" and not any(item["kind"] == "human" for item in matching):
                raise ValueError(f"{label} human_acceptance PASS requires human evidence")

    metric_declarations = data["efficiency_metrics"]
    if not isinstance(metric_declarations, list):
        raise ValueError("efficiency_metrics must be an array")
    seen_metrics: set[str] = set()
    for index, metric in enumerate(metric_declarations):
        label = f"efficiency_metrics[{index}]"
        if not isinstance(metric, dict):
            raise ValueError(f"{label} must be an object")
        _exact_keys(metric, EFFICIENCY_METRIC_REQUIRED, set(), label)
        name = _enum_string(metric["name"], METRIC_NAMES, f"{label}.name")
        if name in seen_metrics:
            raise ValueError(f"duplicate efficiency metric: {name}")
        seen_metrics.add(name)
        _enum_string(metric["direction"], METRIC_DIRECTIONS, f"{label}.direction")
        threshold = metric["threshold"]
        if not isinstance(threshold, dict):
            raise ValueError(f"{label}.threshold must be an object")
        _exact_keys(threshold, THRESHOLD_REQUIRED, set(), f"{label}.threshold")
        kind = _enum_string(threshold["kind"], THRESHOLD_KINDS, f"{label}.threshold.kind")
        value = _nonnegative_number(threshold["value"], f"{label}.threshold.value")
        if kind == "relative" and value > 1:
            raise ValueError(f"{label}.threshold.value must be between 0 and 1 for relative thresholds")

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
        _validate_evidence_array(capability["evidence"], f"{label}.evidence")

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
        route = _enum_string(upgrade["route"], UPGRADE_ROUTES, f"{label}.route")
        for field in ("action", "expected_gain", "smallest_useful_check"):
            _nonempty_string(upgrade[field], f"{label}.{field}")
        if type(upgrade["human_gate"]) is not bool:
            raise ValueError(f"{label}.human_gate must be a boolean")
        if route == "HUMAN_GATE" and not upgrade["human_gate"]:
            raise ValueError(f"{label}.route HUMAN_GATE requires human_gate true")
        if upgrade["human_gate"] and "human_gate_reason" not in upgrade:
            raise ValueError(f"{label}.human_gate_reason is required when human_gate is true")
        if "human_gate_reason" in upgrade:
            _nonempty_string(upgrade["human_gate_reason"], f"{label}.human_gate_reason")

    if "migration" in data:
        migration = data["migration"]
        if not isinstance(migration, dict) or set(migration) != {"from_schema", "notes"}:
            raise ValueError("migration must contain exactly from_schema and notes")
        _nonempty_string(migration["from_schema"], "migration.from_schema")
        _string_array(migration["notes"], "migration.notes")


def has_passing_evidence(capability: dict[str, Any]) -> bool:
    return any(item["status"] == "PASS" and item["claim_scope"] == "capability_use" for item in capability["evidence"])


def classify_gap(capability: dict[str, Any]) -> str | None:
    if capability["relevance"] == "irrelevant":
        return None
    if capability["availability"] in {"installed_not_exposed", "disabled", "unavailable"}:
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
    if capability["availability"] != "available_in_session" or not capability["discovered"]:
        return 0.0
    if capability["usage"] == "used":
        return 1.0 if has_passing_evidence(capability) else 0.25
    if capability["usage"] == "misused":
        return 0.25
    return 0.0


def decision(data: dict[str, Any], score: int, gaps: list[dict[str, Any]]) -> str:
    if data["audit_mutation_status"] == "MUTATION_DETECTED" or data["scope_conformance"]["status"] == "FAIL":
        return "CAPABILITY_REPLAN_NEEDED"
    if any(upgrade["human_gate"] for upgrade in data["upgrades"]):
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
    actual = {_normalize_text(gap["capability"]): gap["gap"] for gap in gaps}
    for upgrade in upgrades:
        name = _normalize_text(upgrade["capability"])
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
        if capability["availability"] == "available_in_session":
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
        "decision": decision(data, score, gaps),
        "audit_mutation_status": data["audit_mutation_status"],
        "scope_conformance": data["scope_conformance"]["status"],
        "relevant_capability_count": relevant_count,
        "gaps": gaps,
        "recommended_upgrades": data["upgrades"],
    }
    warnings: list[str] = []
    if data["scope_conformance"]["status"] == "UNKNOWN":
        warnings.append("Scope conformance is unknown; before/after verification cannot be PROVEN.")
    if data["audit_mutation_status"] == "UNKNOWN":
        warnings.append("Audit mutation status is unknown; before/after verification cannot be PROVEN.")
    if data["run_evidence"] is None:
        warnings.append("Run evidence is absent; before/after verification cannot be PROVEN.")
    elif data["run_evidence"]["parse_status"] != "PASS":
        warnings.append("Run evidence is partial; before/after verification cannot be PROVEN.")
    if gaps and not data["upgrades"]:
        warnings.append("Capability gaps exist but no evidence-backed upgrade was supplied.")
    if warnings:
        result["warnings"] = warnings
    return result


def _capability_declarations(audit: dict[str, Any]) -> tuple[tuple[str, str, int], ...]:
    return tuple(sorted((_normalize_text(item["name"]), item["relevance"], item["impact"]) for item in audit["capabilities"]))


def _outcome_declarations(audit: dict[str, Any]) -> tuple[tuple[str, str, bool, str], ...]:
    return tuple(
        sorted(
            (_normalize_text(item["id"]), _normalize_text(item["description"]), item["required"], item["claim_scope"])
            for item in audit["outcomes"]
        )
    )


def _metric_declarations(audit: dict[str, Any]) -> tuple[tuple[str, str, str, float], ...]:
    return tuple(
        sorted(
            (
                item["name"],
                item["direction"],
                item["threshold"]["kind"],
                float(item["threshold"]["value"]),
            )
            for item in audit["efficiency_metrics"]
        )
    )


def _operation_declaration(audit: dict[str, Any]) -> tuple[Any, ...]:
    contract = audit["operation_contract"]
    return (
        contract["task_mode"],
        contract["local_mutation_scope"],
        contract["external_actions"],
        tuple(_normalize_text(item) for item in contract["constraints"]),
        tuple(_normalize_text(item) for item in contract["human_gates"]),
    )


def _outcome_statuses(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_normalize_text(item["id"]): item for item in audit["outcomes"]}


def _metric_change(baseline: float, candidate: float, direction: str) -> float:
    return baseline - candidate if direction == "lower" else candidate - baseline


def _metric_meets_threshold(change: float, baseline: float, kind: str, threshold: float) -> bool:
    if change <= 0:
        return False
    if kind == "absolute":
        return change >= threshold
    if baseline == 0:
        return False
    return change / abs(baseline) >= threshold


def compare_audits(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_result = analyze_audit(baseline)
    candidate_result = analyze_audit(candidate)
    comparable_schema = baseline["schema_version"] == candidate["schema_version"] == SCHEMA_VERSION
    comparable_target_type = baseline["target_type"] == candidate["target_type"]
    comparable_goal = _normalize_text(baseline["goal"]) == _normalize_text(candidate["goal"])
    comparable_operation_contract = _operation_declaration(baseline) == _operation_declaration(candidate)
    comparable_capabilities = _capability_declarations(baseline) == _capability_declarations(candidate)
    comparable_outcomes = _outcome_declarations(baseline) == _outcome_declarations(candidate)
    comparable_metrics = _metric_declarations(baseline) == _metric_declarations(candidate)
    comparable = all(
        (
            comparable_schema,
            comparable_target_type,
            comparable_goal,
            comparable_operation_contract,
            comparable_capabilities,
            comparable_outcomes,
            comparable_metrics,
        )
    )

    baseline_gaps = {_normalize_text(item["capability"]): item for item in baseline_result["gaps"]}
    candidate_gaps = {_normalize_text(item["capability"]): item for item in candidate_result["gaps"]}
    resolved_gap_count = sum(1 for name in baseline_gaps if name not in candidate_gaps)
    relevance_by_name = {_normalize_text(item["name"]): item["relevance"] for item in baseline["capabilities"]}
    required_gap_regression = any(
        GAP_SEVERITY[candidate_gaps.get(name, {}).get("gap")] > GAP_SEVERITY[baseline_gaps.get(name, {}).get("gap")]
        for name, _, _ in _capability_declarations(baseline)
        if relevance_by_name[name] == "required"
    )

    baseline_outcomes = _outcome_statuses(baseline)
    candidate_outcomes = _outcome_statuses(candidate)
    outcome_improvements = [
        item["id"]
        for key, item in candidate_outcomes.items()
        if item["status"] == "PASS" and baseline_outcomes.get(key, {}).get("status") != "PASS"
    ]
    outcome_rank = {"NOT_EVALUATED": 0, "FAIL": 1, "PARTIAL": 2, "PASS": 3}
    required_outcome_regression = any(
        item["required"]
        and outcome_rank[item["status"]] < outcome_rank[baseline_outcomes[key]["status"]]
        for key, item in candidate_outcomes.items()
    )

    metric_improvements: list[str] = []
    metric_regressions: list[str] = []
    if baseline["run_evidence"] is not None and candidate["run_evidence"] is not None:
        baseline_values = baseline["run_evidence"]["metrics"]
        candidate_values = candidate["run_evidence"]["metrics"]
        for declaration in candidate["efficiency_metrics"]:
            name = declaration["name"]
            before = float(baseline_values[name])
            after = float(candidate_values[name])
            change = _metric_change(before, after, declaration["direction"])
            threshold = declaration["threshold"]
            if change < 0:
                metric_regressions.append(name)
            elif _metric_meets_threshold(change, before, threshold["kind"], float(threshold["value"])):
                metric_improvements.append(name)

    score_delta = candidate_result["capability_utilization_score"] - baseline_result["capability_utilization_score"]
    candidate_scope_failure = candidate["scope_conformance"]["status"] == "FAIL"
    candidate_audit_mutation = candidate["audit_mutation_status"] == "MUTATION_DETECTED"
    unknown_scope = baseline["scope_conformance"]["status"] != "PASS" or candidate["scope_conformance"]["status"] != "PASS"
    audit_mutation_ready = all(
        item["audit_mutation_status"] == "NO_FILES_MODIFIED_BY_AUDIT" for item in (baseline, candidate)
    )
    run_evidence_ready = all(
        item is not None and item["parse_status"] == "PASS" for item in (baseline["run_evidence"], candidate["run_evidence"])
    )

    if not comparable:
        verification = "INCONCLUSIVE"
    elif candidate_scope_failure or candidate_audit_mutation or score_delta < 0 or required_gap_regression or required_outcome_regression or metric_regressions:
        verification = "REGRESSION"
    elif unknown_scope or not audit_mutation_ready or not run_evidence_ready:
        verification = "INCONCLUSIVE"
    elif score_delta > 0 and resolved_gap_count > 0:
        verification = "PROVEN" if outcome_improvements or metric_improvements else "UTILIZATION_IMPROVED_OUTCOME_UNPROVEN"
    else:
        verification = "NO_CHANGE"

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
        "required_outcome_regression": required_outcome_regression,
        "outcome_improvements": outcome_improvements,
        "metric_improvements": metric_improvements,
        "metric_regressions": metric_regressions,
        "comparable_schema": comparable_schema,
        "comparable_target_type": comparable_target_type,
        "comparable_goal": comparable_goal,
        "comparable_operation_contract": comparable_operation_contract,
        "comparable_capabilities": comparable_capabilities,
        "comparable_outcomes": comparable_outcomes,
        "comparable_metrics": comparable_metrics,
        "run_evidence_ready": run_evidence_ready,
        "audit_mutation_ready": audit_mutation_ready,
    }


def load_audit(path: str | None) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and score a codex-efficiency-auditor v0.3 capability audit.")
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
        print(render_comparison(result))
    else:
        print(render_audit(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
