#!/usr/bin/env python3
"""Regression and privacy checks for strict Codex JSONL evidence collection."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from collect_run_evidence import CollectionError, collect_run_evidence
from score_audit import validate_run_evidence


SECRET = "SUPER_SECRET_TOKEN_123"
PRIVATE_PATH = "C:\\Users\\Private\\sensitive-project"
PRIVATE_POSIX_PATH = "/home/private/sensitive-project"


def _line(top_type: str, payload: dict[str, object]) -> str:
    return json.dumps({"type": top_type, "payload": payload}, ensure_ascii=False)


def _fixture_lines() -> list[str]:
    return [
        _line(
            "session_meta",
            {
                "id": "raw-session-id",
                "cli_version": "codex-cli 0.3",
                "originator": PRIVATE_POSIX_PATH,
                "cwd": PRIVATE_PATH,
                "base_instructions": SECRET,
            },
        ),
        _line(
            "turn_context",
            {
                "turn_id": "raw-turn-id",
                "collaboration_mode": {"kind": "default"},
                "approval_policy": "never",
                "sandbox_policy": {"type": "danger-full-access", "writable_roots": [PRIVATE_PATH]},
                "multi_agent_mode": "disabled",
                "cwd": PRIVATE_PATH,
            },
        ),
        _line("event_msg", {"type": "task_started", "turn_id": "raw-turn-id"}),
        _line(
            "response_item",
            {
                "type": "custom_tool_call",
                "call_id": "raw-call-id",
                "name": "exec",
                "status": "completed",
                "input": f'await tools.shell_command({{command: "echo {SECRET} {PRIVATE_PATH}"}})',
            },
        ),
        _line(
            "response_item",
            {
                "type": "custom_tool_call_output",
                "call_id": "raw-call-id",
                "output": f"successful output {SECRET} {PRIVATE_PATH}",
            },
        ),
        _line(
            "event_msg",
            {
                "type": "mcp_tool_call_end",
                "call_id": "raw-mcp-id",
                "duration": 12,
                "invocation": {"server": "codegraph", "tool": "search_graph", "arguments": {"query": SECRET}},
                "result": {"Ok": {"content": SECRET}},
            },
        ),
        _line("event_msg", {"type": "patch_apply_end", "call_id": "raw-patch", "success": True, "changes": [PRIVATE_PATH]}),
        _line("event_msg", {"type": "web_search_end", "call_id": "raw-search", "query": SECRET}),
        _line(
            "event_msg",
            {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": 100,
                        "cached_input_tokens": 20,
                        "output_tokens": 40,
                        "reasoning_output_tokens": 10,
                        "total_tokens": 140,
                    }
                },
            },
        ),
        _line(
            "event_msg",
            {
                "type": "task_complete",
                "turn_id": "raw-turn-id",
                "duration_ms": 2500,
                "time_to_first_token_ms": 125,
                "last_agent_message": SECRET,
            },
        ),
        _line("event_msg", {"type": "task_started", "turn_id": "other-turn"}),
        _line("event_msg", {"type": "turn_aborted", "turn_id": "other-turn", "duration_ms": 500, "reason": SECRET}),
        _line("world_state", {"state": {"secret": SECRET}}),
        _line("compacted", {"message": SECRET}),
    ]


def test_complete_collection_and_privacy() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "rollout.jsonl"
        path.write_text("\n".join(_fixture_lines()) + "\n", encoding="utf-8")
        result = collect_run_evidence(path)
    validate_run_evidence(result)
    rendered = json.dumps(result, ensure_ascii=False)
    for forbidden in (SECRET, PRIVATE_PATH, PRIVATE_POSIX_PATH, "raw-session-id", "raw-turn-id", "raw-call-id", "echo"):
        assert forbidden not in rendered, forbidden
    assert result["parse_status"] == "PASS"
    assert result["session"]["session_id_hash"].startswith("sha256:")
    assert result["execution_contexts"][0]["sandbox_mode"] == "danger-full-access"
    assert result["metrics"]["total_duration_ms"] == 3000
    assert result["metrics"]["total_tokens"] == 140
    assert result["metrics"]["mcp_calls"] == 1
    assert result["metrics"]["patch_calls"] == 1
    assert result["metrics"]["web_searches"] == 1
    tool_names = {item["name"] for item in result["tool_usage"]}
    assert {"exec", "shell_command", "mcp::codegraph::search_graph", "apply_patch", "web_search"} <= tool_names


def test_malformed_and_unknown_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        malformed = Path(directory) / "malformed.jsonl"
        malformed.write_text(_fixture_lines()[0] + "\n{not-json\n", encoding="utf-8")
        try:
            collect_run_evidence(malformed)
        except CollectionError as error:
            assert "malformed JSONL" in str(error)
        else:
            raise AssertionError("malformed JSONL should fail closed")
        partial = collect_run_evidence(malformed, allow_partial=True)
        assert partial["parse_status"] == "PARTIAL"
        assert partial["invalid_line_count"] == 1

        unknown = Path(directory) / "unknown.jsonl"
        unknown.write_text(_line("event_msg", {"type": "future_event", "secret": SECRET}) + "\n", encoding="utf-8")
        try:
            collect_run_evidence(unknown)
        except CollectionError as error:
            assert "unknown event structure" in str(error)
        else:
            raise AssertionError("unknown event type should fail closed")
        partial_unknown = collect_run_evidence(unknown, allow_partial=True)
        assert partial_unknown["parse_status"] == "PARTIAL"
        assert "event:future_event (1)" in partial_unknown["unknown_event_types"]
        assert SECRET not in json.dumps(partial_unknown)


def main() -> int:
    test_complete_collection_and_privacy()
    test_malformed_and_unknown_fail_closed()
    print("strict run evidence regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
