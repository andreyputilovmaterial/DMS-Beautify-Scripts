# Testing

- Development tests live in `tests/` and run with pytest.
- New features and behavioral changes should be verified with tests.
- When fixing a bug, add a regression test that fails before the fix and passes after.
- Each script at the repo root (e.g. `apbeautify_prepdms.py`,
  `apbeautify_preptabscripts.py`) must stay importable without executing `main()` on
  import (it is guarded by `if __name__ == "__main__"`), so tests can import it directly.
