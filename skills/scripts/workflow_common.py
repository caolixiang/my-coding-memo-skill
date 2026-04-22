#!/usr/bin/env python3
"""Shared helpers for the coding memo workflow skill."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

SKILL_NAME = "my-coding-memo-skill"
GENERATED_MARKER = "<!-- generated-by: my-coding-memo-skill -->"
AGENTS_START_MARKER = "<!-- my-coding-memo-skill:start -->"
AGENTS_END_MARKER = "<!-- my-coding-memo-skill:end -->"
CLAUDE_START_MARKER = "<!-- my-coding-memo-skill:claude:start -->"
CLAUDE_END_MARKER = "<!-- my-coding-memo-skill:claude:end -->"
LEGACY_GENERATED_MARKERS = ("<!-- generated-by: coding-memo-workflow -->",)
LEGACY_AGENTS_MARKER_PAIRS = (
    ("<!-- coding-memo-workflow:start -->", "<!-- coding-memo-workflow:end -->"),
)

PLAN_TEMPLATE_BODY = """# Today's Goals

- 

## Scope

- In:
- Out:

## Phase Plan

### Phase 1 - <title>

- Goal:
- Changes:
- Acceptance:
- Status: pending | in_progress | done

## Phase Acceptance Log

### Phase 1

- Result:
- Evidence:
- Notes:

## Test Log

- `<command>`:

## Commit Log

- `<commit_hash>` - 

## Exception Log

- None

## Tomorrow Plan

- 
"""

MEMO_TEMPLATE_BODY = """# YYYYMMDD Memo

## Items

- [HH:mm] Item:

## Commits

- `<commit_hash>`:

## Notes

- None
"""

AGENTS_WORKFLOW_BODY = """## Coding Memo Workflow

### Instruction Priority And Exceptions

1. Treat platform and runtime constraints as higher priority than this workflow.
2. Treat direct developer instructions as higher priority than this workflow.
3. If a higher-priority instruction conflicts with this workflow, call out the conflict before proceeding.
4. Record every approved exception in today's `docs/plan/YYYYMMDD.md` under `## Exception Log`.

### Workflow Files

- Store plan files at `docs/plan/YYYYMMDD.md`.
- Store memo files at `docs/memo/YYYYMMDD.md`.
- Keep reusable templates at `docs/plan/TEMPLATE.md` and `docs/memo/TEMPLATE.md`.
- Use the user's timezone for every `YYYYMMDD` value unless the user explicitly requests a different timezone.

### Daily Operating Rules

1. Read the latest plan in `docs/plan/` and the latest memo in `docs/memo/` before resuming work, especially after context compression or a new conversation.
2. Create today's plan and memo files before implementation when they do not already exist.
3. Execute work in numbered phases, even if the task only needs one phase.
4. Keep each phase scoped, implemented, accepted, and logged separately.
5. Create one code commit after each completed phase unless the user explicitly says not to commit.
6. Update today's plan and memo after each phase commit with the commit hash and summary, but do not create a same-day follow-up commit just for those doc updates.
7. On the next workday, create a docs-only rollover commit for the previous day's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` if they still have uncommitted changes.
8. Record tests, exceptions, and follow-up work in today's plan.

### Plan Requirements

The daily plan file must include:

- `# Today's Goals`
- `## Scope`
- `## Phase Plan`
- `## Phase Acceptance Log`
- `## Test Log`
- `## Commit Log`
- `## Exception Log`
- `## Tomorrow Plan`

### Memo Requirements

The daily memo file must include:

- `# YYYYMMDD Memo`
- `## Items`
- `## Commits`
- `## Notes`

### Commit Rules

1. Finish phase self-checks before creating the phase code commit.
2. Exclude today's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` from same-day phase commits.
3. Keep one code commit scoped to one phase unless the user explicitly requests otherwise.
4. If the user explicitly says not to commit, keep the phase and validation records anyway.

### Test Logging

