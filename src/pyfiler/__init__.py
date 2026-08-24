"""Public API for pyfiler.

Canonical APIs are explicitly exported here; compatibility aliases remain
available from their implementation modules and ``pyfiler.operations``.
"""
from .explorer import Explorer
from .storage import StorageInfo, setup_storage
from .files import read_contents, append_contents, remove_contents, replace_contents, create_file, delete_file, copy_file, move_file, rename_file, touch_file, file_exists, clear_file
from .folders import create_folder, move_into, delete_folder, list_folder, remove_from_folder, list_files, list_folders, clear_folder, copy_folder, move_folder, rename_folder
from .search import find_paths, find_files, find_folders, find_text, find_pattern, find_by_extension, find_by_size
from .paths import absolute_path, relative_path, parent_path, file_name, file_extension, file_stem, join_paths, normalize_path, is_absolute, is_relative, has_parent, path_parts, with_name, with_extension, is_root, common_path, relative_to, add_suffix
from .metadata import exists, is_file, is_folder, is_empty, size_of, extension_of, created_at, modified_at, accessed_at, metadata, permissions, name_of, stem_of, path_kind, same_type, is_symlink, device_id, inode, mode, nlink, same_filesystem, same_object
from .hashing import file_hash, hash_algorithms
from .comparison import files_equal
from .tree import directory_tree, directory_size, count_files, count_folders, extension_counts
from . import exceptions as _exceptions
from .exceptions import *

__all__ = [
    "Explorer", "StorageInfo", "setup_storage",
    "read_contents", "append_contents", "remove_contents", "replace_contents", "create_file", "delete_file", "copy_file", "move_file", "rename_file", "touch_file", "file_exists", "clear_file",
    "create_folder", "move_into", "delete_folder", "list_folder", "remove_from_folder", "list_files", "list_folders", "clear_folder", "copy_folder", "move_folder", "rename_folder",
    "find_paths", "find_files", "find_folders", "find_text", "find_pattern", "find_by_extension", "find_by_size",
    "absolute_path", "relative_path", "parent_path", "file_name", "file_extension", "file_stem", "join_paths", "normalize_path", "is_absolute", "is_relative", "has_parent", "path_parts", "with_name", "with_extension", "is_root", "common_path", "relative_to", "add_suffix",
    "exists", "is_file", "is_folder", "is_empty", "size_of", "extension_of", "created_at", "modified_at", "accessed_at", "metadata", "permissions", "name_of", "stem_of", "path_kind", "same_type", "is_symlink", "device_id", "inode", "mode", "nlink", "same_filesystem", "same_object",
    "file_hash", "hash_algorithms", "files_equal", "directory_tree", "directory_size", "count_files", "count_folders", "extension_counts",
]
for _name, _value in vars(_exceptions).items():
    if not _name.startswith("_") and isinstance(_value, type) and _value.__module__ == _exceptions.__name__:
        __all__.append(_name)
__all__ = list(dict.fromkeys(__all__))
__version__ = "0.2.3"
