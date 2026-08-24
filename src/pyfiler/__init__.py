"""Public API for pyfiler.

The names in ``__all__`` are the stable, intentionally exposed API.
Internal helpers from implementation modules are not re-exported.
"""

from .explorer import Explorer
from .storage import StorageInfo, setup_storage
from .files import (
    get_contents,
    add_contents,
    remove_contents,
    edit_contents,
    create_file,
    delete_file,
    copy_file,
    move_file,
    rename_file,
    touch_file,
    file_exists,
    read_file,
    write_file,
    append_file,
    clear_file,
)
from .folders import (
    create_folder,
    add_parent,
    delete_folder,
    folder_contents,
    folder_remove_contents,
    list_dir,
    list_files,
    list_folders,
    clear_folder,
    copy_folder,
    move_folder,
    rename_folder,
)
from .search import (
    find,
    find_files,
    find_folders,
    search_contents,
    search_regex,
    find_extension,
    find_by_size,
)
from .paths import (
    absolute,
    relative,
    parent,
    filename,
    extension,
    stem,
    join,
    normalize,
)
from .metadata import (
    exists,
    is_file,
    is_folder,
    is_empty,
    file_size,
    file_extension,
    created_at,
    modified_at,
    accessed_at,
    metadata,
    permissions,
    file_name,
    file_stem,
    path_kind,
    same_type,
)
from .hashing import hash_file, available_hash_algorithms
from .comparison import compare_files
from .tree import tree, folder_size, count_files, count_folders, extension_stats
from .exceptions import *
from .exceptions import __dict__ as _exception_namespace

# Export every public pyfiler exception as well as the stable API above.
_exception_names = tuple(
    name
    for name, value in _exception_namespace.items()
    if isinstance(value, type)
    and value.__module__ == "pyfiler.exceptions"
    and not name.startswith("_")
)

__all__ = (
    "Explorer",
    "StorageInfo",
    "setup_storage",
    "get_contents",
    "add_contents",
    "remove_contents",
    "edit_contents",
    "create_file",
    "delete_file",
    "copy_file",
    "move_file",
    "rename_file",
    "touch_file",
    "file_exists",
    "read_file",
    "write_file",
    "append_file",
    "clear_file",
    "create_folder",
    "add_parent",
    "delete_folder",
    "folder_contents",
    "folder_remove_contents",
    "list_dir",
    "list_files",
    "list_folders",
    "clear_folder",
    "copy_folder",
    "move_folder",
    "rename_folder",
    "find",
    "find_files",
    "find_folders",
    "search_contents",
    "search_regex",
    "find_extension",
    "find_by_size",
    "absolute",
    "relative",
    "parent",
    "filename",
    "extension",
    "stem",
    "join",
    "normalize",
    "exists",
    "is_file",
    "is_folder",
    "is_empty",
    "file_size",
    "file_extension",
    "created_at",
    "modified_at",
    "accessed_at",
    "metadata",
    "permissions",
    "file_name",
    "file_stem",
    "path_kind",
    "same_type",
    "hash_file",
    "available_hash_algorithms",
    "compare_files",
    "tree",
    "folder_size",
    "count_files",
    "count_folders",
    "extension_stats",
) + _exception_names

__version__ = "0.2.1"
