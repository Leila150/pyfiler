
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