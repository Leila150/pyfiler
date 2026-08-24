"""Filesystem metadata helpers."""
from .utils import to_path
from .exceptions import PathNotFoundError


def exists(path): return to_path(path).exists()
def is_file(path): return to_path(path).is_file()
def is_folder(path): return to_path(path).is_dir()
def is_empty(path):
    p = to_path(path)
    if not p.exists():
        raise PathNotFoundError(str(p))
    return not any(p.iterdir()) if p.is_dir() else p.stat().st_size == 0

def size_of(path): return to_path(path).stat().st_size
def extension_of(path): return to_path(path).suffix
def created_at(path): return to_path(path).stat().st_ctime
def modified_at(path): return to_path(path).stat().st_mtime
def accessed_at(path): return to_path(path).stat().st_atime

def metadata(path):
    p = to_path(path)
    if not p.exists():
        raise PathNotFoundError(str(p))
    stat = p.stat()
    isfile = p.is_file()
    isfolder = p.is_dir()
    return {
        "name": p.name,
        "path": str(p.resolve()),
        "type": "file" if isfile else "folder" if isfolder else "other",
        "size": stat.st_size,
        "extension": p.suffix if isfile else "",
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "accessed": stat.st_atime,
        "is_file": isfile,
        "is_folder": isfolder,
        "is_empty": not any(p.iterdir()) if isfolder else stat.st_size == 0 if isfile else False,
    }

def permissions(path): return to_path(path).stat().st_mode
def name_of(path): return to_path(path).name
def stem_of(path): return to_path(path).stem

def path_kind(path):
    p = to_path(path)
    if p.is_file(): return "file"
    if p.is_dir(): return "folder"
    if p.exists(): return "other"
    return "missing"

def same_type(first, second):
    return path_kind(first) == path_kind(second) and path_kind(first) in {"file", "folder"}


# Backwards-compatible aliases.
file_size = size_of
file_extension = extension_of
file_name = name_of
file_stem = stem_of
