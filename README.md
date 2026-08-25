# pyfiler

**pyfiler** is a Python filesystem toolkit for working with files, folders, paths, searches, metadata, hashes, directory statistics, storage information, and secure rooted filesystem access.

It provides two main ways to work:

- **Simple functions** for straightforward filesystem operations.
- **`Explorer`** for applications that need operations restricted to a configured root directory.

> **Status:** Active development. The public API may continue to grow.

---

## ✨ Features

- 📄 Create, read, edit, append, clear, copy, move, rename, touch, and delete files
- 📁 Create, list, clear, copy, move, rename, and delete folders
- 🔎 Search by name, extension, text, regular expression, and size
- 🧭 Path manipulation and inspection helpers
- 📊 File and folder metadata
- #️⃣ SHA-256, MD5, and other supported file hashes
- 🔍 File comparison
- 🌳 Directory trees and directory statistics
- 🧭 Root-restricted `Explorer` API
- 📱 Storage capability and filesystem information through `storage_info`
- 🔐 Path-security checks
- 🚫 No third-party runtime dependencies

---

## 📦 Installation

From the repository:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

The runtime library uses Python's standard library and does not require third-party packages.

---

## 🚀 Quick Start

### Create and read a file

```python
import pyfiler

pyfiler.create_file(
    "hello.txt",
    "Hello, pyfiler!\nThis is line two.\n"
)

print(pyfiler.get_contents("hello.txt"))
```

### Read selected lines

Lines are **1-based**:

```python
print(pyfiler.get_contents("hello.txt", [1, 2]))
```

### Modify a file

```python
pyfiler.add_contents("hello.txt", "Line three.\n")
pyfiler.remove_contents("hello.txt", [2])
pyfiler.edit_contents("hello.txt", "Completely new contents")
```

---

## 📄 Files

Common file operations include:

| Function | Description |
|---|---|
| `create_file()` | Create a new file |
| `get_contents()` | Read all or selected lines |
| `add_contents()` | Append contents |
| `remove_contents()` | Remove selected lines or clear contents |
| `edit_contents()` | Replace file contents |
| `clear_file()` | Empty a file |
| `touch_file()` | Create or touch a file |
| `copy_file()` | Copy a file |
| `move_file()` | Move a file |
| `rename_file()` | Rename a file |
| `delete_file()` | Delete a file |
| `file_exists()` | Check whether a path is a file |

Example:

```python
from pyfiler import create_file, get_contents, copy_file

create_file("original.txt", "Hello")
copy_file("original.txt", "backup.txt")

print(get_contents("backup.txt"))
```

### Line numbers

Line-based operations use **positive 1-based integers**:

```python
get_contents("file.txt", [1, 3, 5])
```

Invalid line lists and invalid line numbers raise pyfiler exceptions instead of silently doing the wrong thing.

---

## 📁 Folders

Folder operations include:

- `create_folder`
- `add_parent`
- `delete_folder`
- `folder_contents`
- `folder_remove_contents`
- `list_dir`
- `list_files`
- `list_folders`
- `clear_folder`
- `copy_folder`
- `move_folder`
- `rename_folder`

Example:

```python
from pyfiler import create_folder, create_file, add_parent, folder_contents

folder = create_folder("project")
file = create_file("main.py", "print('Hello')")
add_parent(file, folder)

for item in folder_contents(folder):
    print(item)
```

---

## 🔎 Searching

pyfiler supports recursive searching by several criteria.

```python
from pyfiler import find, find_files, search_contents, search_regex

print(find(".", "*.py"))
print(find_files(".", "*.py"))
print(search_contents(".", "pyfiler"))
print(search_regex(".", r"def\s+\w+"))
```

Search capabilities include:

| Operation | Purpose |
|---|---|
| `find` | Find matching paths |
| `find_files` | Find files |
| `find_folders` | Find folders |
| `search_contents` | Search file contents |
| `search_regex` | Search contents using regex |
| `find_extension` / `find_by_extension` | Find by extension |
| `find_by_size` | Find files by size |

Search operations use a consistent policy for symbolic links and safely handle many filesystem changes encountered during traversal.

---

## 🧭 Paths

Path helpers make common path operations easier:

```python
from pyfiler import absolute, relative, parent, filename, extension

print(absolute("hello.txt"))
print(relative("project/hello.txt", "project"))
print(parent("project/hello.txt"))
print(filename("project/hello.txt"))
print(extension("project/hello.txt"))
```

Other helpers include:

- `stem`
- `join`
- `normalize`
- `common_path`
- `path_kind`
- `same_type`
- `with_extension`
- `is_pathlike`
- root detection helpers

---

## 📊 Metadata

Inspect filesystem objects with helpers such as:

```python
from pyfiler import metadata

info = metadata("hello.txt")
print(info)
```

