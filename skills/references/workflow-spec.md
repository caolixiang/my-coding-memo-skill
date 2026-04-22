# Workflow Specification

This skill installs a repository-level workflow for coding agents. The workflow is intentionally project-independent and focuses on durable state tracking. The core workflow lives in repository files and can operate without helper scripts.

## Installed Files

- `AGENTS.md`
- `CLAUDE.md` (optional, when the repository uses Claude memory)
- `docs/plan/TEMPLATE.md`
- `docs/memo/TEMPLATE.md`
- `docs/plan/YYYYMMDD.md`
- `docs/memo/YYYYMMDD.md`

These files define the workflow contract. Helper scripts may create or refresh them, but they are not required for the workflow to function.

## Instruction File Contract

The installer upserts a marked block into `AGENTS.md` and can also upsert a marked block into `CLAUDE.md`.

AGENTS markers:

- Start marker: `<!-- my-coding-memo-skill:start -->`
- End marker: `<!-- my-coding-memo-skill:end -->`

CLAUDE markers:

- Start marker: `<!-- my-coding-memo-skill:claude:start -->`
- End marker: `<!-- my-coding-memo-skill:claude:end -->`

When `AGENTS.md` or `CLAUDE.md` already exists:

- Preserve all existing repository-specific content.
- Replace only the marked workflow block if it already exists.
- Append the block if it does not exist yet.

When `AGENTS.md` does not exist:

- Create a minimal file with a repository-wide scope section.
- Add the workflow block below that scope section.

When `CLAUDE.md` does not exist:

- Create it only when Claude support is explicitly requested, such as `--claude always`.
- Otherwise leave it absent.

## Workflow Rules

The installed block enforces these rules:

1. Keep instruction priority explicit and log approved exceptions in the plan file.
2. Store daily plan files at `docs/plan/YYYYMMDD.md`.
3. Store daily memo files at `docs/memo/YYYYMMDD.md`.
4. Use the user's timezone for `YYYYMMDD`. If the user explicitly requests a different timezone, follow that.
5. Read the latest plan and latest memo before resuming work, especially after context compression or a new conversation.
6. Execute work in numbered phases.
7. Create one code commit after each completed phase unless the user explicitly says not to commit.
8. Update the current day's plan and memo after the phase commit, but delay committing those two daily docs until the next workday.
9. On the next workday, create a docs-only rollover commit for the previous day's plan and memo if they still have uncommitted changes.
10. Record phase acceptance, test results, commit history, and exceptions in the plan file.
11. Record chronological work items and commit summaries in the memo file.

## Template Requirements

### Plan Template

The canonical plan template must include:

- `# Today's Goals`
- `## Scope`
- `## Phase Plan`
- `## Phase Acceptance Log`
- `## Test Log`
- `## Commit Log`
- `## Exception Log`
- `## Tomorrow Plan`

### Memo Template

The canonical memo template must include:

- `# YYYYMMDD Memo`
- `## Items`
- `## Commits`
- `## Notes`

## Daily Preparation Flow

If helper scripts are available, use `scripts/prepare_day.py` when starting work:

1. Resolve the effective date.
2. Resolve the user's timezone automatically from thread context or the local runtime environment whenever possible; do not make manual timezone input the default path.
3. Let the script normalize the timezone to a stable IANA name whenever possible.
4. Find the latest existing plan and memo before creating anything new.
5. Detect whether the previous day's plan and memo still have uncommitted changes that need a rollover docs commit.
6. Ensure `docs/plan/YYYYMMDD.md` exists.
7. Ensure `docs/memo/YYYYMMDD.md` exists.
8. Read the files reported by `LATEST_EXISTING_PLAN_PATH` and `LATEST_EXISTING_MEMO_PATH` before continuing.
9. If `PENDING_ROLLOVER_DOCS=true`, commit the files in `PENDING_ROLLOVER_DOC_PATHS` before starting new implementation for the new day.

Without helper scripts, follow the same contract manually:

1. Resolve today's date in the user's timezone.
2. Ensure today's daily plan and memo files exist.
3. Read the latest existing plan and memo before continuing.
4. If the previous day's daily docs still have uncommitted changes, create the rollover docs commit before starting new implementation.

## Installer Order

On the first invocation of this workflow in a repository, the preferred order is:

1. Create or refresh `docs/plan/TEMPLATE.md`.
2. Create or refresh `docs/memo/TEMPLATE.md`.
3. Update or create `AGENTS.md`.
4. Update `CLAUDE.md` when it already exists, or create it when Claude support is explicitly requested.
5. Then run the day-start preparation flow for today's files.

## Safety Rules

- Do not overwrite a user-authored template unless the user explicitly asks for it.
- Do not remove repository-specific sections from `AGENTS.md`.
- Keep generated templates in English unless the user explicitly requests another language.
- Keep the workflow block idempotent so rerunning the installer is safe.
