#!/usr/bin/env python3
"""Create daily plan and memo files and report resume and rollover metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_common import (
    latest_memo_path,
    latest_plan_path,
    pending_rollover_doc_paths,
    render_daily_document,
    render_memo_template,
    render_plan_template,
    resolve_date,
    resolve_timezone_label,
    write_text,
)


def load_template(path: Path, default_text: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default_text


def ensure_daily_file(path: Path, content: str, overwrite: bool) -> str:
    existed = path.exists()
    if existed and not overwrite:
        return "existing"
    write_text(path, content)
    return "updated" if existed else "created"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target repository root.")
    parser.add_argument("--date", help="Working date in YYYYMMDD format.")
    parser.add_argument(
        "--timezone",
        help="Optional timezone override. When omitted, the script auto-detects the user's local timezone.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate today's plan and memo files even if they already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_root = Path(args.target).expanduser().resolve()

    if not target_root.exists():
        raise SystemExit(f"Target path does not exist: {target_root}")
    if not target_root.is_dir():
        raise SystemExit(f"Target path is not a directory: {target_root}")

    try:
        date_value = resolve_date(args.date, args.timezone)
        timezone_label = resolve_timezone_label(args.timezone)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    plan_dir = target_root / "docs" / "plan"
    memo_dir = target_root / "docs" / "memo"
    latest_existing_plan = latest_plan_path(plan_dir)
    latest_existing_memo = latest_memo_path(memo_dir)
    pending_rollover_paths = pending_rollover_doc_paths(target_root, date_value)
    pending_rollover_dates = sorted({path.stem for path in pending_rollover_paths})
    pending_rollover_date = ",".join(pending_rollover_dates)

    plan_template = load_template(plan_dir / "TEMPLATE.md", render_plan_template())
    memo_template = load_template(memo_dir / "TEMPLATE.md", render_memo_template())

    today_plan_path = plan_dir / f"{date_value}.md"
    today_memo_path = memo_dir / f"{date_value}.md"

    plan_status = ensure_daily_file(
        today_plan_path,
        render_daily_document(plan_template, date_value),
        overwrite=args.overwrite,
    )
    memo_status = ensure_daily_file(
        today_memo_path,
        render_daily_document(memo_template, date_value),
        overwrite=args.overwrite,
    )

    print(f"TARGET_ROOT={target_root}")
    print(f"DATE={date_value}")
    print(f"TIMEZONE={timezone_label}")
    print(
        "LATEST_EXISTING_PLAN_PATH="
        + (str(latest_existing_plan) if latest_existing_plan is not None else "")
    )
    print(
        "LATEST_EXISTING_MEMO_PATH="
        + (str(latest_existing_memo) if latest_existing_memo is not None else "")
    )
    print(f"PENDING_ROLLOVER_DOCS={'true' if pending_rollover_paths else 'false'}")
    print(f"PENDING_ROLLOVER_DOC_DATE={pending_rollover_date}")
    print(
        "PENDING_ROLLOVER_DOC_PATHS="
        + ";".join(str(path) for path in pending_rollover_paths)
    )
    print(f"TODAY_PLAN_PATH={today_plan_path}")
    print(f"TODAY_MEMO_PATH={today_memo_path}")
    print(f"PLAN_STATUS={plan_status}")
    print(f"MEMO_STATUS={memo_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
