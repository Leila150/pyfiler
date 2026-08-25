import shutil
import tempfile
import unittest
from pathlib import Path

import pyfiler
import pyfiler.storage_info as storage_info


class PyFilerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="pyfiler_test_"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def check(self, name, fn):
        try:
            fn()
        except Exception as exc:
            print(f"[FAIL] {name}\n       {type(exc).__name__}: {exc}")
            raise
        else:
            print(f"[PASS] {name}")

    def test_files(self):
        def run():
            path = self.root / "test.txt"
            pyfiler.create_file(path, "one\ntwo\nthree\n")
            self.assertEqual(pyfiler.read_contents(path), "one\ntwo\nthree\n")
            self.assertEqual(pyfiler.read_contents(path, [2]), "two\n")
            pyfiler.append_contents(path, "four\n")
            pyfiler.remove_contents(path, [2])
            self.assertNotIn("two", pyfiler.read_contents(path))
            pyfiler.replace_contents(path, "done")
            self.assertEqual(pyfiler.read_contents(path), "done")
            pyfiler.clear_file(path)
            self.assertEqual(pyfiler.read_contents(path), "")
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
            self.assertTrue(pyfiler.files_equal(source, copy))
            pyfiler.move_file(copy, moved)
            pyfiler.rename_file(moved, renamed.name)
            self.assertEqual(pyfiler.read_contents(renamed), "hello")
            pyfiler.delete_file(renamed)
            self.assertFalse(renamed.exists())

        self.check("file copy, move, rename and delete", run)

    def test_folders(self):
        def run():
            folder = pyfiler.create_folder(self.root / "folder")
            source = pyfiler.create_file(self.root / "child.txt", "hello")
            pyfiler.move_into(source, folder)
            self.assertEqual(len(pyfiler.list_folder(folder)), 1)
            self.assertTrue(pyfiler.list_files(folder))
            pyfiler.remove_from_folder(folder, ["child.txt"])
            self.assertEqual(pyfiler.list_folder(folder), [])

        self.check("folder operations", run)

    def test_search_and_tree(self):
        def run():
            folder = pyfiler.create_folder(self.root / "project")
            pyfiler.create_file(folder / "main.py", "print('hello')")
            pyfiler.create_file(folder / "readme.txt", "hello")
            pyfiler.create_folder(folder / "src")
            pyfiler.create_file(folder / "src" / "app.py", "def app(): pass")
            self.assertEqual(len(pyfiler.find_files(folder, "*.py")), 2)
            self.assertEqual(len(pyfiler.find_by_extension(folder, ".py")), 2)
            self.assertEqual(len(pyfiler.find_text(folder, "hello")), 2)
            self.assertEqual(len(pyfiler.find_pattern(folder, r"def\s+\w+")), 1)
            self.assertEqual(len(pyfiler.find_pattern(folder, r"def\\s+\\w+")), 0)
            self.assertEqual(pyfiler.count_files(folder), 3)
            self.assertEqual(pyfiler.count_folders(folder), 1)
            self.assertIn("main.py", pyfiler.directory_tree(folder))

        self.check("search and tree operations", run)

    def test_metadata_and_paths(self):
        def run():
            path = pyfiler.create_file(self.root / "hello.py", "hello")
            info = pyfiler.metadata(path)
            self.assertEqual(info["type"], "file")
            self.assertTrue(info["is_file"])
            self.assertFalse(info["is_folder"])
            self.assertEqual(pyfiler.name_of(path), "hello.py")
            self.assertEqual(pyfiler.stem_of(path), "hello")
            self.assertEqual(pyfiler.extension_of(path), ".py")
            self.assertEqual(pyfiler.path_kind(path), "file")
            self.assertTrue(pyfiler.exists(path))
            self.assertTrue(pyfiler.is_file(path))
            self.assertFalse(pyfiler.is_folder(path))

        self.check("metadata and path operations", run)

    def test_hashing(self):
        def run():
            path = pyfiler.create_file(self.root / "hash.txt", "hello")
            digest = pyfiler.file_hash(path, "SHA-256")
            self.assertEqual(len(digest), 64)
            self.assertIn("sha256", pyfiler.hash_algorithms())
            with self.assertRaises(pyfiler.UnsupportedHashAlgorithmError):
                pyfiler.file_hash(path, "definitely-not-a-hash")
            with self.assertRaises(ValueError):
                pyfiler.file_hash(path, "sha256", 0)

        self.check("hashing", run)

    def test_explorer(self):
        def run():
            fs = pyfiler.Explorer(self.root)
            fs.create_folder("src")
            fs.create_file("src/main.py", "print('Hello')")
            self.assertTrue(fs.exists("src/main.py"))
            self.assertTrue(fs.is_file("src/main.py"))
            self.assertEqual(fs.read_contents("src/main.py"), "print('Hello')")
            self.assertEqual(fs.metadata("src/main.py")["type"], "file")
            fs.append_contents("src/main.py", "\nprint('Bye')")
            self.assertIn("Bye", fs.read_contents("src/main.py"))
            self.assertEqual(fs.relative("src/main.py"), Path("src/main.py"))

            with self.assertRaises(pyfiler.PathOutsideRootError):
                fs.create_file("../escape.txt", "blocked")

        self.check("rooted Explorer", run)

    def test_storage_info(self):
        def run():
            self.assertTrue(storage_info.exists())
            self.assertTrue(storage_info.available())
            self.assertTrue(storage_info.readable())
            self.assertTrue(storage_info.writable())
            self.assertTrue(storage_info.can_read())
            self.assertTrue(storage_info.can_write())
            self.assertTrue(storage_info.permission_granted())
            self.assertTrue(storage_info.write_test())

            info = storage_info.check(self.root)
            self.assertTrue(info.available)
            self.assertTrue(info.permission_granted)
            self.assertEqual(info.filesystem, storage_info.filesystem(self.root))
            self.assertGreaterEqual(info.total_bytes, info.free_bytes)
            self.assertGreaterEqual(info.used_bytes, 0)
            self.assertTrue(storage_info.disk_usage(self.root).total >= storage_info.disk_usage(self.root).free)

        self.check("storage information", run)

    def test_storage_aliases_and_details(self):
        def run():
            self.assertEqual(storage_info.storage(), storage_info.available())
            self.assertEqual(storage_info.status().available, storage_info.available())
            self.assertTrue(storage_info.home_directory().exists())
            self.assertTrue(storage_info.current_directory().exists())
            self.assertTrue(storage_info.temporary_directory().exists())
            self.assertTrue(storage_info.platform_name())
            self.assertTrue(storage_info.operating_system())
            self.assertTrue(storage_info.default_storage().exists())
            self.assertTrue(storage_info.path().exists())

        self.check("storage information details", run)


if __name__ == "__main__":
    print("=" * 70)
    print("PYFILER TEST SUITE")
    print("=" * 70)
    result = unittest.main(verbosity=2, exit=False)
    print("=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
