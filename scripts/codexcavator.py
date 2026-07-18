#!/usr/bin/env python3
"""Unified, non-breaking Codexcavator command-line experience."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import audit_codex_capabilities
from cli_support import CliFailure, classify_error, emit_error, render_audit, render_comparison
from collect_run_evidence import CollectionError, collect_run_evidence
from migrate_audit import migrate_audit
from score_audit import analyze_audit, compare_audits, load_audit


class UXArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliFailure(
            "ARGUMENT_ERROR",
            "The command arguments are invalid. Use help to see the supported form.",
            "python scripts/codexcavator.py --help",
        )


def _emit_json(value: Any) -> None:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _require_v03(data: dict[str, Any]) -> None:
    if data.get("schema_version") == "0.2":
        raise CliFailure(
            "V02_MIGRATION_REQUIRED",
            "This is a v0.2 audit; it must be migrated before v0.3 scoring.",
            "python scripts/codexcavator.py migrate --help",
        )


def _audit(args: argparse.Namespace) -> int:
    audit = load_audit(args.audit)
    _require_v03(audit)
    result = analyze_audit(audit)
    if args.json_output:
        _emit_json(result)
    else:
        sys.stdout.write(render_audit(result) + "\n")
    return 0


def _compare(args: argparse.Namespace) -> int:
    baseline = load_audit(args.before)
    candidate = load_audit(args.after)
    _require_v03(baseline)
    _require_v03(candidate)
    result = compare_audits(baseline, candidate)
    if args.json_output:
        _emit_json(result)
    else:
        sys.stdout.write(render_comparison(result) + "\n")
    return 0


def _collect(args: argparse.Namespace) -> int:
    result = collect_run_evidence(Path(args.input), allow_partial=args.allow_partial)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


def _migrate(args: argparse.Namespace) -> int:
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(source, dict):
        raise ValueError("input must be a JSON object")
    rendered = json.dumps(migrate_audit(source), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


def _inventory(args: argparse.Namespace) -> int:
    legacy_args = ["audit_codex_capabilities.py"]
    if args.codex_home:
        legacy_args.extend(["--codex-home", args.codex_home])
    for context in args.context or []:
        legacy_args.extend(["--context", context])
    if args.session_capabilities:
        legacy_args.extend(["--session-capabilities", args.session_capabilities])
    if args.full:
        legacy_args.append("--full")
    if args.json_output:
        legacy_args.append("--json")
    captured_error = io.StringIO()
    with contextlib.redirect_stderr(captured_error):
        result = audit_codex_capabilities.main(legacy_args)
    if result != 0:
        raise CliFailure(
            "AUDIT_SCHEMA_INVALID",
            "The session capability input does not satisfy the inventory contract.",
            "python scripts/codexcavator.py inventory --help",
        )
    return result


def build_parser() -> UXArgumentParser:
    parser = UXArgumentParser(
        description="Audit Codex capability use, collect private metadata, and prove task improvement.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Validate and score one strict v0.3 audit.")
    audit.add_argument("audit", help="Path to an audit v0.3 JSON file.")
    audit.add_argument("--json", action="store_true", dest="json_output", help="Emit machine-readable JSON.")
    audit.set_defaults(handler=_audit)

    compare = subparsers.add_parser("compare", help="Compare compatible before and after audits.")
    compare.add_argument("--before", required=True, help="Baseline v0.3 audit JSON path.")
    compare.add_argument("--after", required=True, help="Candidate v0.3 audit JSON path.")
    compare.add_argument("--json", action="store_true", dest="json_output", help="Emit machine-readable JSON.")
    compare.set_defaults(handler=_compare)

    collect = subparsers.add_parser("collect", help="Collect strict metadata-only evidence from Codex JSONL.")
    collect.add_argument("--input", required=True, help="Codex rollout JSONL path.")
    collect.add_argument("--output", help="Optional output JSON path. Defaults to stdout.")
    collect.add_argument(
        "--allow-partial",
        action="store_true",
        help="Diagnostic only: emit PARTIAL evidence that cannot support PROVEN.",
    )
    collect.set_defaults(handler=_collect)

    migrate = subparsers.add_parser("migrate", help="Migrate a v0.2 audit to strict v0.3.")
    migrate.add_argument("--input", required=True, help="v0.2 audit JSON path.")
    migrate.add_argument("--output", help="Optional v0.3 output path. Defaults to stdout.")
    migrate.set_defaults(handler=_migrate)

    inventory = subparsers.add_parser("inventory", help="Scan local Codex capability availability read-only.")
    inventory.add_argument("--codex-home", help="Override CODEX_HOME for the read-only scan.")
    inventory.add_argument("--context", action="append", help="Task goal or constraints used for relevance ranking.")
    inventory.add_argument("--session-capabilities", help="Explicit current-session capability JSON file.")
    inventory.add_argument("--full", action="store_true", help="Print the full inventory.")
    inventory.add_argument("--json", action="store_true", dest="json_output", help="Emit machine-readable JSON.")
    inventory.set_defaults(handler=_inventory)
    return parser


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    json_output = "--json" in raw_args
    command = raw_args[0] if raw_args and raw_args[0] in {"audit", "compare", "collect", "migrate", "inventory"} else ""
    try:
        args = build_parser().parse_args(raw_args)
        return args.handler(args)
    except (CliFailure, CollectionError, OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        failure = classify_error(error, command or "", rollout=command == "collect")
        return emit_error(failure, json_output=json_output)


if __name__ == "__main__":
    raise SystemExit(main())
