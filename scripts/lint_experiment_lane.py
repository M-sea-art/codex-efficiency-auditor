#!/usr/bin/env python3
"""Validate Evo-style Experiment Lane contracts for codex-efficiency-auditor."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_MARKERS = [
    "Objective",
    "Metric",
    "Direction",
    "Baseline",
    "Candidate directions",
    "Gates",
    "Allowed paths",
    "Forbidden paths",
    "Shared locks",
    "Human gates",
    "Rollback",
    "Decision rule",
]

SUBJECTIVE_METRIC_PATTERNS = [
    r"\blooks?\s+good\b",
    r"\bfeel(s)?\b",
    r"\baesthetic\b",
    r"\bvisual taste\b",
    r"\bbrand feel\b",
    r"好看",
    r"审美",
    r"感觉",
    r"江湖感",
    r"更好",
]

VAGUE_PATTERNS = [
    r"make it better",
    r"improve everything",
    r"whatever works",
    r"no gate",
    r"gate:\s*(none|n/a|not needed)",
    r"随便",
    r"都可以",
    r"无需验证",
    r"不需要\s*gate",
]

UNAUTHORIZED_PATTERNS = [
    r"auto[- ]?publish",
    r"publish without (approval|confirmation|authorization)",
    r"auto[- ]?push",
    r"push without (approval|confirmation|authorization)",
    r"auto[- ]?deploy",
    r"deploy without (approval|confirmation|authorization)",
    r"auto[- ]?delete",
    r"delete without (approval|confirmation|authorization)",
    r"auto[- ]?reset",
    r"reset without (approval|confirmation|authorization)",
    r"自动公开",
    r"直接公开",
    r"自动发布",
    r"直接发布",
    r"自动推送",
    r"直接推送",
    r"自动部署",
    r"直接部署",
    r"自动删除",
    r"直接删除",
    r"自动重置",
    r"直接重置",
    r"auto[- ]?(use|read|rotate|change|store).*(credential|secret|token|api[_ -]?key)",
    r"(use|read|rotate|change|store).*(credential|secret|token|api[_ -]?key).*(without|no approval|no confirmation|no authorization)",
    r"auto[- ]?(bill|charge|pay|purchase|subscribe)",
    r"(billing|paid service|payment|purchase|subscription).*(without|no approval|no confirmation|no authorization)",
    r"auto[- ]?(account|permission|role|oauth)",
    r"(account|permission|role|oauth).*(without|no approval|no confirmation|no authorization)",
    r"auto[- ]?(comment|reply|post|email|message)",
    r"(comment|reply|post|email|message).*(without|no approval|no confirmation|no authorization)",
    r"(自动|直接).*(凭证|密钥|令牌|token|api key|api_key)",
    r"(自动|直接).*(付费|付款|订阅|扣费|账单)",
    r"(自动|直接).*(账号|账户|权限|授权|oauth)",
    r"(自动|直接).*(评论|回复|发帖|邮件|消息)",
    r"未经(批准|确认|授权).*(凭证|密钥|令牌|token|api key|api_key|付费|付款|订阅|账号|账户|评论|回复|发帖|邮件|消息)",
]

UNSUITABLE_EXPERIMENT_PATTERNS = [
    r"\blegal\s+(judg(e)?ment|advice|decision|claim)\b",
    r"\bmedical\s+(judg(e)?ment|advice|decision|diagnosis)\b",
    r"\bfinancial\s+(judg(e)?ment|advice|decision|recommendation)\b",
    r"\bcompliance\s+(judg(e)?ment|decision|claim)\b",
    r"\bcopyright\s+(decision|claim|ownership)\b",
    r"\bownership\s+(decision|claim)\b",
    r"法律(判断|建议|结论)",
    r"医疗(判断|建议|诊断)",
    r"金融(判断|建议|结论)",
    r"合规(判断|结论)",
    r"版权(判断|归属|结论)",
    r"所有权(判断|归属|结论)",
]

HIGH_RISK_GATE_PATTERNS = [
    ("G1_PUSH", [r"\bpush\b", r"\bgit\s+push\b", r"推送"]),
    ("G2_PUBLISH", [r"\bpublish\b", r"\brelease\b", r"\bpublic\b", r"公开", r"发布"]),
    ("G3_DEPLOY", [r"\bdeploy\b", r"\bdeployment\b", r"部署"]),
    (
        "G4_ACCOUNT",
        [
            r"\bcredential(s)?\b",
            r"\bsecret(s)?\b",
            r"\btoken(s)?\b",
            r"\bapi[_ -]?key(s)?\b",
            r"\bbilling\b",
            r"\bpaid service(s)?\b",
            r"\bpayment(s)?\b",
            r"\baccount(s)?\b",
            r"\bpermission(s)?\b",
            r"\boauth\b",
            r"凭证",
            r"密钥",
            r"令牌",
            r"付费",
            r"付款",
            r"账单",
            r"账号",
            r"账户",
            r"权限",
            r"授权",
        ],
    ),
    ("G5_DESTRUCTIVE", [r"\bdelete\b", r"\breset\b", r"\boverwrite\b", r"\bmigration\b", r"删除", r"重置", r"覆盖", r"迁移"]),
    ("G6_EXTERNAL_COMMENT", [r"\bcomment\b", r"\breply\b", r"\bpost\b", r"\bemail\b", r"\bmessage\b", r"评论", r"回复", r"发帖", r"邮件", r"消息"]),
]


MARKER_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?P<marker>"
    + "|".join(re.escape(marker) for marker in sorted(REQUIRED_MARKERS, key=len, reverse=True))
    + r")\s*[:：]\s*(?P<rest>.*)$",
    flags=re.IGNORECASE,
)


def _canonical_marker(raw_marker: str) -> str | None:
    for marker in REQUIRED_MARKERS:
        if raw_marker.casefold() == marker.casefold():
            return marker
    return None


def _section_map(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_marker: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_marker, current_lines
        if current_marker is not None:
            sections[current_marker] = "\n".join(current_lines).strip()
        current_marker = None
        current_lines = []

    for line in text.splitlines():
        match = MARKER_RE.match(line)
        if match:
            flush()
            current_marker = _canonical_marker(match.group("marker"))
            rest = match.group("rest").strip()
            current_lines = [rest] if rest else []
            continue
        if current_marker is not None:
            current_lines.append(line.rstrip())

    flush()
    return sections


def _content_for_marker(text: str, marker: str) -> str | None:
    content = _section_map(text).get(marker)
    if content and content.strip():
        return content.strip()
    return None


def _has_marker(text: str, marker: str) -> bool:
    return _content_for_marker(text, marker) is not None


def _has_any(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def _missing_human_gate_ids(text: str, human_gates: str | None) -> list[str]:
    if not human_gates:
        return []
    missing: list[str] = []
    for gate_id, patterns in HIGH_RISK_GATE_PATTERNS:
        if _has_any(patterns, text) and gate_id not in human_gates:
            missing.append(gate_id)
    return missing


def lint_text(text: str, source: str) -> list[str]:
    errors: list[str] = []

    if "Experiment Lane" not in text:
        errors.append(f"{source}: missing `Experiment Lane` heading or label")

    for marker in REQUIRED_MARKERS:
        if not _has_marker(text, marker):
            errors.append(f"{source}: missing required marker `{marker}:`")

    direction = _content_for_marker(text, "Direction")
    if direction and not re.search(r"\b(max|min)\b", direction, flags=re.IGNORECASE):
        errors.append(f"{source}: Direction must be `max` or `min`")

    objective = _content_for_marker(text, "Objective")
    metric = _content_for_marker(text, "Metric")
    baseline = _content_for_marker(text, "Baseline")
    candidates = _content_for_marker(text, "Candidate directions")
    if metric:
        if len(metric) < 8:
            errors.append(f"{source}: Metric is too thin")
        if _has_any(SUBJECTIVE_METRIC_PATTERNS, metric):
            errors.append(f"{source}: subjective metric is not suitable for Experiment Lane")

    gates = _content_for_marker(text, "Gates")
    if gates:
        if not re.search(r"(exit code|pass|fail|pytest|test|lint|typecheck|build|check|验证|通过|失败)", gates, flags=re.IGNORECASE):
            errors.append(f"{source}: Gates must name a concrete pass/fail check")

    forbidden = _content_for_marker(text, "Forbidden paths")
    if forbidden and re.search(r"^(none|n/a|not applicable|无|没有)$", forbidden, flags=re.IGNORECASE):
        errors.append(f"{source}: Forbidden paths must be explicit, not empty")

    human_gates = _content_for_marker(text, "Human gates")
    if human_gates and not re.search(r"(G[1-6]_|APPROVED|Human Gate|human review|人工|批准|确认)", human_gates, flags=re.IGNORECASE):
        errors.append(f"{source}: Human gates must name explicit gates or human review")
    for gate_id in _missing_human_gate_ids(text, human_gates):
        errors.append(f"{source}: high-risk action mentions `{gate_id}` scope but Human gates does not name `{gate_id}`")

    decision = _content_for_marker(text, "Decision rule")
    if decision and not re.search(r"(metric|gate|pass|fail|discard|keep|指标|门禁|通过|失败|丢弃|保留)", decision, flags=re.IGNORECASE):
        errors.append(f"{source}: Decision rule must combine metric and gate outcomes")

    suitability_text = "\n".join(item for item in (objective, metric, baseline, candidates, gates, decision) if item)
    if _has_any(UNSUITABLE_EXPERIMENT_PATTERNS, suitability_text):
        errors.append(f"{source}: legal, medical, financial, compliance, copyright, or ownership judgment is not suitable for Experiment Lane")

    for pattern in VAGUE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{source}: vague or ungated instruction matched `{pattern}`")

    for pattern in UNAUTHORIZED_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{source}: high-risk action must stop at a Human Gate; matched `{pattern}`")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: lint_experiment_lane.py <file> [<file> ...]", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for raw_path in argv[1:]:
        path = Path(raw_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            all_errors.append(f"{path}: cannot read file: {exc}")
            continue
        all_errors.extend(lint_text(text, str(path)))

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print("Experiment Lane lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
