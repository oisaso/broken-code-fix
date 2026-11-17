"""The same test suite runs against both versions.

Run from inside this directory:  python -m unittest -v

before/ : 6 failures, 1 pass (the pass is a control - the suite is honest)
after/  : 7 passes
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import tasktracker


class TaskTrackerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.path = str(Path(self._tmp.name) / "tasks.json")
        # The buggy module shares one default list across the whole process;
        # clear it so each test starts from a known state (no-op in after/).
        for default in tasktracker.load_tasks.__defaults__ or ():
            if isinstance(default, list):
                default.clear()

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_file_returns_independent_lists(self):
        first = tasktracker.load_tasks(self.path)
        first.append({"id": 99, "title": "leak", "done": False})
        second = tasktracker.load_tasks(self.path)
        self.assertEqual(second, [], "shared mutable default leaked between calls")

    def test_unicode_survives_load(self):
        payload = [{"id": 1, "title": "café ☕", "done": False}]
        Path(self.path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        loaded = tasktracker.load_tasks(self.path)
        self.assertEqual(loaded[0]["title"], "café ☕")

    def test_quotes_and_newlines_survive_save(self):
        tasks = tasktracker.load_tasks(self.path)
        tasktracker.add_task(tasks, 'He said "halt"\nthen left', self.path)
        # the file on disk must be valid JSON, whatever load_tasks swallows
        json.loads(Path(self.path).read_text(encoding="utf-8"))
        reloaded = tasktracker.load_tasks(self.path)
        self.assertEqual(len(reloaded), 1, "task lost on save/load round-trip")
        self.assertEqual(reloaded[0]["title"], 'He said "halt"\nthen left')

    def test_pagination_starts_on_page_one(self):
        tasks = [{"id": i, "title": f"task {i}", "done": False} for i in range(1, 26)]
        page_one = tasktracker.list_tasks(tasks, page=1, per_page=10)
        page_two = tasktracker.list_tasks(tasks, page=2, per_page=10)
        page_three = tasktracker.list_tasks(tasks, page=3, per_page=10)
        self.assertEqual([t["id"] for t in page_one], list(range(1, 11)))
        self.assertEqual([t["id"] for t in page_two], list(range(11, 21)))
        self.assertEqual([t["id"] for t in page_three], list(range(21, 26)))

    def test_ids_stay_unique_after_delete(self):
        tasks = tasktracker.load_tasks(self.path)
        a = tasktracker.add_task(tasks, "a", self.path)
        b = tasktracker.add_task(tasks, "b", self.path)
        c = tasktracker.add_task(tasks, "c", self.path)
        tasktracker.remove_task(tasks, b["id"], self.path)
        d = tasktracker.add_task(tasks, "d", self.path)
        ids = [a["id"], c["id"], d["id"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate id after delete")

    def test_corrupt_file_is_reported_not_swallowed(self):
        Path(self.path).write_text("not json at all", encoding="utf-8")
        with self.assertRaises(ValueError):
            tasktracker.load_tasks(self.path)

    def test_done_and_remove_persist(self):
        # control test: passes in both versions - the suite is not rigged
        tasks = tasktracker.load_tasks(self.path)
        first = tasktracker.add_task(tasks, "write report", self.path)
        second = tasktracker.add_task(tasks, "send invoice", self.path)
        tasktracker.complete_task(tasks, first["id"], self.path)
        tasktracker.remove_task(tasks, second["id"], self.path)
        reloaded = tasktracker.load_tasks(self.path)
        self.assertEqual(len(reloaded), 1)
        self.assertTrue(reloaded[0]["done"])


if __name__ == "__main__":
    unittest.main()
