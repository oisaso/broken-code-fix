"""Task tracker CLI - FIXED VERSION.

Same features, same CLI. Every defect from ../before/tasktracker.py is gone:
fresh defaults, explicit encoding, correct pagination, collision-free ids,
atomic writes, and corruption raises instead of hiding. See ../FIXES.md.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

DEFAULT_PATH = "tasks.json"


def load_tasks(path=DEFAULT_PATH, tasks=None):
    # fix 1: fresh default list per call - no shared state
    default = [] if tasks is None else tasks
    file = Path(path)
    if not file.exists():
        return list(default)
    try:
        # fix 2: encoding pinned to utf-8, the encoding save_tasks writes
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        # fix 6: corruption is loud, never a silent empty list
        raise ValueError(f"Corrupt task file: {file}") from exc
    if not isinstance(data, list):
        raise ValueError(f"Corrupt task file: {file}")
    return data


def save_tasks(tasks, path=DEFAULT_PATH):
    # fix 5: write a temp file, then atomically swap it in.
    # json.dump handles escaping; the real file is never truncated mid-write.
    file = Path(path)
    fd, tmp_name = tempfile.mkstemp(dir=str(file.parent), prefix=file.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        os.replace(tmp_name, file)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def add_task(tasks, title, path=DEFAULT_PATH):
    # fix 4: max id + 1 survives deletes
    next_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def list_tasks(tasks, page=1, per_page=10):
    # fix 3: page numbers are 1-based
    start = max(page - 1, 0) * per_page
    return tasks[start : start + per_page]


def complete_task(tasks, task_id, path=DEFAULT_PATH):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks, path)
            return True
    return False


def remove_task(tasks, task_id, path=DEFAULT_PATH):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[i]
            save_tasks(tasks, path)
            return True
    return False


USAGE = """usage: tasktracker.py <command>
  add <title>        add a task
  list [page]        list tasks (10 per page)
  done <id>          mark a task done
  rm <id>            delete a task"""


def main(argv):
    if len(argv) < 2:
        print(USAGE)
        return 1
    command = argv[1]
    try:
        tasks = load_tasks()
    except ValueError as exc:
        print(f"error: {exc}")
        return 1
    if command == "add":
        title = " ".join(argv[2:]).strip()
        if not title:
            print("error: empty title")
            return 1
        task = add_task(tasks, title)
        print(f"added task #{task['id']}")
    elif command == "list":
        page = int(argv[2]) if len(argv) > 2 else 1
        rows = list_tasks(tasks, page)
        print(f"page {page}: {len(rows)} task(s)")
        for task in rows:
            mark = "x" if task["done"] else " "
            print(f"  [{mark}] {task['id']:>3}  {task['title']}")
    elif command == "done":
        if len(argv) < 3 or not complete_task(tasks, int(argv[2])):
            print("error: unknown task id")
            return 1
        print(f"task {argv[2]} done")
    elif command == "rm":
        if len(argv) < 3 or not remove_task(tasks, int(argv[2])):
            print("error: unknown task id")
            return 1
        print(f"task {argv[2]} removed")
    else:
        print(USAGE)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
