#!/usr/bin/env python3
"""Install or refresh the coding memo workflow in a target repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_common import (
    AGENTS_END_MARKER,
    AGENTS_START_MARKER,
    CLAUDE_END_MARKER,
    CLAUDE_START_MARKER,
    GENERATED_MARKER,
    LEGACY_AGENTS_MARKER_PAIRS,
    LEGACY_GENERATED_MARKERS,
    render_agents_block,
    render_claude_block,
    render_memo_template,
    render_plan_template,
    write_text,
)


def build_instruction_file(title: str, block: str) -> str:
    return f"""# {title}

## Scope

- This file applies to the repository root and all subdirectories.

""" + block


def upsert_marked_file(
    path: Path,
    block: str,
    *,
    start_marker: str,
    end_marker: str,
    create_title: str,
    legacy_marker_pairs: tuple[tuple[str, str], ...] = (),
) -> str:
    if not path.exists():
        write_text(path, build_instruction_file(create_title, block))
        return "created"

    existing = path.read_text(encoding="utf-8")
    if start_marker in existing and end_marker in existing:
        start = existing.index(start_marker)
        end = existing.index(end_marker) + len(end_marker)
        updated = existing[:start].rstrip() + "\n\n" + block + existing[end:].lstrip("\n")
        write_text(path, updated)
        return "updated"

    for legacy_start, legacy_end in legacy_marker_pairs:
        if legacy_start in existing and legacy_end in existing:
            start = existing.index(legacy_start)
            end = existing.index(legacy_end) + len(legacy_end)
            updated = existing[:start].rstrip() + "\n\n" + block + existing[end:].lstrip("\n")
            write_text(path, updated)
            return "updated-legacy"

    separator = "\n\n" if existing.rstrip() else ""
    updated = existing.rstrip() + separator + block
    write_text(path, updated)
    return "appended"


def upsert_agents_file(path: Path) -> str:
    return upsert_marked_file(
        path,
        render_agents_block(),
        start_marker=AGENTS_START_MARKER,
        end_marker=AGENTS_END_MARKER,
        create_title="AGENTS.md",
        legacy_marker_pairs=LEGACY_AGENTS_MARKER_PAIRS,
    )


def upsert_claude_file(path: Path) -> str:
    return upsert_marked_file(
        path,
        render_claude_block(),
        start_marker=CLAUDE_START_MARKER,
        end_marker=CLAUDE_END_MARKER,
        create_title="CLAUDE.md",
    )


def update_template(path: Path, content: str, overwrite_templates: bool) -> str:
    if not path.exists():
        write_text(path, content)
        return "created"

    existing = path.read_text(encoding="utf-8")
    generated_markers = (GENERATED_MARKER, *LEGACY_GENERATED_MARKERS)
    if existing.startswith(generated_markers) or overwrite_templates:
        write_text(path, content)
        return "updated"

    return "kept-existing"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target repository root.")
    parser.add_argument(
        "--claude",
        choices=("auto", "always", "never"),
        default="auto",
        help=(
            "How to handle CLAUDE.md: auto updates it when present, "
            "always creates or updates it, never skips it."
        ),
    )
    parser.add_argument(
        "--overwrite-templates",
        action="store_true",
        help="Replace existing non-generated templates with the canonical ones.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_root = Path(args.target).expanduser().resolve()

    if not target_root.exists():
        raise SystemExit(f"Target path does not exist: {target_root}")
    if not target_root.is_dir():
        raise SystemExit(f"Target path is not a directory: {target_root}")

    plan_template_status = update_template(
        target_root / "docs" / "plan" / "TEMPLATE.md",
        render_plan_template(),
        overwrite_templates=args.overwrite_templates,
    )
    memo_template_status = update_template(
        target_root / "docs" / "memo" / "TEMPLATE.md",
        render_memo_template(),
        overwrite_templates=args.overwrite_templates,
    )
    agents_status = upsert_agents_file(target_root / "AGENTS.md")

    claude_path = target_root / "CLAUDE.md"
    if args.claude == "never":
        claude_status = "skipped"
    elif args.claude == "auto" and not claude_path.exists():
        claude_status = "skipped"
    else:
        claude_status = upsert_claude_file(claude_path)

    print(f"TARGET_ROOT={target_root}")
    print(f"PLAN_TEMPLATE_STATUS={plan_template_status}")
    print(f"MEMO_TEMPLATE_STATUS={memo_template_status}")
    print(f"AGENTS_STATUS={agents_status}")
    print(f"CLAUDE_STATUS={claude_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
