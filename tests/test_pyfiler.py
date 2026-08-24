import shutil
import tempfile
import unittest
from pathlib import Path

import pyfiler


class PyFilerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="pyfiler_test_"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def check(self, name, fn):
        try:
            fn()
        except Exception:
            print(f"[FAIL] {name}")
            raise
        else:
            print(f"[PASS] {name}")

    def test_files(self):
        def run():
            path = self.root / "test.txt"
            pyfiler.create_file(path, "one\ntwo\nthree\n")
            self.assertEqual(pyfiler.get_contents(path), "one\ntwo\nthree\n")
            self.assertEqual(pyfiler.get_contents(path, [2]), "two\n")
            pyfiler.add_contents(path, "four\n")
            pyfiler.remove_contents(path, [2])
            self.assertNotIn("two", pyfiler.get_contents(path))
            pyfiler.edit_contents(path, "done")
            self.assertEqual(pyfiler.read_file(path), "done")
            pyfiler.write_file(path, "rewritten")
            pyfiler.append_file(path, "!")
            self.assertEqual(pyfiler.get_contents(path), "rewritten!")
            pyfiler.clear_file(path)
            self.assertEqual(pyfiler.get_contents(path), "")
            pyfiler.touch_file(path)
            self.assertTrue(pyfiler.file_exists(path))

        self.check("file operations", run)

    def test_file_transfer(self):
        def run():
            source = self.root / "source.txt"
            copy = self.root / "copy.txt"
            moved = self.root / "moved.txt"
            renamed = self.root / "renamed.txt"
            pyfiler.create_file(source, "hello")
            pyfiler.copy_file(source, copy)
            self.assertTrue(pyfiler.compare_files(source, copy))
            pyfiler.move_file(copy, moved)
            pyfiler.rename_file(moved, renamed.name)
            self.assertEqual(pyfiler.get_contents(renamed), "hello")
            pyfiler.delete_file(renamed)
            self.assertFalse(renamed.exists())

        self.check("file copy, move, rename and delete", run)

    def test_folders(self):
        def run():
            folder = pyfiler.create_folder(self.root / "folder")
            source = pyfiler.create_file(self.root / "child.txt", "hello")
            pyfiler.add_parent(source, folder)
            self.assertEqual(len(pyfiler.folder_contents(folder)), 1)
            self.assertTrue(pyfiler.list_files(folder))
            pyfiler.folder_remove_contents(folder, ["child.txt"])
            self.assertEqual(pyfiler.folder_contents(folder), [])

        self.check("folder operations", run)

    def test_search_and_tree(self):
        def run():
            folder = pyfiler.create_folder(self.root / "project")
            pyfiler.create_file(folder / "main.py", "print('hello')")
            pyfiler.create_file(folder / "readme.txt", "hello")
            pyfiler.create_folder(folder / "src")
            pyfiler.create_file(folder / "src" / "app.py", "def app(): pass")
            self.assertEqual(len(pyfiler.find_files(folder, "*.py")), 2)
            self.assertEqual(len(pyfiler.find_extension(folder, ".py")), 2)
            self.assertEqual(len(pyfiler.search_contents(folder, "hello")), 2)
            self.assertEqual(len(pyfiler.search_regex(folder, r"def\\s+\\w+")), 1)
            self.assertEqual(pyfiler.count_files(folder), 3)
            self.assertEqual(pyfiler.count_folders(folder), 1)
            self.assertIn("main.py", pyfiler.tree(folder))

        self.check("search and tree operations", run)

    def test_metadata_and_paths(self):
        def run():
            path = pyfiler.create_file(self.root / "hello.py", "hello")
            info = pyfiler.metadata(path)
            self.assertEqual(info["type"], "file")
            self.assertTrue(info["is_file"])
            self.assertFalse(info["is_folder"])
            self.assertEqual(pyfiler.file_name(path), "hello.py")
            self.assertEqual(pyfiler.file_stem(path), "hello")
            self.assertEqual(pyfiler.file_extension(path), ".py")
            self.assertEqual(pyfiler.path_kind(path), "file")
            self.assertTrue(pyfiler.exists(path))
            self.assertTrue(pyfiler.is_file(path))
            self.assertFalse(pyfiler.is_folder(path))

        self.check("metadata and path operations", run)

    def test_hashing(self):
        def run():
            path = pyfiler.create_file(self.root / "hash.txt", "hello")
            digest = pyfiler.hash_file(path, "sha256")
            self.assertEqual(len(digest), 64)
            self.assertIn("sha256", pyfiler.available_hash_algorithms())

        self.check("hashing", run)

    def test_explorer(self):
        def run():
            fs = pyfiler.Explorer(self.root)
            fs.create_folder("src")
            fs.create_file("src/main.py", "print('Hello')")
            self.assertTrue(fs.exists("src/main.py"))
            self.assertTrue(fs.is_file("src/main.py"))
            self.assertEqual(fs.get_contents("src/main.py"), "print('Hello')")
            self.assertEqual(fs.metadata("src/main.py")["type"], "file")
            fs.add_contents("src/main.py", "\nprint('Bye')")
            self.assertIn("Bye", fs.get_contents("src/main.py"))

            with self.assertRaises(pyfiler.PathOutsideRootError):
                fs.create_file("../escape.txt", "blocked")

        self.check("rooted Explorer", run)

    def test_storage(self):
        def run():
            storage = pyfiler.setup_storage(self.root)
            self.assertTrue(storage.available)
            self.assertTrue(storage.permission_granted)
            self.assertEqual(Path(storage.path).resolve(), self.root.resolve())

        self.check("storage setup", run)


if __name__ == "__main__":
    print("=" * 60)
    print("PYFILER TEST SUITE")
    print("=" * 60)
    result = unittest.main(verbosity=2, exit=False)
    print("=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
