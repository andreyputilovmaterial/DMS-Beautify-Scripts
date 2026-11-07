# Project context

Living working memory for this repository. Read this first on every task; update it
before finishing every task.

## What this is

`DMS-Beautify-Scripts` contains helper scripts that post-format ("beautify") DMS /
mrStudio script exports (`.mrs` / `.dms`). They normalize line breaks, reorder
table definitions, strip noisy comments, and tidy the generated code so it is
easier to read, review, and diff. Primary use: make the output of the DMS
data-management scripts less painful to work through — e.g. large batches of
Mailchimp banner updates (200+ tickets).

> Honest status (from the README): this is regarded as the wrong approach. The
> scripts are fragile regex one-offs that do not work in most projects and should
> be re-written to use a real parser instead of the current pile of regex
> expressions. Treat them as project-specific helpers, not a general tool.

## Current layout

- `apbeautify_prepdms.py` — beautifies `Metadata` and `OnNextCase` blocks in DMS
  files. Stdlib only. CLI: `-1/--da` (required) and optional `-2/--prep`.
- `apbeautify_preptabscripts.py` — beautifies table scripts: splits tables via
  `TableSplitter`, normalizes titles/comments/line breaks, and reorders
  `gridsummary`/`tableof` arguments. Stdlib only. Same CLI shape; its
  `beautify_working_file` deliberately raises "not implemented here".
- `README.md` — project intro and (negative) status.
- `docs/` — this file and `roadmap.md`.
- `.clinerules/` — AI working rules (project context memory, roadmap, design,
  testing, code style, commit messages, terminal commands).

## Key decisions & reasoning

- **Stdlib only.** Both scripts import `os`, `time`, `re`, `sys`, `datetime`,
  `argparse`, `pathlib` — no third-party runtime dependencies, so there is no
  `requirements.txt`. `requirements-dev.txt` holds only `pytest` for the future
  test suite.
- **Regex-based transformation.** The scripts do string-level `re.sub` transforms
  rather than parsing the DMS/mrStudio grammar. This is the core weakness: regex
  cannot reliably handle nested/conditional syntax, so each script only works on
  the specific shapes it was written for.
- **Input -> output naming.** The `-1/--da` input is written to `<input>.f.mrs`;
  the optional `-2/--prep` input is written to `<input>.upd.mrs`. Outputs are
  written next to the input (same `Path`).
- **Two related but separate scripts.** `apbeautify_prepdms.py` targets
  `Metadata`/`OnNextCase`; `apbeautify_preptabscripts.py` targets table scripts.
  They share the same CLI shape and the `main(args)` +
  `if __name__ == "__main__"` guard but are otherwise independent.
- **`datetime.utcnow()` (2026-11):** both scripts call `datetime.utcnow()`, which
  is deprecated since Python 3.12 (emits `DeprecationWarning`). The value is never
  used — the `elapsed_time` line is commented out — so it can simply be dropped.

## Gotchas

- `.gitignore` contains `**/[Tt]est*`, which also matches a future `tests/`
  directory. A committed pytest suite will need explicit negations (`!tests/` and
  `!tests/**`) or a tweak to that pattern (see the testing rule in
  `.clinerules/03-testing.md`).
- Both scripts print noisy debug lines (`"beautify_metadata called!"`,
  `"Starting..."`, `"Finished"`, etc.).
- `apbeautify_preptabscripts.py` keeps a large commented-out first `TableSplitter`
  draft and a `# TODO: implement` for `table_variable` (always `None` today).
- The scripts open the `--da` file unconditionally; a missing/unreadable path
  crashes with `FileNotFoundError` rather than a friendly message.

## Open questions / follow-ups

See `docs/roadmap.md`.
