#!/usr/bin/env python3
"""Regression checks for the Codexcavator v0.3 audit contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from audit_contract import (
    AUDIT_MUTATION_STATUSES,
    AVAILABILITY_TYPES,
    CAPABILITY_REQUIRED,
    CLAIM_SCOPES,
    EFFICIENCY_METRIC_REQUIRED,
    EVIDENCE_KINDS,
    EVIDENCE_REQUIRED,
    EVIDENCE_STATUSES,
    METRIC_NAMES,
    OUTCOME_REQUIRED,
    RELEVANCE_MULTIPLIER,
    RUN_EVIDENCE_REQUIRED,
    RUN_METRIC_FIELDS,
    SCHEMA_VERSION,
    TARGET_TYPES,
    TOP_LEVEL_REQUIRED,
    UPGRADE_REQUIRED,
    UPGRADE_ROUTES,
)
from score_audit import analyze_audit, classify_gap, compare_audits


ROOT = Path(__file__).resolve().parents[1]
SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def evidence(
    status: str = "PASS",
    *,
    kind: str = "test",
    claim_scope: str = "capability_use",
    summary: str = "verified result",
) -> dict[str, str]:
    return {"kind": kind, "status": status, "claim_scope": claim_scope, "summary": summary}


def capability(name: str, **overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": name,
        "relevance": "required",
        "availability": "available_in_session",
        "discovered": True,
        "usage": "used",
        "impact": 5,
        "evidence": [evidence()],
    }
    item.update(overrides)
    return item


def run_evidence(*, digest: str = SHA_A, parse_status: str = "PASS", **metric_overrides: int) -> dict[str, object]:
    metrics = {
        "turns_started": 1,
        "turns_completed": 1,
        "turns_aborted": 0,
        "total_duration_ms": 1000,
        "average_time_to_first_token_ms": 100,
        "input_tokens": 500,
        "cached_input_tokens": 100,
        "output_tokens": 200,
        "reasoning_output_tokens": 50,
        "total_tokens": 700,
        "tool_calls": 2,
        "failed_tool_calls": 0,
        "mcp_calls": 0,
        "failed_mcp_calls": 0,
        "web_searches": 0,
        "patch_calls": 0,
        "failed_patch_calls": 0,
    }
    metrics.update(metric_overrides)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_format": "codex_jsonl",
        "source_sha256": digest,
        "redaction": "strict_metadata_v1",
        "parse_status": parse_status,
        "invalid_line_count": 0 if parse_status == "PASS" else 1,
        "unknown_event_types": [] if parse_status == "PASS" else ["event:future (1)"],
        "session": {"session_id_hash": SHA_A, "cli_version": "codex-cli 0.1", "originator": "fixture", "turn_count": 1},
        "execution_contexts": [],
        "metrics": metrics,
        "tool_usage": [{"name": "shell_command", "count": 2, "failures": 0}],
    }


def outcome(
    status: str,
    *,
    outcome_id: str = "functional-path",
    claim_scope: str = "functional",
    required: bool = True,
    kind: str = "test",
) -> dict[str, object]:
    return {
        "id": outcome_id,
        "description": "The same required path succeeds.",
        "required": required,
        "claim_scope": claim_scope,
        "status": status,
        "evidence": [evidence(status, kind=kind, claim_scope=claim_scope)],
    }


def metric(name: str = "total_tokens", *, kind: str = "relative", value: float = 0.1) -> dict[str, object]:
    return {"name": name, "direction": "lower", "threshold": {"kind": kind, "value": value}}


def audit(
    capabilities: list[dict[str, object]],
    upgrades: list[dict[str, object]] | None = None,
    *,
    outcomes: list[dict[str, object]] | None = None,
    metrics: list[dict[str, object]] | None = None,
    run: dict[str, object] | None = None,
    scope_status: str = "PASS",
) -> dict[str, object]:
    scope_evidence = [evidence(claim_scope="authorization", kind="artifact")] if scope_status == "PASS" else []
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_id": "fixture-audit",
        "target_type": "thread",
        "goal": "verify the same task",
        "operation_contract": {
            "task_mode": "implement",
            "local_mutation_scope": "project",
            "external_actions": "forbidden",
            "constraints": ["keep scope bounded"],
            "human_gates": [],
        },
        "scope_conformance": {"status": scope_status, "evidence": scope_evidence},
        "audit_mutation_status": "NO_FILES_MODIFIED_BY_AUDIT",
        "run_evidence": run if run is not None else run_evidence(),
        "outcomes": outcomes or [],
        "efficiency_metrics": metrics or [],
        "capabilities": capabilities,
        "upgrades": upgrades or [],
    }


def upgrade(name: str, gap: str, *, human_gate: bool = False) -> dict[str, object]:
    item: dict[str, object] = {
        "capability": name,
        "gap": gap,
        "route": "HUMAN_GATE" if human_gate else "DISCOVER_FIRST",
        "action": "Use the capability correctly.",
        "expected_gain": "Close the measured gap.",
        "smallest_useful_check": "Repeat the same path and collect scoped PASS evidence.",
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
    run_schema = json.loads((ROOT / "schemas" / "run-evidence.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert set(schema["required"]) == TOP_LEVEL_REQUIRED
    assert set(schema["properties"]["target_type"]["enum"]) == TARGET_TYPES
    assert set(schema["properties"]["audit_mutation_status"]["enum"]) == AUDIT_MUTATION_STATUSES
    capability_schema = schema["properties"]["capabilities"]["items"]
    assert set(capability_schema["required"]) == CAPABILITY_REQUIRED
    assert set(capability_schema["properties"]["relevance"]["enum"]) == set(RELEVANCE_MULTIPLIER)
    assert set(capability_schema["properties"]["availability"]["enum"]) == AVAILABILITY_TYPES
    evidence_schema = schema["$defs"]["evidence"]
    assert set(evidence_schema["required"]) == EVIDENCE_REQUIRED
    assert set(evidence_schema["properties"]["kind"]["enum"]) == EVIDENCE_KINDS
    assert set(evidence_schema["properties"]["status"]["enum"]) == EVIDENCE_STATUSES
    assert set(evidence_schema["properties"]["claim_scope"]["enum"]) == CLAIM_SCOPES
    outcome_schema = schema["properties"]["outcomes"]["items"]
    assert set(outcome_schema["required"]) == OUTCOME_REQUIRED
    metric_schema = schema["properties"]["efficiency_metrics"]["items"]
    assert set(metric_schema["required"]) == EFFICIENCY_METRIC_REQUIRED
    assert set(metric_schema["properties"]["name"]["enum"]) == METRIC_NAMES
    upgrade_schema = schema["properties"]["upgrades"]["items"]
    assert set(upgrade_schema["required"]) == UPGRADE_REQUIRED
    assert set(upgrade_schema["properties"]["route"]["enum"]) == UPGRADE_ROUTES
    assert set(run_schema["required"]) == RUN_EVIDENCE_REQUIRED
    assert set(run_schema["properties"]["metrics"]["required"]) == RUN_METRIC_FIELDS


def test_gap_precedence_and_scoped_evidence() -> None:
    assert classify_gap(capability("missing", availability="unavailable")) == "UNAVAILABLE"
    assert classify_gap(capability("disabled", availability="disabled")) == "UNAVAILABLE"
    assert classify_gap(capability("installed", availability="installed_not_exposed")) == "UNAVAILABLE"
    assert classify_gap(capability("hidden", discovered=False)) == "UNDISCOVERED"
    assert classify_gap(capability("idle", usage="unused")) == "UNUSED"
    assert classify_gap(capability("wrong", usage="misused")) == "MISUSED"
    visual_only = capability("claimed", evidence=[evidence(claim_scope="visual", kind="screenshot")])
    result = analyze_audit(audit([visual_only], [upgrade("claimed", "UNVERIFIED")]))
    assert result["capability_utilization_score"] == 25
    assert result["gaps"][0]["gap"] == "UNVERIFIED"


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


def test_scope_and_human_gate_precedence() -> None:
    scoped_failure = audit([capability("tests")], scope_status="FAIL")
    assert analyze_audit(scoped_failure)["decision"] == "CAPABILITY_REPLAN_NEEDED"
    gated = audit(
        [capability("owner", usage="misused", evidence=[evidence("PARTIAL")])],
        [upgrade("owner", "MISUSED", human_gate=True)],
    )
    assert analyze_audit(gated)["decision"] == "NEEDS_HUMAN_DECISION"


def test_outcome_evidence_boundaries() -> None:
    visual_for_functional = audit([capability("tests")], outcomes=[outcome("PASS", claim_scope="visual", kind="screenshot")])
    visual_for_functional["outcomes"][0]["claim_scope"] = "functional"
    expect_invalid(visual_for_functional, "same claim_scope")
    fake_human = audit([capability("tests")], outcomes=[outcome("PASS", claim_scope="human_acceptance", kind="artifact")])
    expect_invalid(fake_human, "requires human evidence")


def test_strict_validation_and_upgrade_matching() -> None:
    unknown_field = audit([capability("tests")])
    unknown_field["surprise"] = True
    expect_invalid(unknown_field, "unknown fields")
    duplicate = audit([capability("Tests"), capability("tests")])
    expect_invalid(duplicate, "duplicate capability name")
    bad_route = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
    )
    bad_route["upgrades"][0]["route"] = "HUMAN_GATE"
    expect_invalid(bad_route, "requires human_gate true")
    mismatch = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "MISUSED")],
    )
    expect_invalid(mismatch, "does not match actual gap")


def test_utilization_only_is_not_proven() -> None:
    baseline = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
        run=run_evidence(digest=SHA_A),
    )
    candidate = audit([capability("tests")], run=run_evidence(digest=SHA_B))
    result = compare_audits(baseline, candidate)
    assert result["capability_upgrade_verification"] == "UTILIZATION_IMPROVED_OUTCOME_UNPROVEN"
    assert result["score_delta"] == 100
    assert result["resolved_gap_count"] == 1


def test_outcome_or_metric_can_prove_upgrade() -> None:
    baseline = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
        outcomes=[outcome("FAIL")],
        run=run_evidence(digest=SHA_A),
    )
    candidate = audit(
        [capability("tests")],
        outcomes=[outcome("PASS")],
        run=run_evidence(digest=SHA_B),
    )
    result = compare_audits(baseline, candidate)
    assert result["capability_upgrade_verification"] == "PROVEN"
    assert result["outcome_improvements"] == ["functional-path"]

    metric_baseline = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
        metrics=[metric()],
        run=run_evidence(digest=SHA_A, total_tokens=1000),
    )
    metric_candidate = audit(
        [capability("tests")],
        metrics=[metric()],
        run=run_evidence(digest=SHA_B, total_tokens=800),
    )
    metric_result = compare_audits(metric_baseline, metric_candidate)
    assert metric_result["capability_upgrade_verification"] == "PROVEN"
    assert metric_result["metric_improvements"] == ["total_tokens"]


def test_regression_and_inconclusive_paths() -> None:
    baseline = audit(
        [capability("tests", usage="unused", evidence=[])],
        [upgrade("tests", "UNUSED")],
        metrics=[metric()],
        run=run_evidence(digest=SHA_A, total_tokens=1000),
    )
    regressed = audit(
        [capability("tests")],
        metrics=[metric()],
        run=run_evidence(digest=SHA_B, total_tokens=1100),
    )
    assert compare_audits(baseline, regressed)["capability_upgrade_verification"] == "REGRESSION"

    partial = audit(
        [capability("tests")],
        metrics=[metric()],
        run=run_evidence(digest=SHA_B, parse_status="PARTIAL", total_tokens=800),
    )
    assert compare_audits(baseline, partial)["capability_upgrade_verification"] == "INCONCLUSIVE"

    changed_contract = copy.deepcopy(regressed)
    changed_contract["operation_contract"]["task_mode"] = "review"
    result = compare_audits(baseline, changed_contract)
    assert result["capability_upgrade_verification"] == "INCONCLUSIVE"
    assert result["comparable_operation_contract"] is False


def main() -> int:
    test_schema_constants_are_synchronized()
    test_gap_precedence_and_scoped_evidence()
    test_irrelevant_capability_is_not_scored()
    test_scope_and_human_gate_precedence()
    test_outcome_evidence_boundaries()
    test_strict_validation_and_upgrade_matching()
    test_utilization_only_is_not_proven()
    test_outcome_or_metric_can_prove_upgrade()
    test_regression_and_inconclusive_paths()
    print("Codexcavator v0.3 score regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
