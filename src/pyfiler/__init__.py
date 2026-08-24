"""Public API for pyfiler.

Only names listed in ``__all__`` are considered part of the stable public
API. Implementation helpers remain private to their modules.
"""

from .explorer import Explorer
from .storage import StorageInfo, setup_storage
from .files import (
    get_contents, add_contents, remove_contents, edit_contents,
    create_file, delete_file, copy_file, move_file, rename_file,
    touch_file, file_exists, read_file, write_file, append_file, clear_file,
)
from .folders import (
    create_folder, add_parent, delete_folder, folder_contents,
    folder_remove_contents, list_dir, list_files, list_folders,
    clear_folder, copy_folder, move_folder, rename_folder,
)
from .search import (
    find, find_files, find_folders, search_contents, search_regex,
    find_extension, find_by_size,
)
from .paths import absolute, relative, parent, filename, extension, stem, join, normalize
from .metadata import (
    exists, is_file, is_folder, is_empty, file_size, file_extension,
    created_at, modified_at, accessed_at, metadata, permissions,
    file_name, file_stem, path_kind, same_type,
)
from .hashing import hash_file, available_hash_algorithms
from .comparison import compare_files
from .tree import tree, folder_size, count_files, count_folders, extension_stats

# Exceptions are public API too.
from . import exceptions as _exceptions
from .exceptions import *

# Explicitly list every stable public symbol. Keeping this list literal makes
# accidental API expansion easy to spot during code review and documentation.
__all__ = [
    # Core
    "Explorer", "StorageInfo", "setup_storage",
    # Files
    "get_contents", "add_contents", "remove_contents", "edit_contents",
    "create_file", "delete_file", "copy_file", "move_file", "rename_file",
    "touch_file", "file_exists", "read_file", "write_file", "append_file",
    "clear_file",
    # Folders
    "create_folder", "add_parent", "delete_folder", "folder_contents",
    "folder_remove_contents", "list_dir", "list_files", "list_folders",
    "clear_folder", "copy_folder", "move_folder", "rename_folder",
    # Search
    "find", "find_files", "find_folders", "search_contents", "search_regex",
    "find_extension", "find_by_size",
    # Paths
    "absolute", "relative", "parent", "filename", "extension", "stem",
    "join", "normalize",
    # Metadata
    "exists", "is_file", "is_folder", "is_empty", "file_size",
    "file_extension", "created_at", "modified_at", "accessed_at",
    "metadata", "permissions", "file_name", "file_stem", "path_kind",
    "same_type",
    # Hashing / comparison
    "hash_file", "available_hash_algorithms", "compare_files",
    # Tree
    "tree", "folder_size", "count_files", "count_folders", "extension_stats",
]

# Add every exception defined by pyfiler.exceptions. This keeps the exception
# hierarchy available from ``import pyfiler`` without exporting unrelated
# imported names from that module.
for _name, _value in vars(_exceptions).items():
    if (
        not _name.startswith("_")
        and isinstance(_value, type)
        and _value.__module__ == _exceptions.__name__
    ):
        __all__.append(_name)

# Prevent duplicate exports while preserving the documented order.
__all__ = list(dict.fromkeys(__all__))

__version__ = "0.2.1"
