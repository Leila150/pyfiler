"""High-level rooted filesystem interface."""
from .utils import to_path, safe_inside
from .files import (
    read_contents, append_contents, remove_contents, replace_contents,
    create_file, delete_file, copy_file, move_file, rename_file,
    touch_file, file_exists, clear_file,
)
from .folders import (
    create_folder, move_into, delete_folder, list_folder,
    remove_from_folder, list_files, list_folders, clear_folder,
    copy_folder, move_folder, rename_folder,
)
from .search import (
    find_paths, find_files, find_folders, find_text, find_pattern,
    find_by_extension, find_by_size,
)
from .metadata import metadata, exists, is_file, is_folder, is_empty
from .exceptions import InvalidRootError, RootNotFoundError


class Explorer:
    """Operate on filesystem paths while enforcing a configured root."""

    def __init__(self, root=".", create=False):
        self.root = to_path(root).resolve()
        if self.root.exists() and not self.root.is_dir():
            raise InvalidRootError(str(self.root))
        if not self.root.exists():
            if create:
                self.root.mkdir(parents=True)
            else:
                raise RootNotFoundError(str(self.root))

    def _path(self, path):
        value = to_path(path)
        return safe_inside(value, self.root) if value.is_absolute() else safe_inside(self.root / value, self.root)

    # Files
    def read_contents(self, name, line_num=None):
        return read_contents(name, line_num, self._path(name))

    def append_contents(self, name, contents):
        return append_contents(name, contents, self._path(name))

    def remove_contents(self, name, line_num=None):
        return remove_contents(name, line_num, self._path(name))

    def replace_contents(self, name, contents):
        return replace_contents(name, contents, self._path(name))

    def create_file(self, name, contents=""):
        return create_file(name, contents, self._path(name))

    def delete_file(self, name):
        return delete_file(name, self._path(name))

    def copy_file(self, source, destination, overwrite=False):
        return copy_file(self._path(source), self._path(destination), overwrite)

    def move_file(self, source, destination, overwrite=False):
        return move_file(self._path(source), self._path(destination), overwrite)

    def rename_file(self, name, new_name):
        return rename_file(self._path(name), new_name)

    def touch_file(self, name):
        return touch_file(name, self._path(name))

    def file_exists(self, name):
        return file_exists(name, self._path(name))

    def clear_file(self, name):
        return clear_file(name, self._path(name))

    # Backwards-compatible file aliases.
    get_contents = read_contents
    add_contents = append_contents
    edit_contents = replace_contents
    read_file = read_contents
    write_file = replace_contents
    append_file = append_contents

    # Folders
    def create_folder(self, name):
        return create_folder(name, trajectory=self._path(name))

    def move_into(self, child, parent):
        return move_into(self._path(child), self._path(parent))

    def delete_folder(self, name, recursive=False):
        return delete_folder(self._path(name), recursive)

    def list_folder(self, name="."):
        return list_folder(self._path(name))

    def remove_from_folder(self, name, child):
        return remove_from_folder(self._path(name), child)

    def list_files(self, name="."):
        return list_files(self._path(name))

    def list_folders(self, name="."):
        return list_folders(self._path(name))

    def clear_folder(self, name="."):
        return clear_folder(self._path(name))

    def copy_folder(self, source, destination, overwrite=False):
        return copy_folder(self._path(source), self._path(destination), overwrite)

    def move_folder(self, source, destination, overwrite=False):
        return move_folder(self._path(source), self._path(destination), overwrite)

    def rename_folder(self, name, new_name):
        return rename_folder(self._path(name), new_name)

    # Backwards-compatible folder aliases.
    add_parent = move_into
    folder_contents = list_folder
    folder_remove_contents = remove_from_folder

    # Search
    def find_paths(self, name=".", pattern="*"):
        return find_paths(self._path(name), pattern)

    def find_files(self, name=".", pattern="*"):
        return find_files(self._path(name), pattern)

    def find_folders(self, name=".", pattern="*"):
        return find_folders(self._path(name), pattern)

    def find_text(self, name=".", text=""):
        return find_text(self._path(name), text)

    def find_pattern(self, name=".", pattern=""):
        return find_pattern(self._path(name), pattern)

    def find_by_extension(self, name=".", extension=""):
        return find_by_extension(self._path(name), extension)

    def find_by_size(self, name=".", minimum=None, maximum=None):
        return find_by_size(self._path(name), minimum, maximum)

    # Backwards-compatible search aliases.
    find = find_paths
    search_contents = find_text
    search_regex = find_pattern
    find_extension = find_by_extension

    # Metadata
    def exists(self, name):
        return exists(self._path(name))

    def is_file(self, name):
        return is_file(self._path(name))

    def is_folder(self, name):
        return is_folder(self._path(name))

    def is_empty(self, name):
        return is_empty(self._path(name))

    def metadata(self, name):
        return metadata(self._path(name))

    def path(self, name="."):
        return self._path(name)

    def relative(self, name="."):
        return self._path(name).relative_to(self.root)
