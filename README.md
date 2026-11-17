# Bug-fix demo — broken AI-style code, before and after

**What it proves:** you can take plausible AI-generated code with six real
defects, reproduce each failure with a test, fix it without changing behavior,
and explain every root cause in plain English. This is the proof piece for the
"fix your broken AI-generated code" gig.

## The two-minute demo

```bash
# 1. show it's actually broken
cd before
python -m unittest -v
# -> 6 red (5 failures + 1 error), plus 1 control pass

# 2. show it's fixed
cd ../after
python -m unittest -v
# -> 7 passes
```

Same code features, same test file. Only `tasktracker.py` differs.

## What's inside

| Path | What it is |
|---|---|
| `before/tasktracker.py` | buggy CLI task tracker (each bug marked `# bug N:`) |
| `after/tasktracker.py` | fixed version |
| `before/test_tasktracker.py` | failing suite |
| `after/test_tasktracker.py` | identical suite, now green |
| `FIXES.md` | root-cause table: symptom -> cause -> fix |

## Use it in the gig

Attach the repo link and paste the FIXES.md table into the gig description —
buyers scan for a symptom they recognize. Most will find one ("page 1 is
empty after an update" / "my file corrupted when the title had quotes").

## Run the app itself

```bash
cd after
python tasktracker.py add "write the proposal"
python tasktracker.py add "send invoice"
python tasktracker.py list
python tasktracker.py done 1
```
