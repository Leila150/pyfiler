# pyfiler

**pyfiler** is a zero-dependency Python filesystem toolkit for creating, reading, editing, moving, copying, searching, inspecting, hashing, and organizing files and folders.

It is designed around two styles: simple filesystem functions and the rooted `Explorer` API for safer application-level file management.

> **Status:** active development — API may grow, but the public functions documented here are the intended interface.

## Highlights

- 📄 File creation and content editing
- 📝 Read specific 1-based lines
- 📁 Folder creation and organization
- 🔎 Recursive name, extension, text, regex, and size searching
- 🧭 Path helpers
- 📊 Metadata and filesystem inspection
- 🔐 Root-restricted `Explorer`
- #️⃣ File hashing and comparison
- 🌳 Directory trees and statistics
- 📱 Cross-platform storage information
- 🚫 No third-party runtime dependencies

## Installation

```bash
pip install .
```

For development from a cloned repository:

```bash
pip install -e .
```

## File API

```python
from pyfiler import (
    create_file,
    get_contents,
    add_contents,
    remove_contents,
    edit_contents,
)

create_file("hello.txt", "line one\nline two\nline three\n")

print(get_contents("hello.txt"))
print(get_contents("hello.txt", [1, 3]))

add_contents("hello.txt", "line four\n")
remove_contents("hello.txt", [2])
edit_contents("hello.txt", "completely replaced")
```

### File operations

| Function | Purpose |
|---|---|
| `create_file(name, contents="", trajectory=None)` | Create a new file |
| `get_contents(name, line_num=None, trajectory=None)` | Read all or selected lines |
| `add_contents(name, contents, trajectory=None)` | Append text |
| `remove_contents(name, line_num=None, trajectory=None)` | Remove selected lines or clear the file |
| `edit_contents(name, contents, trajectory=None)` | Replace the complete file |
| `delete_file(name, trajectory=None)` | Delete a file |
| `copy_file(source, destination, overwrite=False)` | Copy a file |
| `move_file(source, destination, overwrite=False)` | Move a file |
| `rename_file(name, new_name)` | Rename a file |
| `touch_file(name, trajectory=None)` | Create or touch a file |
| `file_exists(name, trajectory=None)` | Check whether a path is a file |
| `clear_file(name, trajectory=None)` | Empty an existing file |

`line_num` is a list of positive integers and uses **1-based line numbering**.

`trajectory` lets you supply the physical path separately from the logical `name`.

## Folder API

```python
from pyfiler import create_folder, create_file, add_parent, folder_contents

folder = create_folder("project")
file = create_file("main.py", "print('hello')")
add_parent(file, folder)

for item in folder_contents(folder):
    print(item)
```

Available folder operations include `create_folder`, `add_parent`, `delete_folder`, `folder_contents`, `folder_remove_contents`, `list_dir`, `list_files`, `list_folders`, `clear_folder`, `copy_folder`, `move_folder`, and `rename_folder`.

`create_folder(..., contents=...)` can populate a new folder from existing files or folders.

## Explorer

`Explorer` confines relative and absolute paths to one configured root.

```python
from pyfiler import Explorer

fs = Explorer("workspace", create=True)
fs.create_folder("src")
fs.create_file("src/main.py", "print('Hello')")

print(fs.exists("src/main.py"))
print(fs.get_contents("src/main.py"))
print(fs.metadata("src/main.py"))
```

Explorer also exposes file operations, folder operations, searching, metadata checks, copying, moving, and path helpers. Attempts to escape the root are rejected.

## Search

```python
from pyfiler import find, find_files, search_contents, search_regex

print(find(".", "*.py"))
print(find_files(".", "*.py"))
print(search_contents(".", "pyfiler"))
print(search_regex(".", r"def\\s+\\w+"))
```

## Metadata and paths

Useful helpers include `exists`, `is_file`, `is_folder`, `is_empty`, `file_size`, `file_extension`, `created_at`, `modified_at`, `accessed_at`, `metadata`, `permissions`, `file_name`, `file_stem`, `path_kind`, `same_type`, `absolute`, `relative`, `parent`, `filename`, `extension`, `stem`, `join`, and `normalize`.

`metadata()` returns the path, type, size, extension, timestamps, and boolean file/folder/empty information.

## Hashing and comparison

```python
from pyfiler import hash_file, compare_files

print(hash_file("hello.txt", "sha256"))
print(compare_files("hello.txt", "copy.txt"))
```

## Trees and statistics

`tree`, `folder_size`, `count_files`, `count_folders`, and `extension_stats` provide quick directory analysis.

## Storage

```python
from pyfiler import setup_storage

storage = setup_storage()
print(storage.platform)
print(storage.path)
print(storage.permission_granted)
```

`setup_storage()` provides filesystem/storage information. Python itself cannot silently grant Android or iOS OS permissions; the host application must request those permissions through the platform APIs.

## Exceptions

All package-specific exceptions inherit from `PyFilerError`. pyfiler provides specialized errors for missing paths, invalid lines, file/folder conflicts, copying/moving failures, security violations, storage problems, hashing, comparisons, and other filesystem operations.

Catch `PyFilerError` when you want one handler for pyfiler failures, or catch a specific exception when you need precise handling.

## Testing

The repository test suite uses the Python standard library and can be run without installing pytest:

```bash
python tests/test_pyfiler.py
```

## Project layout

```text
pyfiler/
├── src/pyfiler/
│   ├── __init__.py
│   ├── comparison.py
│   ├── exceptions.py
│   ├── explorer.py
│   ├── files.py
│   ├── folders.py
│   ├── hashing.py
│   ├── metadata.py
│   ├── paths.py
│   ├── search.py
│   ├── storage.py
│   ├── tree.py
│   └── utils.py
├── tests/
├── examples/
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

## License

pyfiler is **proprietary software**. It is not released under MIT, Apache-2.0, GPL, BSD, or another open-source license.

See [`LICENSE`](LICENSE) for the complete terms. In particular, copying, modifying, redistributing, sublicensing, or publishing derivative versions is not permitted without explicit written authorization from the copyright holder.

Copyright © 2026 Leila150. All rights reserved.
