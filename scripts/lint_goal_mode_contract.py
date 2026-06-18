#!/usr/bin/env python3
"""Validate Goal Mode Contract drafts for codex-efficiency-auditor."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_MARKER_GROUPS = [
    ("command", [r"/goal"]),
    ("verification", [r"Verification[:：]", r"验证[:：]"]),
    ("constraints", [r"Constraints[:：]", r"约束[:：]"]),
    ("boundaries", [r"Boundaries[:：]", r"边界[:：]"]),
    ("iteration policy", [r"Iteration policy[:：]", r"迭代策略[:：]"]),
    ("stop when", [r"Stop when[:：]", r"完成条件[:：]", r"停止条件[:：]"]),
    ("pause if", [r"Pause if[:：]", r"暂停条件[:：]", r"阻塞条件[:：]"]),
    ("polling audit", [r"Polling audit[:：]", r"轮询审计[:：]"]),
    ("human intervention", [r"Human intervention triggers[:：]", r"人工介入触发[:：]", r"人工介入[:：]"]),
    ("final report", [r"Final report format[:：]", r"最终报告格式[:：]", r"最终报告[:：]"]),
]

PLACEHOLDER_PATTERNS = [
    r"\[[^\]]+\]",
    r"\bTBD\b",
    r"\bTODO\b",
    r"<[^>]+>",
    r"待补充",
    r"待定",
]

VAGUE_OR_RISKY_PATTERNS = [
    r"make sure it works",
    r"edit anything",
    r"change whatever",
    r"keep trying",
    r"until it (looks|seems|feels) good",
    r"随便改",
    r"随意修改",
    r"一直尝试",
    r"持续尝试",
    r"直到满意",
    r"看起来不错就行",
    r"感觉可以",
    r"全盘修改",
]

UNAUTHORIZED_ACTION_PATTERNS = [
    r"自动公开",
    r"直接公开",
    r"无需确认.*公开",
    r"无需确认.*发布",
    r"自动发布",
    r"直接发布",
    r"自动删除",
    r"直接删除",
    r"自动重置",
    r"直接重置",
    r"自动推送",
    r"直接推送",
    r"使用凭证",
    r"使用付费",
    r"use credentials",
    r"use paid",
    r"publish without (approval|confirmation|authorization)",
    r"deploy without (approval|confirmation|authorization)",
    r"delete without (approval|confirmation|authorization)",
    r"reset without (approval|confirmation|authorization)",
    r"push without (approval|confirmation|authorization)",
]

VERIFICATION_EVIDENCE_PATTERNS = [
    r"\b(run|start|open|test|build|lint|typecheck|verify|inspect|capture|screenshot|log|artifact|file|url|api|browser|local|ci|pr)\b",
    r"(运行|启动|打开|测试|构建|检查|验证|读取|截图|日志|产物|文件|链接|接口|浏览器|本地|证据|CI|PR)",
]

BOUNDARY_PATTERNS = [
    r"(owned paths|allowed paths|forbidden paths|shared locks|read-only|worktree|branch)",
    r"(允许|禁止|边界|共享锁|只读|路径|目录|worktree|分支)",
]

PAUSE_EVIDENCE_PATTERNS = [
    r"(credential|payment|production|destructive|release|deploy|account|legal|medical|financial|copyright|ownership|scope)",
    r"(凭证|付费|生产|破坏性|公开|发布|部署|账号|法律|医疗|金融|版权|所有权|范围)",
]


def _has_any(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def _marker_content(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(rf"^\s*{pattern}\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None


def lint_text(text: str, source: str) -> list[str]:
    errors: list[str] = []

    if re.search(r"^\s*/目标\b", text, flags=re.MULTILINE):
        errors.append(f"{source}: use `/goal`, not `/目标`, as the executable command")

    for name, patterns in REQUIRED_MARKER_GROUPS:
        if not _has_any(patterns, text):
            labels = " or ".join(pattern.replace(r"[:：]", ":") for pattern in patterns)
            errors.append(f"{source}: missing required marker `{labels}` for {name}")

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{source}: unresolved placeholder matched `{pattern}`")

    for pattern in VAGUE_OR_RISKY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{source}: vague or unbounded instruction matched `{pattern}`")

    for pattern in UNAUTHORIZED_ACTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{source}: high-risk action must be paused for human authorization; matched `{pattern}`")

    goal_line = next((line.strip() for line in text.splitlines() if line.strip().startswith("/goal")), "")
    if goal_line and len(goal_line.removeprefix("/goal").strip()) < 20:
        errors.append(f"{source}: /goal outcome is too short to be actionable")

    verification = _marker_content(text, REQUIRED_MARKER_GROUPS[1][1])
    if verification and not _has_any(VERIFICATION_EVIDENCE_PATTERNS, verification):
        errors.append(f"{source}: verification should name concrete commands, checks, logs, screenshots, artifacts, browser checks, CI, PR state, or files")

    boundaries = _marker_content(text, REQUIRED_MARKER_GROUPS[3][1])
    if boundaries and not _has_any(BOUNDARY_PATTERNS, boundaries):
        errors.append(f"{source}: boundaries should name allowed paths, forbidden paths, shared locks, read-only areas, branches, or worktrees")

    pause = _marker_content(text, REQUIRED_MARKER_GROUPS[6][1])
    if pause and not _has_any(PAUSE_EVIDENCE_PATTERNS, pause):
        errors.append(f"{source}: pause conditions should include high-risk triggers or human decision points")

    for name, patterns in REQUIRED_MARKER_GROUPS[1:]:
        content = _marker_content(text, patterns)
        if content and len(content) < 12:
            errors.append(f"{source}: `{name}` content is too thin")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: lint_goal_mode_contract.py <file> [<file> ...]", file=sys.stderr)
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

    print("Goal mode contract lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
