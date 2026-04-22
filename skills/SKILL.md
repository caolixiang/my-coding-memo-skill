---
name: my-coding-memo-skill
description: Install and maintain a project-independent memo and phase-based plan workflow for coding agents. Use when Codex needs to initialize or repair AGENTS.md workflow rules, scaffold docs/plan and docs/memo templates, create today's worklog files in the user's timezone, or resume work by reading the latest plan and memo in an existing repository. The core workflow lives in repository files; bundled scripts are optional accelerators, not a hard requirement.
---

# Coding Memo Workflow

Use this skill to add a reusable planning and memo discipline to any repository. The workflow is project-agnostic: its core contract lives in repository files such as `AGENTS.md`, `CLAUDE.md`, `docs/plan/`, and `docs/memo/`. The bundled scripts are optional helpers for bootstrapping and day-start preparation.

## Quick Start

1. Identify the target repository root.
2. If the repo already has `AGENTS.md`, `CLAUDE.md`, or custom planning docs, read [references/workflow-spec.md](references/workflow-spec.md) before making changes.
3. If the target repository is outside the current writable workspace, request approval before editing files or running installer scripts against it.
4. On the first invocation of this skill in a repository, install the workflow before doing day-start preparation.
5. The install flow is: create or refresh `docs/plan/TEMPLATE.md` and `docs/memo/TEMPLATE.md` first, then update or create `AGENTS.md`, and then update or create `CLAUDE.md` when the repo already uses Claude memory or the user explicitly asks for Claude support.
6. The default install command is `python scripts/install_workflow.py --target /path/to/repo`.
7. If the repository already uses Claude or the user wants Claude support installed, use `python scripts/install_workflow.py --target /path/to/repo --claude always`.
8. If the repository does not already have an equivalent workflow, either update the files manually or run the installer from this skill directory.
9. Resolve the user's timezone automatically from the thread context or local runtime environment. Do not default to asking the user to pass a timezone manually.
10. If the helper script is available, run `python scripts/prepare_day.py --target /path/to/repo` to create today's plan and memo files and print the latest plan/memo paths plus any pending rollover-doc signals.
11. If the helper script is not being used, manually ensure today's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` exist, then read the latest plan and memo before continuing.
12. Use `--timezone <user_timezone>` only when the user explicitly wants an override or the thread context clearly provides a timezone that differs from the local machine timezone.
13. When the helper script is used, treat `LATEST_EXISTING_PLAN_PATH`, `LATEST_EXISTING_MEMO_PATH`, and `PENDING_ROLLOVER_DOCS` as the day-start signals.
14. When the helper script is not used, apply the same contract manually: read the latest plan and memo first, and roll the previous day's docs into a docs-only commit before new implementation if they are still uncommitted.

## Install Workflow

Use `scripts/install_workflow.py` when a repository needs the workflow for the first time, or when the canonical workflow block/templates need to be refreshed. If the repository already carries equivalent rules and templates, manual edits are acceptable and the script is optional.

What the installer does:

- Create `docs/plan/TEMPLATE.md` and `docs/memo/TEMPLATE.md` when missing.
- Refresh generated templates in place when they were previously created by this skill.
- Upsert a marked `my-coding-memo-skill` block into `AGENTS.md` without replacing unrelated project rules.
- Update an existing `CLAUDE.md` automatically when one is already present.
- Create or update `CLAUDE.md` when `--claude always` is passed.
- Leave user-authored templates untouched unless `--overwrite-templates` is passed explicitly.

Recommended command:

```bash
python scripts/install_workflow.py --target /path/to/repo
```

If the repository should also carry Claude memory rules, use:

```bash
python scripts/install_workflow.py --target /path/to/repo --claude always
```

Use `--overwrite-templates` only when the user explicitly wants the canonical templates to replace existing custom templates.

## Prepare a Work Day

Use `scripts/prepare_day.py` after the workflow is installed, or whenever a new day of work starts. If the repository already manages the day-start flow through plain files and agent instructions, follow the same contract manually.

What the daily preparation script does:

- Resolve the working date in the user's timezone.
- Auto-detect and normalize the timezone to a stable IANA name such as `Asia/Shanghai` or `America/New_York` whenever possible.
- Print the latest existing plan and memo paths so a resumed or compressed conversation can reload both sources of state.
- Detect whether the previous day's daily docs still have uncommitted changes that should be rolled over in a docs-only commit.
- Create `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` from the repository templates if they do not already exist.
- Report today's plan and memo file locations for the current workday.

Recommended command:

```bash
python scripts/prepare_day.py --target /path/to/repo
```

If the user needs a specific day, pass `--date YYYYMMDD`. If the user explicitly requests a different timezone, pass `--timezone <user_timezone>` as an override. Only ask the user for timezone information when neither the thread context nor the local environment can provide a reliable answer.

When the script reports `PENDING_ROLLOVER_DOCS=true`, treat that as a required rollover step: commit the previous day's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` before starting new implementation work for the new day.

Manual day-start fallback when the script is not in use:

1. Resolve today's `YYYYMMDD` in the user's timezone.
2. Ensure today's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` exist.
3. Read the latest existing daily plan and memo before continuing.
4. If yesterday's plan and memo still have uncommitted changes, roll them into a docs-only commit before new implementation starts.

## Operating Rules

When applying this skill inside a target repository:

1. Preserve repository-specific instructions. Only add or update the marked workflow block instead of rewriting unrelated `AGENTS.md` content.
2. If the repository uses `CLAUDE.md`, only add or update the marked workflow block there instead of rewriting unrelated memory content.
3. Keep the workflow language in English unless the user explicitly requests another language.
4. Use the user's timezone when creating or interpreting `YYYYMMDD` file names, and prefer a canonical IANA timezone label over ambiguous abbreviations such as `CST`.
5. Treat the plan as the source of truth for phase goals, acceptance, tests, commits, and exceptions.
6. Treat the memo as the chronological activity log. Append an item for each meaningful step and add a commit entry after every phase commit.
7. After each completed phase, create one code commit for that phase unless the user explicitly says not to commit.
8. Do not create a second same-day commit only to capture plan and memo updates with the new hash. Leave today's plan and memo uncommitted until the next workday.
9. On the next workday, commit the previous day's plan and memo files in a docs-only rollover commit before starting new implementation.
10. Before starting work in a resumed thread, a fresh conversation, or a post-compression conversation, read the latest plan and memo first.
11. If a higher-priority instruction forces an exception to the workflow, record it in that day's plan file.

## Resources

- [references/workflow-spec.md](references/workflow-spec.md): Canonical workflow contract, installed file layout, and instruction-file block semantics.
- `scripts/install_workflow.py`: Optional installer for workflow files in a target repository.
- `scripts/prepare_day.py`: Optional day-start helper that creates today's files, reports the latest plan/memo to read, and surfaces pending rollover doc commits.
- `scripts/workflow_common.py`: Shared templates and utility functions used by the optional helper scripts.
