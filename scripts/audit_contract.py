#!/usr/bin/env python3
"""Shared constants for the codex-efficiency-auditor v0.3 audit contract."""

from __future__ import annotations


SCHEMA_VERSION = "0.3"
RUN_EVIDENCE_SCHEMA_VERSION = "0.3"

RELEVANCE_MULTIPLIER = {"required": 1.0, "useful": 0.6, "irrelevant": 0.0}
AVAILABILITY_TYPES = {
    "available_in_session",
    "installed_not_exposed",
    "disabled",
    "unavailable",
    "unknown",
}
USAGE_TYPES = {"used", "unused", "misused", "not_applicable"}
TARGET_TYPES = {"thread", "repo", "worktree", "pr", "agent_run", "transcript"}
AUDIT_MUTATION_STATUSES = {"NO_FILES_MODIFIED_BY_AUDIT", "MUTATION_DETECTED", "UNKNOWN"}
GAP_TYPES = {"UNAVAILABLE", "UNDISCOVERED", "UNUSED", "MISUSED", "UNVERIFIED"}
GAP_SEVERITY = {None: 0, "UNVERIFIED": 1, "MISUSED": 2, "UNUSED": 3, "UNDISCOVERED": 4, "UNAVAILABLE": 5}

TASK_MODES = {"answer", "plan", "diagnose", "implement", "review", "monitor", "unknown"}
LOCAL_MUTATION_SCOPES = {"none", "project", "host", "unknown"}
EXTERNAL_ACTION_POLICIES = {"forbidden", "human_gate", "authorized", "unknown"}
CONFORMANCE_STATUSES = {"PASS", "FAIL", "UNKNOWN"}

EVIDENCE_KINDS = {
    "command",
    "test",
    "build",
    "ci",
    "git",
    "trace",
    "runtime",
    "screenshot",
    "artifact",
    "human",
    "other",
}
EVIDENCE_STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_EVALUATED"}
CLAIM_SCOPES = {
    "capability_use",
    "functional",
    "visual",
    "domain",
    "integrity",
    "human_acceptance",
    "authorization",
    "efficiency",
    "other",
}

UPGRADE_ROUTES = {"REUSE", "NATIVE", "INSTALLED", "BUILD", "DISCOVER_FIRST", "HUMAN_GATE"}
COMPARISON_RESULTS = {
    "PROVEN",
    "UTILIZATION_IMPROVED_OUTCOME_UNPROVEN",
    "REGRESSION",
    "INCONCLUSIVE",
    "NO_CHANGE",
}

METRIC_NAMES = {
    "total_duration_ms",
    "average_time_to_first_token_ms",
    "total_tokens",
    "failed_tool_calls",
    "turns_aborted",
}
METRIC_DIRECTIONS = {"lower", "higher"}
THRESHOLD_KINDS = {"absolute", "relative"}

RUN_SOURCE_FORMATS = {"codex_jsonl"}
RUN_REDACTION_MODES = {"strict_metadata_v1"}
RUN_PARSE_STATUSES = {"PASS", "PARTIAL"}
RUN_METRIC_FIELDS = {
    "turns_started",
    "turns_completed",
    "turns_aborted",
    "total_duration_ms",
    "average_time_to_first_token_ms",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
    "tool_calls",
    "failed_tool_calls",
    "mcp_calls",
    "failed_mcp_calls",
    "web_searches",
    "patch_calls",
    "failed_patch_calls",
}

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "audit_id",
    "target_type",
    "goal",
    "operation_contract",
    "scope_conformance",
    "audit_mutation_status",
    "run_evidence",
    "outcomes",
    "efficiency_metrics",
    "capabilities",
    "upgrades",
}
TOP_LEVEL_OPTIONAL = {"migration"}
OPERATION_CONTRACT_REQUIRED = {
    "task_mode",
    "local_mutation_scope",
    "external_actions",
    "constraints",
    "human_gates",
}
SCOPE_CONFORMANCE_REQUIRED = {"status", "evidence"}
CAPABILITY_REQUIRED = {"name", "relevance", "availability", "discovered", "usage", "impact", "evidence"}
EVIDENCE_REQUIRED = {"kind", "status", "claim_scope", "summary"}
EVIDENCE_OPTIONAL = {"locator"}
OUTCOME_REQUIRED = {"id", "description", "required", "claim_scope", "status", "evidence"}
EFFICIENCY_METRIC_REQUIRED = {"name", "direction", "threshold"}
THRESHOLD_REQUIRED = {"kind", "value"}
UPGRADE_REQUIRED = {
    "capability",
    "gap",
    "route",
    "action",
    "expected_gain",
    "smallest_useful_check",
    "human_gate",
}
UPGRADE_OPTIONAL = {"human_gate_reason"}

RUN_EVIDENCE_REQUIRED = {
    "schema_version",
    "source_format",
    "source_sha256",
    "redaction",
    "parse_status",
    "invalid_line_count",
    "unknown_event_types",
    "session",
    "execution_contexts",
    "metrics",
    "tool_usage",
}
RUN_SESSION_REQUIRED = {"session_id_hash", "cli_version", "originator", "turn_count"}
RUN_CONTEXT_REQUIRED = {"turn_id_hash", "collaboration_mode", "approval_policy", "sandbox_mode", "multi_agent_mode"}
RUN_TOOL_USAGE_REQUIRED = {"name", "count", "failures"}