Metadata can include:

- Path
- Type
- Size
- Extension
- Timestamps
- File/folder status
- Empty status
- Permissions
- Other filesystem information

Additional helpers include `exists`, `is_file`, `is_folder`, `is_empty`, `file_size`, `file_extension`, `created_at`, `modified_at`, `accessed_at`, `permissions`, `name_of`, `stem_of`, `extension_of`, and `path_kind`.

---

## #️⃣ Hashing and comparison

Calculate file hashes:

```python
from pyfiler import hash_file

print(hash_file("hello.txt", "sha256"))
```

Compare files:

```python
from pyfiler import compare_files

print(compare_files("hello.txt", "copy.txt"))
```

Supported algorithms can be inspected through the hashing API.

---

## 🌳 Directory statistics

Analyze directories with:

- `tree`
- `folder_size`
- `count_files`
- `count_folders`
- `extension_stats`

Example:

```python
from pyfiler import tree, folder_size, count_files

print(tree("project"))
print(folder_size("project"))
print(count_files("project"))
```

These operations account for filesystem changes encountered during traversal rather than assuming a directory remains completely unchanged while it is being inspected.

---

## 🧭 Explorer

`Explorer` provides a rooted interface for applications that should not freely access paths outside a configured directory.

```python
from pyfiler import Explorer

fs = Explorer("workspace", create=True)

fs.create_folder("src")
fs.create_file("src/main.py", "print('Hello')")

print(fs.exists("src/main.py"))
print(fs.get_contents("src/main.py"))
print(fs.metadata("src/main.py"))
```

Paths that attempt to escape the configured root are rejected.

Explorer provides filesystem operations, searching, metadata, path helpers, and security checks through the same rooted interface.

---

## 📱 Storage Information

Use `storage_info` to inspect storage availability, access capabilities, filesystem information, and disk usage.

```python
import pyfiler.storage_info as storage_info

print(storage_info.storage())
print(storage_info.readable())
print(storage_info.writable())
print(storage_info.filesystem())
print(storage_info.free_space())
```

For a complete status object:

```python
info = storage_info.check()

print(info.available)
print(info.readable)
print(info.writable)
print(info.permission_granted)
print(info.total_bytes)
print(info.free_bytes)
print(info.used_bytes)
print(info.filesystem)
print(info.platform)
```

Useful storage helpers include:

- `storage()` / `available()` — determine whether storage is available
- `readable()` / `writable()` — inspect access capabilities
- `can_read()` / `can_write()` / `can_execute()` — permission checks
- `write_test()` — perform a real temporary write test
- `check()` — return structured storage information
- `disk_usage()` — inspect filesystem capacity
- `total_space()` / `free_space()` / `used_space()` — capacity helpers
- `filesystem()` — identify the filesystem when supported
- `home_directory()` / `current_directory()` / `temporary_directory()` — useful locations

> **Platform permissions:** pyfiler can inspect whether storage is accessible, but it cannot grant operating-system permissions. Android, iOS, and other platforms may require the host application to request access through their platform-specific APIs.

---

## 🔐 Security

`Explorer` is designed for applications that need a filesystem boundary.

```python
fs = Explorer("workspace", create=True)

fs.create_file("safe.txt", "allowed")

# Attempts to escape the root are rejected.
fs.create_file("../outside.txt", "blocked")
```

pyfiler performs validation for many invalid filesystem operations and exposes specialized exceptions for security violations, missing paths, file/folder conflicts, invalid lines, invalid patterns, hashing errors, and other failures.

Symbolic links are handled conservatively by recursive search and directory-analysis operations.

---

## ⚠️ Exceptions

All package-specific exceptions inherit from `PyFilerError`.

```python
from pyfiler import PyFilerError

try:
    ...
except PyFilerError as exc:
    print(f"PyFiler error: {exc}")
```

Specific exception classes are available when an application needs more precise error handling.

---

## 🧪 Testing

The repository includes a standalone test suite that does **not require pytest**.

From the repository root:

```bash
python tests/test_pyfiler.py
```

The test runner prints each test result and exits with a non-zero status if a test fails.

---

## 📂 Project Structure

```text
pyfiler/
├── src/
│   └── pyfiler/
│       ├── __init__.py
│       ├── comparison.py
│       ├── exceptions.py
│       ├── explorer.py
│       ├── files.py
│       ├── folders.py
│       ├── hashing.py
│       ├── metadata.py
│       ├── path_utils.py
│       ├── paths.py
│       ├── search.py
│       ├── storage_info.py
│       ├── tree.py
│       └── utils.py
├── tests/
│   └── test_pyfiler.py
├── examples/
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

---

## 📜 License

pyfiler is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

Copyright © 2026 Leila150.
