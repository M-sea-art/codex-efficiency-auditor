#!/usr/bin/env python3
"""Validate Task State Pack directories for codex-efficiency-auditor."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "task_spec.md",
    "progress.json",
    "findings.jsonl",
    "directions_tried.json",
    "iteration_log.jsonl",
    "gates.json",
    "rollback.md",
]

ALLOWED_STATUSES = {
    "AUTHORIZED_GOAL",
    "PREFLIGHT_AUDIT",
    "TASK_CARD_READY",
    "AUTONOMOUS_WORK",
    "PERIODIC_AUDIT",
    "STALE_PROGRESS",
    "REPEATED_FAILURE",
    "RECOVERY_NEEDED",
    "NEEDS_HUMAN_DECISION",
    "READY_FOR_FINAL_AUDIT",
    "BLOCKED",
    "VERSION_CLOSED",
}

TASK_SPEC_MARKERS = [
    "Goal:",
    "Non-goals:",
    "Allowed paths:",
    "Forbidden paths:",
    "Shared locks:",
    "Metric, if any:",
    "Gates:",
    "Success criteria:",
    "Pause conditions:",
    "Human gates:",
    "Final report:",
]

ROLLBACK_MARKERS = [
    "Rollback",
    "Branch/worktree cleanup:",
    "Revert strategy:",
    "Generated files to remove:",
    "External state touched:",
    "Human gate status:",
]

GATE_PASS_PATTERNS = [
    "exit code",
    "pass",
    "fail",
    "pytest",
    "test",
    "lint",
    "typecheck",
    "build",
    "check",
    "验证",
    "通过",
    "失败",
]

DECORATIVE_GATE_PATTERNS = [
    "looks good",
    "seems fine",
    "manual vibes",
    "no gate",
    "not needed",
    "n/a",
    "随便",
    "感觉可以",
    "看起来不错",
    "无需验证",
]

EMPTY_MARKER_VALUES = {
    "none",
    "n/a",
    "not applicable",
    "无",
    "没有",
}

NONE_ALLOWED_MARKERS = {
    "Metric, if any:",
}

HIGH_RISK_GATE_PATTERNS = [
    ("G1_PUSH", ["push", "git push", "推送"]),
    ("G2_PUBLISH", ["publish", "public", "release", "公开", "发布"]),
    ("G3_DEPLOY", ["deploy", "deployment", "部署"]),
    (
        "G4_ACCOUNT",
        [
            "credential",
            "secret",
            "token",
            "api_key",
            "api key",
            "billing",
            "paid service",
            "payment",
            "account",
            "permission",
            "oauth",
            "凭证",
            "密钥",
            "令牌",
            "付费",
            "付款",
            "账单",
            "账号",
            "账户",
            "权限",
            "授权",
        ],
    ),
    ("G5_DESTRUCTIVE", ["delete", "reset", "overwrite", "migration", "删除", "重置", "覆盖", "迁移"]),
    ("G6_EXTERNAL_COMMENT", ["comment", "reply", "post", "email", "message", "评论", "回复", "发帖", "邮件", "消息"]),
]

MARKER_PATTERNS = {
    marker: re.compile(rf"^\s*(?:[-*]\s*)?{re.escape(marker.rstrip(':：'))}\s*[:：]\s*(?P<rest>.*)$", re.IGNORECASE)
    for marker in TASK_SPEC_MARKERS
}


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
    return None


def _lint_jsonl(path: Path, errors: list[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{index}: invalid JSONL record: {exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{path}:{index}: JSONL record must be an object")


def _contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.casefold()
    return any(needle.casefold() in lowered for needle in needles)


def _is_task_spec_marker(line: str) -> bool:
    return any(pattern.match(line) for pattern in MARKER_PATTERNS.values())


def _marker_value(text: str, marker: str) -> str | None:
    lines = text.splitlines()
    pattern = MARKER_PATTERNS[marker]
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue

        rest = match.group("rest").strip()
        if rest:
            return rest

        following: list[str] = []
        for next_line in lines[index + 1 :]:
            if _is_task_spec_marker(next_line):
                break
            if next_line.strip():
                following.append(next_line.strip())
        return "\n".join(following).strip()

    return None


def _is_empty_marker_value(text: str, marker: str) -> bool:
    value = _marker_value(text, marker)
    if value is None:
        return False
    if not value.strip():
        return True
    if marker in NONE_ALLOWED_MARKERS:
        return False
    normalized_lines = [line.strip().lstrip("-* ").casefold() for line in value.splitlines() if line.strip()]
    return all(line in EMPTY_MARKER_VALUES for line in normalized_lines)


def _missing_human_gate_ids(text: str, human_gates: list[str]) -> list[str]:
    human_gate_text = "\n".join(human_gates).casefold()
    missing: list[str] = []
    for gate_id, needles in HIGH_RISK_GATE_PATTERNS:
        if _contains_any(text, needles) and gate_id.casefold() not in human_gate_text:
            missing.append(gate_id)
    return missing


def lint_pack(path: Path) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        return [f"{path}: path does not exist"]
    if not path.is_dir():
        return [f"{path}: Task State Pack must be a directory"]

    for name in REQUIRED_FILES:
        if not (path / name).is_file():
            errors.append(f"{path}: missing required file `{name}`")
    if not (path / "evidence").is_dir():
        errors.append(f"{path}: missing required directory `evidence/`")

    task_spec = path / "task_spec.md"
    if task_spec.is_file():
        text = task_spec.read_text(encoding="utf-8")
        for marker in TASK_SPEC_MARKERS:
            if marker not in text:
                errors.append(f"{task_spec}: missing marker `{marker}`")
            elif _is_empty_marker_value(text, marker):
                errors.append(f"{task_spec}: marker `{marker}` must not be empty")

    progress_path = path / "progress.json"
    if progress_path.is_file():
        progress = _load_json(progress_path, errors)
        if isinstance(progress, dict):
            for key in (
                "task_id",
                "status",
                "iteration",
                "stale_count",
                "last_progress_at",
                "last_evidence",
                "last_failure_signature",
                "next_safe_action",
            ):
                if key not in progress:
                    errors.append(f"{progress_path}: missing key `{key}`")
            status = progress.get("status")
            if status not in ALLOWED_STATUSES:
                errors.append(f"{progress_path}: status must be one of {', '.join(sorted(ALLOWED_STATUSES))}")
            stale_count = progress.get("stale_count")
            if not isinstance(stale_count, int) or stale_count < 0:
                errors.append(f"{progress_path}: stale_count must be a non-negative integer")
            iteration = progress.get("iteration")
            if not isinstance(iteration, int) or iteration < 0:
                errors.append(f"{progress_path}: iteration must be a non-negative integer")
            last_progress_at = progress.get("last_progress_at")
            if not isinstance(last_progress_at, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", last_progress_at):
                errors.append(f"{progress_path}: last_progress_at must be a non-empty ISO-like timestamp string")
            last_failure_signature = progress.get("last_failure_signature")
            if last_failure_signature is not None and not isinstance(last_failure_signature, str):
                errors.append(f"{progress_path}: last_failure_signature must be null or a string")
        elif progress is not None:
            errors.append(f"{progress_path}: root JSON must be an object")

    directions_path = path / "directions_tried.json"
    if directions_path.is_file():
        directions = _load_json(directions_path, errors)
        if isinstance(directions, dict):
            items = directions.get("directions")
            if not isinstance(items, list):
                errors.append(f"{directions_path}: `directions` must be a list")
            elif not items:
                errors.append(f"{directions_path}: `directions` must include at least one direction or explicit initial placeholder")
        elif directions is not None:
            errors.append(f"{directions_path}: root JSON must be an object")

    gates_path = path / "gates.json"
    if gates_path.is_file():
        gates = _load_json(gates_path, errors)
        if isinstance(gates, dict):
            gate_items = gates.get("gates")
            if not isinstance(gate_items, list) or not gate_items:
                errors.append(f"{gates_path}: `gates` must be a non-empty list")
            else:
                required_gate_seen = False
                for index, gate in enumerate(gate_items, start=1):
                    if not isinstance(gate, dict):
                        errors.append(f"{gates_path}: gate #{index} must be an object")
                        continue
                    for key in ("id", "type", "pass_condition", "required"):
                        if not gate.get(key):
                            errors.append(f"{gates_path}: gate #{index} missing `{key}`")
                    if gate.get("required") is True:
                        required_gate_seen = True
                    elif "required" in gate:
                        errors.append(f"{gates_path}: gate #{index} `required` must be true for Task State Pack gates")
                    if gate.get("type") == "command" and not gate.get("command"):
                        errors.append(f"{gates_path}: command gate #{index} missing `command`")
                    pass_condition = str(gate.get("pass_condition", ""))
                    command = str(gate.get("command", ""))
                    if not _contains_any(pass_condition + " " + command, GATE_PASS_PATTERNS):
                        errors.append(f"{gates_path}: gate #{index} must name a concrete pass/fail or command check")
                    if _contains_any(pass_condition + " " + command, DECORATIVE_GATE_PATTERNS):
                        errors.append(f"{gates_path}: gate #{index} appears decorative rather than enforceable")
                if not required_gate_seen:
                    errors.append(f"{gates_path}: at least one gate must be required")
            human_gates = gates.get("human_gates")
            if not isinstance(human_gates, list):
                errors.append(f"{gates_path}: `human_gates` must be a list, even when empty")
            else:
                if task_spec.is_file():
                    task_spec_text = task_spec.read_text(encoding="utf-8")
                    for gate_id in _missing_human_gate_ids(task_spec_text, human_gates):
                        errors.append(f"{gates_path}: high-risk task language requires `{gate_id}` in `human_gates`")
                for index, gate in enumerate(human_gates, start=1):
                    if not isinstance(gate, str) or not gate.strip():
                        errors.append(f"{gates_path}: human_gates entry #{index} must be a non-empty string")
        elif gates is not None:
            errors.append(f"{gates_path}: root JSON must be an object")

    for name in ("findings.jsonl", "iteration_log.jsonl"):
        jsonl_path = path / name
        if jsonl_path.is_file():
            _lint_jsonl(jsonl_path, errors)

    rollback_path = path / "rollback.md"
    if rollback_path.is_file():
        rollback = rollback_path.read_text(encoding="utf-8")
        if len(rollback.strip()) < 40:
            errors.append(f"{rollback_path}: rollback plan is too thin")
        for marker in ROLLBACK_MARKERS:
            if marker not in rollback:
                errors.append(f"{rollback_path}: missing marker `{marker}`")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: lint_task_state_pack.py <task-state-pack-dir> [<task-state-pack-dir> ...]", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for raw_path in argv[1:]:
        all_errors.extend(lint_pack(Path(raw_path)))

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print("Task State Pack lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
