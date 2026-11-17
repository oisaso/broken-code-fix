# FIXES.md — what was wrong and why

Six defects planted across two files. Each has a failing test in `before/`
that passes in `after/`. The seventh test is a control: it passes in both,
which proves the suite measures real defects, not rigged assertions.

| # | Where | Symptom | Root cause | Fix |
|---|---|---|---|---|
| 1 | `load_tasks` | A list returned by one call grows when another call's list is mutated | `tasks=[]` default argument is created once at import time and shared by every call | `tasks=None` sentinel, fresh list per call |
| 2 | `load_tasks` | `café` becomes `cafÃ©`, `☕` becomes mojibake | File opened in `latin-1` — a band-aid added to silence an earlier decode error | Pin `encoding="utf-8"` on every open, matching what `save_tasks` writes |
| 3 | `list_tasks` | Page 1 is empty, page 2 shows page 1, last page shows nothing | `start = page * per_page` — 1-based page treated as 0-based index | `start = (page - 1) * per_page` with a floor at 0 |
| 4 | `add_task` | After deleting a task, the next id collides with an existing one | `id = len(tasks) + 1` — length is not a stable identity after deletes | `max(existing ids, default=0) + 1` |
| 5 | `save_tasks` | One task titled `He said "halt"` corrupts the entire file | JSON built by string formatting; quotes and newlines break the document; file truncated by `open("w")` before the write can fail | `json.dump` to a temp file, then `os.replace` — atomic swap, real escaping |
| 6 | `load_tasks` | App starts empty after a crash mid-save — user assumes work is gone | `except Exception: return []` hides corruption | Catch only `JSONDecodeError`, re-raise as `ValueError` with the file path |

## Why the fixes are shaped this way

- Atomic write (temp file + `os.replace`) is the same pattern databases use.
  A crash can lose the newest write, never the whole file.
- Errors as values in `main`: the CLI prints a clean message and exits 1,
  no traceback in a user's face.
- No behavior changes beyond the bugs — same commands, same output format.
  A buyer's existing scripts keep working.

## Proof

```
before/  ->  6 red (5 failures + 1 error), 1 control pass
 after/  ->  7 passed
```

## How this maps to the gig

This is the "fix your broken AI-generated code" artifact. A buyer reads the
table, recognizes two or three symptoms from their own app, and messages you.
That recognition is the sale.
