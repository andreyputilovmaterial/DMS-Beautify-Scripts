# Roadmap / TODO

Living TODO list. Add ideas freely; triage at the end of each task.

## Ideas / follow-ups

- **Re-write with a real parser.** Replace the regex-based transforms with a
  proper DMS/mrStudio parser (or at least a lexer/tokenizer) so the scripts work
  across projects instead of only the specific shapes they were written for. This
  is the core issue called out in the README.
- Expand the pytest suite under `tests/` (currently one regression test for the
  `GridSummaryBase` base fix) to cover the rest of the regex transforms in both
  scripts.
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
