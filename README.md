# pyfiler

pyfiler is a powerful Python filesystem toolkit for managing files, folders, paths, metadata, searching, hashing, comparisons, directory trees, and storage. It provides simple functions and a high-level `Explorer` API for safe, flexible, and efficient filesystem operations.

## Structure

```text
pyfiler/
├── src/pyfiler/
│   ├── __init__.py
│   ├── explorer.py
│   ├── files.py
│   ├── folders.py
│   ├── search.py
│   ├── paths.py
│   ├── metadata.py
│   ├── hashing.py
│   ├── comparison.py
│   ├── tree.py
│   ├── storage.py
│   ├── exceptions.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_pyfiler.py
├── examples/
│   ├── basic.py
│   ├── explorer.py
│   ├── searching.py
│   └── metadata.py
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

## Core file API

```python
from pyfiler import *

create_file("hello.txt", "Hello")
print(get_contents("hello.txt"))
add_contents("hello.txt", "\nMore text")
remove_contents("hello.txt", [1])
edit_contents("hello.txt", "Replacement contents")
```

`get_contents`, `add_contents`, `remove_contents`, and `edit_contents` support an optional `trajectory` so the logical name and physical path can be separated when needed.

Line numbers are 1-based lists of integers, for example `get_contents("file.txt", [1, 4, 7])`.

## Folder API

```python
folder = create_folder("project")
file = create_file("main.py", "print('hello')")
add_parent(file, folder)

print(folder_contents(folder))
folder_remove_contents(folder, ["main.py"])
```

Folders can also be created with existing filesystem children through the optional `contents` argument.

## Explorer

```python
from pyfiler import Explorer

fs = Explorer("workspace", create=True)
fs.create_folder("src")
fs.create_file("src/main.py", "print('Hello')")
print(fs.get_contents("src/main.py"))
print(fs.folder_contents("src"))
```

`Explorer` keeps operations inside its configured root and raises a path-security exception if a path attempts to escape it.

## Search and inspection

pyfiler includes recursive name search, extension filtering, text search, regular-expression search, size filtering, metadata, directory trees, file counts, folder counts, extension statistics, hashes, and file comparisons.

## Storage

```python
from pyfiler import setup_storage

storage = setup_storage()
print(storage.platform)
print(storage.path)
print(storage.permission_granted)
```

The storage API provides a cross-platform abstraction. Native Android and iOS permission dialogs must be handled by the host application/runtime because ordinary Python code cannot independently grant operating-system permissions.

## Exceptions

All pyfiler-specific errors inherit from `PyFilerError`. Specialized exceptions also inherit from relevant Python built-ins where appropriate, making normal Python exception handling possible.

## Installation

```text
pip install .
```

## Testing

```text
pytest
```
