"""Task tracker CLI - BUGGY VERSION (demo artifact).

This file is deliberately broken. It mirrors what an AI hands you when asked
for "a quick task tracker": it runs, it looks reasonable, and it loses data.
Each planted defect is marked with a `# bug N:` comment so the before/after
reads clearly. See ../FIXES.md for root causes.
"""

import json
import os
import sys

DEFAULT_PATH = "tasks.json"


def load_tasks(path=DEFAULT_PATH, tasks=[]):
    # bug 1: mutable default argument - one shared list leaks between calls
    if not os.path.exists(path):
        return tasks
    # bug 2: wrong encoding - latin-1 was bolted on to silence an error
    with open(path, encoding="latin-1") as f:
        try:
            return json.load(f)
        except Exception:
            # bug 6: swallows corruption and silently returns an empty list
            return tasks


def save_tasks(tasks, path=DEFAULT_PATH):
    # bug 5: hand-built JSON + truncating open - quotes/newlines break the file
    with open(path, "w", encoding="latin-1") as f:
        f.write("[\n")
        for i, task in enumerate(tasks):
            comma = "," if i < len(tasks) - 1 else ""
            f.write(
                '  {"id": %d, "title": "%s", "done": %s}%s\n'
                % (task["id"], task["title"], "true" if task["done"] else "false", comma)
            )
        f.write("]\n")


def add_task(tasks, title, path=DEFAULT_PATH):
    # bug 4: id from len() - collides after any delete
    task = {"id": len(tasks) + 1, "title": title, "done": False}
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def list_tasks(tasks, page=1, per_page=10):
    # bug 3: off-by-one - page 1 starts at index 10
    start = page * per_page
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
    tasks = load_tasks()

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
