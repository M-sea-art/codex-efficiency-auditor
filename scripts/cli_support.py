#!/usr/bin/env python3
"""Shared human rendering and privacy-bounded CLI errors for Codexcavator."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


class CliFailure(Exception):
    """A stable, actionable failure exposed by the unified CLI."""

    def __init__(self, code: str, message: str, next_action: str, *, note: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.next_action = next_action
        self.note = note


def _safe_validation_message(error: Exception) -> str:
    raw = str(error)
    if raw.startswith("audit is missing required fields:"):
        fields = re.findall(r"[a-z_]+", raw.partition(":")[2])
        return "Audit is missing required v0.3 fields: " + ", ".join(fields) + "."
    if raw.startswith("schema_version must be"):
        return "schema_version must be '0.3'."
    match = re.match(r"([a-z_]+(?:\[\d+\])?(?:\.[a-z_]+)*)\b", raw)
    if match:
        return f"Audit field {match.group(1)} does not satisfy the v0.3 contract."
    return "The audit does not satisfy the strict v0.3 contract."


def classify_error(error: Exception, command: str, *, rollout: bool = False) -> CliFailure:
    help_command = f"python scripts/codexcavator.py {command} --help"
    if isinstance(error, CliFailure):
        return error
    if isinstance(error, FileNotFoundError):
        return CliFailure("FILE_NOT_FOUND", "The requested input file was not found.", help_command)
    if isinstance(error, json.JSONDecodeError):
        return CliFailure(
            "JSON_INVALID",
            f"Input is not valid JSON at line {error.lineno}, column {error.colno}.",
            help_command,
        )
    if isinstance(error, OSError):
        return CliFailure("FILE_IO_ERROR", "The requested file operation could not be completed.", help_command)
    if rollout or error.__class__.__name__ == "CollectionError":
        return CliFailure(
            "ROLLOUT_PARSE_FAILED",
            "The rollout is malformed, incomplete, or contains an unknown critical structure.",
            help_command,
            note="--allow-partial is diagnostic only and can never support PROVEN.",
        )
    if isinstance(error, (TypeError, ValueError)):
        return CliFailure("AUDIT_SCHEMA_INVALID", _safe_validation_message(error), help_command)
    return CliFailure("UNEXPECTED_ERROR", "The command could not be completed.", help_command)


def emit_error(error: CliFailure, *, json_output: bool = False) -> int:
    if json_output:
        payload: dict[str, Any] = {
            "error": {
                "code": error.code,
                "message": error.message,
                "next_action": error.next_action,
            }
        }
        if error.note:
            payload["error"]["note"] = error.note
        sys.stderr.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        sys.stderr.write(f"ERROR [{error.code}]: {error.message}\n")
        if error.note:
            sys.stderr.write(f"NOTE: {error.note}\n")
        sys.stderr.write(f"NEXT: {error.next_action}\n")
    return 2


def audit_next_action(result: dict[str, Any]) -> str:
    if result["decision"] == "NEEDS_HUMAN_DECISION":
        return "Resolve the retained Human Gate, then re-audit the same declarations."
    upgrades = result["recommended_upgrades"]
    if upgrades:
        return upgrades[0]["smallest_useful_check"]
    warnings = result.get("warnings", [])
    if any("Run evidence" in warning for warning in warnings):
        return "Collect strict run evidence, add it to the audit, and run the same audit again."
    if result["gaps"]:
        return "Add one evidence-backed upgrade for the highest-impact gap, then re-audit."
    return "Keep the current capability stack and re-audit only when the goal or evidence changes."


def render_audit(result: dict[str, Any]) -> str:
    lines = [
        f"Schema Version: {result['schema_version']}",
        f"Codex Capability Utilization: {result['capability_utilization_score']}/100",
        f"Decision: {result['decision']}",
        f"Audit Mutation Status: {result['audit_mutation_status']}",
        f"Scope Conformance: {result['scope_conformance']}",
    ]
    if result["gaps"]:
        lines.append("Gaps:")
        for gap in result["gaps"]:
            lines.append(f"- {gap['gap']}: {gap['capability']} ({gap['relevance']}, impact={gap['impact']})")
    if result["recommended_upgrades"]:
        lines.append("Upgrades:")
        for index, upgrade in enumerate(result["recommended_upgrades"], start=1):
            lines.append(f"{index}. [{upgrade['route']}] {upgrade['capability']}: {upgrade['action']}")
            lines.append(f"   Smallest useful check: {upgrade['smallest_useful_check']}")
    warnings = result.get("warnings", [])
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["Next action:", f"- {audit_next_action(result)}"])
    return "\n".join(lines)


COMPARABILITY_LABELS = {
    "comparable_schema": "schema version",
    "comparable_target_type": "target type",
    "comparable_goal": "normalized goal",
    "comparable_operation_contract": "operation contract",
    "comparable_capabilities": "capability declarations",
    "comparable_outcomes": "outcome declarations",
    "comparable_metrics": "efficiency metric declarations",
}


def comparison_blockers(result: dict[str, Any]) -> list[str]:
    blockers = [label for key, label in COMPARABILITY_LABELS.items() if not result[key]]
    if not result["run_evidence_ready"]:
        blockers.append("complete PASS run evidence")
    if not result["audit_mutation_ready"]:
        blockers.append("audit mutation and scope proof")
    verdict = result["capability_upgrade_verification"]
    if verdict == "UTILIZATION_IMPROVED_OUTCOME_UNPROVEN":
        blockers.append("a PASS task outcome or threshold-meeting declared efficiency metric")
    elif verdict == "NO_CHANGE":
        blockers.append("higher utilization with a closed real capability gap")
    elif verdict == "REGRESSION":
        blockers.append("a candidate without required outcome, metric, scope, or mutation-safety regression")
    return blockers


def comparison_next_action(result: dict[str, Any], blockers: list[str]) -> str:
    verdict = result["capability_upgrade_verification"]
    if verdict == "PROVEN":
        return "Retain the verified upgrade and preserve the same declarations for future comparisons."
    if verdict == "UTILIZATION_IMPROVED_OUTCOME_UNPROVEN":
        return "Add a PASS task outcome or threshold-meeting declared metric, then compare again."
    if verdict == "REGRESSION":
        return "Reject or revise the candidate before running the same comparison again."
    if verdict == "INCONCLUSIVE" and blockers:
        return "Align the listed blockers, then run the same comparison again."
    return "Keep the current stack unless new evidence changes the comparison."


def render_comparison(result: dict[str, Any]) -> str:
    lines = [
        f"Schema Version: {result['schema_version']}",
        f"Capability Upgrade Verification: {result['capability_upgrade_verification']}",
        f"Score: {result['baseline_score']} -> {result['candidate_score']} ({result['score_delta']:+d})",
        f"Gaps: {result['baseline_gaps']} -> {result['candidate_gaps']}",
    ]
    improvements = [
        *(f"Outcome: {name}" for name in result["outcome_improvements"]),
        *(f"Metric: {name}" for name in result["metric_improvements"]),
    ]
    if improvements:
        lines.append("Improvements:")
        lines.extend(f"- {item}" for item in improvements)
    blockers = comparison_blockers(result)
    if blockers:
        lines.append("PROVEN blockers:")
        lines.extend(f"- {item}" for item in blockers)
    lines.extend(["Next action:", f"- {comparison_next_action(result, blockers)}"])
    return "\n".join(lines)
