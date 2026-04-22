# Claude Memory Template For Coding Memo Workflow

Copy this file into project-level `CLAUDE.md` or adapt it for user-level `~/.claude/CLAUDE.md`.

Replace `/ABSOLUTE/PATH/TO/my-coding-memo-skill` with the actual local path if you want Claude Code to call the shared scripts directly. If you do not want any helper scripts, keep the rules below and perform the day-start steps manually.

## Coding Memo Workflow

- Before starting implementation, prepare the workday and reload state from the latest plan and memo.
- After context compaction, thread resume, or a fresh conversation, read the latest plan and memo again before continuing.
- Keep daily plan files at `docs/plan/YYYYMMDD.md`.
- Keep daily memo files at `docs/memo/YYYYMMDD.md`.
- Use the user's timezone for `YYYYMMDD`. If the user explicitly requests another timezone, follow that.
- Execute work in numbered phases.
- Create one code commit after each completed phase unless the user explicitly says not to commit.
- After each phase commit, update today's plan and memo with the commit hash and summary.
- Do not create a second same-day docs-only commit for today's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md`.
- On the next workday, if the previous day's plan and memo are still uncommitted, create a docs-only rollover commit before starting new implementation.

## Daily Preparation Step

Preferred path when shared scripts are available:

Run:

```bash
python /ABSOLUTE/PATH/TO/my-coding-memo-skill/scripts/prepare_day.py --target /path/to/repo
```

Then follow these outputs:

- Read `LATEST_EXISTING_PLAN_PATH` if present.
- Read `LATEST_EXISTING_MEMO_PATH` if present.
- If `PENDING_ROLLOVER_DOCS=true`, commit the files in `PENDING_ROLLOVER_DOC_PATHS` before starting new implementation for the day.

Manual fallback when scripts are not used:

- Resolve today's date in the user's timezone.
- Ensure today's `docs/plan/YYYYMMDD.md` and `docs/memo/YYYYMMDD.md` exist.
- Read the latest plan and memo before continuing.
- If the previous day's plan and memo still have uncommitted changes, create the rollover docs commit before starting new implementation.

## First-Time Installation

If the repository does not already contain the workflow files, run:

```bash
python /ABSOLUTE/PATH/TO/my-coding-memo-skill/scripts/install_workflow.py --target /path/to/repo
```

This should install or update:

- `AGENTS.md`
- `docs/plan/TEMPLATE.md`
- `docs/memo/TEMPLATE.md`

If you prefer a no-script setup, create or maintain these files manually in the repository and keep the same workflow rules in `CLAUDE.md`.

## Optional Project Adjustment

If you vendor the workflow into the project, replace the absolute script path with a repository-relative path that is stable for the team.
