# Roadmap / TODO

Living TODO list. Add ideas freely; triage at the end of each task.

## Ideas / follow-ups

- **Re-write with a real parser.** Replace the regex-based transforms with a
  proper DMS/mrStudio parser (or at least a lexer/tokenizer) so the scripts work
  across projects instead of only the specific shapes they were written for. This
  is the core issue called out in the README.
- Add a pytest suite under `tests/` (there are no tests today). This requires
  un-ignoring the `tests/` directory in `.gitignore` (see
  `docs/project-context.md` Gotchas).
- Deduplicate the two scripts: they share the same CLI shape, `main()` skeleton,
  and output-naming logic (`*.f.mrs` / `*.upd.mrs`); extract the common parts.
- Remove dead/leftover code: the large commented-out first `TableSplitter` draft,
  the unused `datetime.utcnow()`/elapsed-time scaffolding, and the noisy
  `print("...called!")` debug lines.
- Implement `table_variable` extraction in `apbeautify_preptabscripts.py`
  (currently a `# TODO: implement` that always sets `None`).
- Decide whether `beautify_working_file` in `apbeautify_preptabscripts.py` should
  be implemented or removed (it currently raises "You crazy do it yourself...").
- Add friendlier error handling for missing/unreadable input files (today a bad
  `--da` path crashes with `FileNotFoundError`).
- Consider a `--dry-run`/`--out` option to avoid clobbering inputs and to make
  the transform easier to test.