1. Record each validation command and result in the daily plan file.
2. If a test is skipped, record the reason in the same file.
"""

AVAILABLE_TIMEZONE_NAMES = available_timezones()
CASEFOLDED_TIMEZONE_NAMES = {
    timezone_name.casefold(): timezone_name for timezone_name in AVAILABLE_TIMEZONE_NAMES
}
TIMEZONE_SUFFIXES: dict[str, list[str]] = {}
for timezone_name in AVAILABLE_TIMEZONE_NAMES:
    suffix = timezone_name.rsplit("/", 1)[-1].casefold()
    TIMEZONE_SUFFIXES.setdefault(suffix, []).append(timezone_name)


def render_plan_template() -> str:
    return GENERATED_MARKER + "\n\n" + PLAN_TEMPLATE_BODY


def render_memo_template() -> str:
    return GENERATED_MARKER + "\n\n" + MEMO_TEMPLATE_BODY


def render_agents_block() -> str:
    return "\n".join(
        [
            AGENTS_START_MARKER,
            AGENTS_WORKFLOW_BODY.rstrip(),
            AGENTS_END_MARKER,
            "",
        ]
    )


def render_claude_block() -> str:
    return "\n".join(
        [
            CLAUDE_START_MARKER,
            AGENTS_WORKFLOW_BODY.rstrip(),
            CLAUDE_END_MARKER,
            "",
        ]
    )


def strip_generated_marker(text: str) -> str:
    markers = (GENERATED_MARKER, *LEGACY_GENERATED_MARKERS)
    for marker in markers:
        if text.startswith(marker):
            return text[len(marker) :].lstrip("\n")
    return text


def _timezone_name_candidates(timezone: str) -> list[str]:
    candidates: list[str] = []
    raw = timezone.strip().removeprefix(":")
    if not raw:
        return candidates

    for candidate in (raw, raw.replace(" ", "_")):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def normalize_timezone_name(timezone: str) -> str | None:
    for candidate in _timezone_name_candidates(timezone):
        matched = CASEFOLDED_TIMEZONE_NAMES.get(candidate.casefold())
        if matched:
            return matched

    for candidate in _timezone_name_candidates(timezone):
        try:
            zone_key = ZoneInfo(candidate).key
        except ZoneInfoNotFoundError:
            continue
        return CASEFOLDED_TIMEZONE_NAMES.get(zone_key.casefold(), zone_key)

    suffix_candidates = {
        candidate.rsplit("/", 1)[-1].casefold()
        for candidate in _timezone_name_candidates(timezone)
        if "/" not in candidate
    }
    for suffix in suffix_candidates:
        matches = TIMEZONE_SUFFIXES.get(suffix, [])
        if len(matches) == 1:
            return matches[0]
    return None


def _timezone_from_localtime_symlink() -> str | None:
    localtime_path = Path("/etc/localtime")
    if not localtime_path.is_symlink():
        return None

    try:
        target = os.readlink(localtime_path)
    except OSError:
        return None

    marker = "zoneinfo/"
    normalized_target = target.replace("\\", "/")
    if marker not in normalized_target:
        return None

    candidate = normalized_target.split(marker, 1)[1].strip("/")
    return normalize_timezone_name(candidate)


def _timezone_from_timezone_file() -> str | None:
    timezone_file = Path("/etc/timezone")
    if not timezone_file.exists():
        return None

    try:
        value = timezone_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None

    if not value:
        return None
    return normalize_timezone_name(value)


def detect_local_timezone_name() -> str | None:
    env_timezone = os.environ.get("TZ")
    if env_timezone:
        normalized_env_timezone = normalize_timezone_name(env_timezone)
        if normalized_env_timezone:
            return normalized_env_timezone

    local_now = datetime.now().astimezone()
    local_tz = local_now.tzinfo
    if local_tz is not None:
        for attribute_name in ("key", "zone"):
            timezone_name = getattr(local_tz, attribute_name, None)
            if isinstance(timezone_name, str):
                normalized_timezone_name = normalize_timezone_name(timezone_name)
                if normalized_timezone_name:
                    return normalized_timezone_name

    for resolver in (_timezone_from_localtime_symlink, _timezone_from_timezone_file):
        timezone_name = resolver()
        if timezone_name:
            return timezone_name

    return None


def resolve_effective_timezone(timezone: str | None) -> tuple[tzinfo, str]:
    if timezone:
        normalized_timezone_name = normalize_timezone_name(timezone)
        if normalized_timezone_name is None:
            raise ValueError(
                f"Unknown timezone: {timezone}. Use an IANA timezone like Asia/Shanghai."
            )
        return ZoneInfo(normalized_timezone_name), normalized_timezone_name

    detected_timezone_name = detect_local_timezone_name()
    if detected_timezone_name is not None:
        return ZoneInfo(detected_timezone_name), detected_timezone_name

    local_now = datetime.now().astimezone()
    timezone_label = local_now.tzname() or "local"
    return local_now.tzinfo or ZoneInfo("UTC"), timezone_label


def resolve_timezone_label(timezone: str | None) -> str:
    _, timezone_label = resolve_effective_timezone(timezone)
    return timezone_label


def resolve_date(date_value: str | None, timezone: str | None) -> str:
    if date_value:
        if len(date_value) != 8 or not date_value.isdigit():
            raise ValueError("Date must use YYYYMMDD format.")
        return date_value
    effective_timezone, _ = resolve_effective_timezone(timezone)
    now = datetime.now(effective_timezone)
    return now.strftime("%Y%m%d")


def daily_document_paths(doc_dir: Path) -> list[Path]:
    if not doc_dir.exists():
        return []
    return sorted(
        path
        for path in doc_dir.glob("*.md")
        if path.name != "TEMPLATE.md" and path.stem.isdigit() and len(path.stem) == 8
    )


def latest_daily_path(doc_dir: Path) -> Path | None:
    candidates = daily_document_paths(doc_dir)
    if not candidates:
        return None
    return candidates[-1]


def latest_plan_path(plan_dir: Path) -> Path | None:
    return latest_daily_path(plan_dir)


def latest_memo_path(memo_dir: Path) -> Path | None:
    return latest_daily_path(memo_dir)


def _git_path_has_uncommitted_changes(target_root: Path, path: Path) -> bool:
    try:
        relative_path = path.resolve().relative_to(target_root.resolve())
    except ValueError:
        return False

    try:
        result = subprocess.run(
            ["git", "-C", str(target_root), "status", "--short", "--", str(relative_path)],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return False

    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def pending_rollover_doc_paths(target_root: Path, today_date: str) -> list[Path]:
    candidates: list[Path] = []
    for directory in (target_root / "docs" / "plan", target_root / "docs" / "memo"):
        for candidate in reversed(daily_document_paths(directory)):
            if candidate.stem >= today_date:
                continue
            if _git_path_has_uncommitted_changes(target_root, candidate):
                candidates.append(candidate)
                break

    return candidates


def render_daily_document(template_text: str, date_value: str) -> str:
    return strip_generated_marker(template_text).replace("YYYYMMDD", date_value)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
