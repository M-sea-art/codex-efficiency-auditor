#!/usr/bin/env python3
"""Score a Codex efficiency audit from category points.

Input JSON example:
{
  "goal_scope": 13,
  "decomposition": 12,
  "capability_use": 10,
  "context_memory": 8,
  "risk_git": 14,
  "verification": 12,
  "reporting": 9,
  "upgrade_leverage": 4
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MAX_POINTS = {
    "goal_scope": 15,
    "decomposition": 15,
    "capability_use": 15,
    "context_memory": 10,
    "risk_git": 15,
    "verification": 15,
    "reporting": 10,
    "upgrade_leverage": 5,
}


def verdict(score: int) -> str:
    if score >= 90:
        return "exemplary Codex-native execution"
    if score >= 75:
        return "strong execution with clear upgrade opportunities"
    if score >= 60:
        return "useful but under-leveraged Codex run"
    if score >= 40:
        return "mostly single-thread execution with weak auditability"
    return "risky, unclear, or not meaningfully auditable"


def load_scores(path: str | None) -> dict[str, int]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("Input must be a JSON object.")
    scores: dict[str, int] = {}
    for key, max_value in MAX_POINTS.items():
        value = int(data.get(key, 0))
        if value < 0 or value > max_value:
            raise SystemExit(f"{key} must be between 0 and {max_value}.")
        scores[key] = value
    return scores


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a Codex efficiency audit JSON.")
    parser.add_argument("json_file", nargs="?", help="Path to JSON scores. Reads stdin if omitted.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    scores = load_scores(args.json_file)
    total = sum(scores.values())
    result = {"score": total, "verdict": verdict(total), "categories": scores}

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Codex Capability Utilization: {total}/100")
        print(f"Verdict: {result['verdict']}")
        for key, value in scores.items():
            print(f"- {key}: {value}/{MAX_POINTS[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

