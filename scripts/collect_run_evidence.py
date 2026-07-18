#!/usr/bin/env python3
"""Collect strict, metadata-only evidence from a Codex rollout JSONL file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from audit_contract import RUN_EVIDENCE_SCHEMA_VERSION


KNOWN_TOP_LEVEL_TYPES = {"session_meta", "turn_context", "event_msg", "response_item", "world_state", "compacted"}
KNOWN_EVENT_TYPES = {
    "agent_message",
    "agent_reasoning",
    "context_compacted",
    "item_completed",
    "mcp_tool_call_end",
    "patch_apply_end",
    "task_complete",
    "task_started",
    "thread_settings_applied",
    "token_count",
    "turn_aborted",
    "user_message",
    "web_search_end",
}
KNOWN_RESPONSE_TYPES = {
    "custom_tool_call",
    "custom_tool_call_output",
    "function_call",
    "function_call_output",
    "message",
    "reasoning",
}
NESTED_TOOL_PATTERN = re.compile(r"\btools\.([A-Za-z][A-Za-z0-9_]*)\s*\(")
SAFE_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_.:@+ -]{1,96}$")


class CollectionError(ValueError):
    """Raised when strict collection cannot produce complete evidence."""


def _digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _digest_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return None
    return _digest_bytes(text.encode("utf-8", errors="replace"))


def _safe_token(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text if SAFE_TOKEN_PATTERN.fullmatch(text) else f"redacted-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}"


def _safe_tool_name(value: Any) -> str:
    safe = _safe_token(value)
    if safe is None:
        return "unknown-tool"
    if safe.startswith("redacted-"):
        return f"unknown-tool-{safe.removeprefix('redacted-')}"
    return safe


def _context_label(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("kind", "type", "mode", "name"):
            if key in value:
                return _safe_token(value[key])
        return "configured"
    return _safe_token(value)


def _as_nonnegative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)) and value >= 0:
        return int(value)
    return 0


def _output_failed(value: Any) -> bool:
    if isinstance(value, dict):
        return bool(value.get("isError") is True or value.get("error") or "Err" in value)
    if isinstance(value, str):
        compact = value.replace(" ", "").lower()
        return '"iserror":true' in compact or '"success":false' in compact
    return False


def _mcp_failed(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    return "Err" in result or result.get("isError") is True or result.get("error") is not None


def collect_run_evidence(path: Path, *, allow_partial: bool = False) -> dict[str, Any]:
    raw = path.read_bytes()
    source_sha256 = _digest_bytes(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CollectionError(f"input is not valid UTF-8: {error}") from error

    invalid_line_count = 0
    unknown_types: Counter[str] = Counter()
    parsed: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            invalid_line_count += 1
            if not allow_partial:
                raise CollectionError(f"malformed JSONL at line {line_number}: {error.msg}") from error
            continue
        if not isinstance(item, dict):
            invalid_line_count += 1
            if not allow_partial:
                raise CollectionError(f"JSONL line {line_number} must be an object")
            continue
        parsed.append(item)

    session_id: Any = None
    cli_version: Any = None
    originator: Any = None
    session_meta_seen = False
    token_usage_seen = False
    contexts: dict[str, dict[str, Any]] = {}
    started_turns: set[str] = set()
    completed_turns: set[str] = set()
    aborted_turns: set[str] = set()
    total_duration_ms = 0
    first_token_values: list[int] = []
    token_usage = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "total_tokens": 0,
    }
    tool_counts: Counter[str] = Counter()
    tool_failures: Counter[str] = Counter()
    call_names: dict[str, str] = {}
    mcp_calls = 0
    failed_mcp_calls = 0
    web_searches = 0
    patch_calls = 0
    failed_patch_calls = 0

    for item in parsed:
        top_type = str(item.get("type", ""))
        if top_type not in KNOWN_TOP_LEVEL_TYPES:
            unknown_types[f"top:{_safe_tool_name(top_type)}"] += 1
            continue
        payload = item.get("payload")
        if not isinstance(payload, dict):
            unknown_types[f"{top_type}:missing-payload"] += 1
            continue

        if top_type == "session_meta":
            session_meta_seen = True
            session_id = session_id or payload.get("session_id") or payload.get("id")
            cli_version = cli_version or payload.get("cli_version")
            originator = originator or payload.get("originator") or payload.get("source")
            continue

        if top_type == "turn_context":
            raw_turn_id = payload.get("turn_id")
            turn_hash = _digest_text(raw_turn_id or f"turn-context-{len(contexts)}")
            assert turn_hash is not None
            contexts[turn_hash] = {
                "turn_id_hash": turn_hash,
                "collaboration_mode": _context_label(payload.get("collaboration_mode")),
                "approval_policy": _context_label(payload.get("approval_policy")),
                "sandbox_mode": _context_label(payload.get("sandbox_policy")),
                "multi_agent_mode": _context_label(payload.get("multi_agent_mode")),
            }
            continue

        if top_type in {"world_state", "compacted"}:
            continue

        payload_type = str(payload.get("type", ""))
        if top_type == "event_msg" and payload_type not in KNOWN_EVENT_TYPES:
            unknown_types[f"event:{_safe_tool_name(payload_type)}"] += 1
            continue
        if top_type == "response_item" and payload_type not in KNOWN_RESPONSE_TYPES:
            unknown_types[f"response:{_safe_tool_name(payload_type)}"] += 1
            continue

        if top_type == "event_msg":
            if payload_type == "task_started":
                started_turns.add(str(payload.get("turn_id") or f"started-{len(started_turns)}"))
            elif payload_type == "task_complete":
                completed_turns.add(str(payload.get("turn_id") or f"completed-{len(completed_turns)}"))
                total_duration_ms += _as_nonnegative_int(payload.get("duration_ms"))
                first_token = _as_nonnegative_int(payload.get("time_to_first_token_ms"))
                if first_token:
                    first_token_values.append(first_token)
            elif payload_type == "turn_aborted":
                aborted_turns.add(str(payload.get("turn_id") or f"aborted-{len(aborted_turns)}"))
                total_duration_ms += _as_nonnegative_int(payload.get("duration_ms"))
            elif payload_type == "token_count":
                info = payload.get("info")
                usage = info.get("total_token_usage") if isinstance(info, dict) else None
                if isinstance(usage, dict):
                    token_usage_seen = True
                    for field in token_usage:
                        token_usage[field] = _as_nonnegative_int(usage.get(field))
            elif payload_type == "mcp_tool_call_end":
                mcp_calls += 1
                invocation = payload.get("invocation")
                server = invocation.get("server") if isinstance(invocation, dict) else None
                tool = invocation.get("tool") if isinstance(invocation, dict) else None
                name = _safe_tool_name(f"mcp::{server or 'unknown'}::{tool or 'unknown'}")
                tool_counts[name] += 1
                if _mcp_failed(payload.get("result")):
                    failed_mcp_calls += 1
                    tool_failures[name] += 1
            elif payload_type == "patch_apply_end":
                patch_calls += 1
                name = "apply_patch"
                tool_counts[name] += 1
                if payload.get("success") is not True:
                    failed_patch_calls += 1
                    tool_failures[name] += 1
            elif payload_type == "web_search_end":
                web_searches += 1
                tool_counts["web_search"] += 1
            continue

        if payload_type in {"custom_tool_call", "function_call"}:
            name = _safe_tool_name(payload.get("name"))
            tool_counts[name] += 1
            call_id = str(payload.get("call_id") or payload.get("id") or "")
            if call_id:
                call_names[call_id] = name
            if str(payload.get("status", "")).lower() in {"failed", "error", "cancelled"}:
                tool_failures[name] += 1
            raw_input = payload.get("input")
            if isinstance(raw_input, str):
                for nested_name in NESTED_TOOL_PATTERN.findall(raw_input):
                    tool_counts[_safe_tool_name(nested_name)] += 1
        elif payload_type in {"custom_tool_call_output", "function_call_output"}:
            call_id = str(payload.get("call_id") or "")
            if call_id and _output_failed(payload.get("output")):
                name = call_names.get(call_id, "unknown-tool-output")
                tool_failures[name] += 1

    critical_issues = []
    if not parsed:
        critical_issues.append("empty-input")
    if not session_meta_seen:
        critical_issues.append("missing-session-meta")
    if not contexts:
        critical_issues.append("missing-turn-context")
    if not started_turns:
        critical_issues.append("missing-task-started")
    if started_turns - completed_turns - aborted_turns:
        critical_issues.append("incomplete-turns")
    if not token_usage_seen:
        critical_issues.append("missing-token-usage")
    for issue in critical_issues:
        unknown_types[f"critical:{issue}"] += 1

    if unknown_types and not allow_partial:
        names = ", ".join(sorted(unknown_types))
        raise CollectionError(f"unknown event structure detected: {names}")

    parse_status = "PARTIAL" if invalid_line_count or unknown_types else "PASS"
    average_first_token = round(sum(first_token_values) / len(first_token_values)) if first_token_values else 0
    tool_usage = [
        {"name": name, "count": count, "failures": min(tool_failures[name], count)}
        for name, count in sorted(tool_counts.items())
    ]
    failed_tool_calls = sum(item["failures"] for item in tool_usage)
    return {
        "schema_version": RUN_EVIDENCE_SCHEMA_VERSION,
        "source_format": "codex_jsonl",
        "source_sha256": source_sha256,
        "redaction": "strict_metadata_v1",
        "parse_status": parse_status,
        "invalid_line_count": invalid_line_count,
        "unknown_event_types": [f"{name} ({count})" for name, count in sorted(unknown_types.items())],
        "session": {
            "session_id_hash": _digest_text(session_id),
            "cli_version": _safe_token(cli_version),
            "originator": _safe_token(originator),
            "turn_count": len(contexts),
        },
        "execution_contexts": [contexts[key] for key in sorted(contexts)],
        "metrics": {
            "turns_started": len(started_turns),
            "turns_completed": len(completed_turns),
            "turns_aborted": len(aborted_turns),
            "total_duration_ms": total_duration_ms,
            "average_time_to_first_token_ms": average_first_token,
            **token_usage,
            "tool_calls": sum(tool_counts.values()),
            "failed_tool_calls": failed_tool_calls,
            "mcp_calls": mcp_calls,
            "failed_mcp_calls": failed_mcp_calls,
            "web_searches": web_searches,
            "patch_calls": patch_calls,
            "failed_patch_calls": failed_patch_calls,
        },
        "tool_usage": tool_usage,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect strict metadata-only evidence from a Codex rollout JSONL file.")
    parser.add_argument("--input", required=True, help="Codex rollout JSONL path.")
    parser.add_argument("--output", help="Optional output JSON path. Defaults to stdout.")
    parser.add_argument("--allow-partial", action="store_true", help="Emit PARTIAL evidence instead of failing closed.")
    args = parser.parse_args(argv)

    try:
        result = collect_run_evidence(Path(args.input), allow_partial=args.allow_partial)
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, CollectionError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
