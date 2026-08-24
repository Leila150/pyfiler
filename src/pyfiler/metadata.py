"""Filesystem metadata helpers."""
from __future__ import annotations

from .exceptions import PathNotFoundError
from .utils import to_path


def _existing(path):
    p = to_path(path)
    if not p.exists():
        raise PathNotFoundError(str(p))
    return p


def exists(path):
    return to_path(path).exists()


def is_file(path):
    return to_path(path).is_file()


def is_folder(path):
    return to_path(path).is_dir()


def is_empty(path):
    p = _existing(path)
    if p.is_dir():
        return not any(p.iterdir())
    if p.is_file():
        return p.stat().st_size == 0
    return False


def size_of(path):
    return _existing(path).stat().st_size


def extension_of(path):
    p = _existing(path)
    return p.suffix if p.is_file() else ""


def created_at(path):
    return _existing(path).stat().st_ctime


def modified_at(path):
    return _existing(path).stat().st_mtime


def accessed_at(path):
    return _existing(path).stat().st_atime


def metadata(path):
    p = _existing(path)
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
        "is_empty": (not any(p.iterdir())) if isfolder else (stat.st_size == 0 if isfile else False),
    }


def permissions(path):
    return _existing(path).stat().st_mode


def name_of(path):
    return _existing(path).name


def stem_of(path):
    return _existing(path).stem


def path_kind(path):
    p = to_path(path)
    if p.is_file():
        return "file"
    if p.is_dir():
        return "folder"
    if p.exists():
        return "other"
    return "missing"


def same_type(first, second):
    first_kind = path_kind(first)
    second_kind = path_kind(second)
    return first_kind == second_kind and first_kind in {"file", "folder"}


# Backwards-compatible aliases.
file_size = size_of
file_extension = extension_of
file_name = name_of
file_stem = stem_of
