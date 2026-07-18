#!/usr/bin/env python3
"""Documentation discoverability and contract-drift checks."""

from __future__ import annotations

from pathlib import Path

from audit_contract import AVAILABILITY_TYPES, CLAIM_SCOPES, UPGRADE_ROUTES


ROOT = Path(__file__).resolve().parents[1]


def test_first_success_routes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for label in (
        "Choose Your Path",
        "选择你的路径",
        "codexcavator.py audit",
        "codexcavator.py compare",
        "codexcavator.py collect",
        "codexcavator.py migrate",
        "codexcavator.py inventory",
    ):
        assert label in readme, label
    assert "python -m compileall -q scripts" in readme
    assert "python -m py_compile scripts/*.py" not in readme
    for error_code in (
        "FILE_NOT_FOUND",
        "JSON_INVALID",
        "AUDIT_SCHEMA_INVALID",
        "ROLLOUT_PARSE_FAILED",
        "V02_MIGRATION_REQUIRED",
    ):
        assert error_code in readme, error_code


def test_contract_docs_are_current() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    templates = (ROOT / "references" / "report-templates.md").read_text(encoding="utf-8")
    documents = {"README.md": readme, "SKILL.md": skill, "references/report-templates.md": templates}
    for name, document in documents.items():
        assert "Schema version: 0.2" not in document, name
    assert "Smallest action:" not in templates
    assert "   - Verification:" not in templates
    for name, document in documents.items():
        for value in (*AVAILABILITY_TYPES, *CLAIM_SCOPES, *UPGRADE_ROUTES):
            assert value in document, f"{value} missing from {name}"
    for label in ("Scope conformance:", "smallest_useful_check", "Next action:"):
        assert label in templates, label


def test_quickstart_fixture_is_sanitized() -> None:
    raw = (ROOT / "examples" / "quickstart" / "minimal-rollout.jsonl").read_text(encoding="utf-8")
    for marker in ("C:\\Users\\", "/home/", "SUPER_SECRET", "auth.json", "private-project"):
        assert marker.lower() not in raw.lower(), marker


def main() -> int:
    test_first_success_routes()
    test_contract_docs_are_current()
    test_quickstart_fixture_is_sanitized()
    print("documentation UX and contract-drift checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
