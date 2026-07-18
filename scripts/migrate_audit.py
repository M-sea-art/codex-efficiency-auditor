#!/usr/bin/env python3
"""Deterministically migrate a Codexcavator v0.2 audit to v0.3."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from audit_contract import SCHEMA_VERSION
from score_audit import validate_audit


V02_REQUIRED = {
    "schema_version",
    "audit_id",
    "target_type",
    "goal",
    "mutation_status",
    "capabilities",
    "upgrades",
}
AVAILABILITY_MAP = {
    "available": "available_in_session",
    "unavailable": "unavailable",
    "unknown": "unknown",
}


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _validate_v02_shape(data: dict[str, Any]) -> None:
    if set(data) != V02_REQUIRED:
        missing = sorted(V02_REQUIRED - data.keys())
        unknown = sorted(data.keys() - V02_REQUIRED)
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise ValueError(f"v0.2 audit fields are invalid ({'; '.join(details)})")
    if data.get("schema_version") != "0.2":
        raise ValueError("input schema_version must be '0.2'")
    if not isinstance(data.get("capabilities"), list) or not data["capabilities"]:
        raise ValueError("v0.2 capabilities must be a non-empty array")
    if not isinstance(data.get("upgrades"), list):
        raise ValueError("v0.2 upgrades must be an array")


def migrate_audit(data: dict[str, Any]) -> dict[str, Any]:
    _validate_v02_shape(data)
    capabilities: list[dict[str, Any]] = []
    for index, raw_capability in enumerate(data["capabilities"]):
        capability = _require_object(raw_capability, f"capabilities[{index}]")
        availability = capability.get("availability")
        if availability not in AVAILABILITY_MAP:
            raise ValueError(f"capabilities[{index}].availability contains an unknown v0.2 value")
        evidence_items = capability.get("evidence")
        if not isinstance(evidence_items, list):
            raise ValueError(f"capabilities[{index}].evidence must be an array")
        migrated_evidence = []
        for evidence_index, raw_evidence in enumerate(evidence_items):
            evidence = copy.deepcopy(_require_object(raw_evidence, f"capabilities[{index}].evidence[{evidence_index}]"))
            evidence["claim_scope"] = "capability_use"
            migrated_evidence.append(evidence)
        capabilities.append(
            {
                "name": capability.get("name"),
                "relevance": capability.get("relevance"),
                "availability": AVAILABILITY_MAP[availability],
                "discovered": capability.get("discovered"),
                "usage": capability.get("usage"),
                "impact": capability.get("impact"),
                "evidence": migrated_evidence,
            }
        )

    upgrades: list[dict[str, Any]] = []
    for index, raw_upgrade in enumerate(data["upgrades"]):
        upgrade = _require_object(raw_upgrade, f"upgrades[{index}]")
        human_gate = upgrade.get("human_gate")
        migrated = {
            "capability": upgrade.get("capability"),
            "gap": upgrade.get("gap"),
            "route": "HUMAN_GATE" if human_gate is True else "DISCOVER_FIRST",
            "action": upgrade.get("action"),
            "expected_gain": upgrade.get("expected_gain"),
            "smallest_useful_check": upgrade.get("verification"),
            "human_gate": human_gate,
        }
        if "human_gate_reason" in upgrade:
            migrated["human_gate_reason"] = upgrade["human_gate_reason"]
        upgrades.append(migrated)

    migrated_audit = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": data["audit_id"],
        "target_type": data["target_type"],
        "goal": data["goal"],
        "operation_contract": {
            "task_mode": "unknown",
            "local_mutation_scope": "unknown",
            "external_actions": "unknown",
            "constraints": [],
            "human_gates": [],
        },
        "scope_conformance": {"status": "UNKNOWN", "evidence": []},
        "audit_mutation_status": data["mutation_status"],
        "run_evidence": None,
        "outcomes": [],
        "efficiency_metrics": [],
        "capabilities": capabilities,
        "upgrades": upgrades,
        "migration": {
            "from_schema": "0.2",
            "notes": [
                "Operation contract and scope conformance were not present in v0.2 and remain unknown.",
                "Run evidence, task outcomes, and efficiency metrics require fresh evidence before comparison can be PROVEN.",
                "Non-Human-Gate upgrade routes were conservatively set to DISCOVER_FIRST.",
            ],
        },
    }
    validate_audit(migrated_audit)
    return migrated_audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate a Codexcavator v0.2 audit to strict v0.3.")
    parser.add_argument("--input", required=True, help="v0.2 audit JSON path.")
    parser.add_argument("--output", help="Optional v0.3 output JSON path. Defaults to stdout.")
    args = parser.parse_args(argv)
    try:
        source = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(source, dict):
            raise ValueError("input must be a JSON object")
        rendered = json.dumps(migrate_audit(source), ensure_ascii=False, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
