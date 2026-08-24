"""Filesystem metadata helpers."""
from __future__ import annotations
import stat
from .exceptions import PathNotFoundError, MetadataUnavailableError
from .utils import to_path


def _existing(path):
    p = to_path(path)
    try: p.stat()
    except FileNotFoundError as exc: raise PathNotFoundError(str(p)) from exc
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
    return p

def exists(path): return to_path(path).exists()
def is_file(path): return to_path(path).is_file()
def is_folder(path): return to_path(path).is_dir()

def is_empty(path):
    p = _existing(path)
    try:
        if p.is_dir(): return not any(p.iterdir())
        return p.is_file() and p.stat().st_size == 0
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc

def size_of(path): return _existing(path).stat().st_size

def extension_of(path):
    p = _existing(path)
    return p.suffix if p.is_file() else ""

def created_at(path): return _existing(path).stat().st_ctime
def modified_at(path): return _existing(path).stat().st_mtime
def accessed_at(path): return _existing(path).stat().st_atime

def metadata(path):
    p = _existing(path)
    try:
        st = p.stat()
        isfile, isfolder = stat.S_ISREG(st.st_mode), stat.S_ISDIR(st.st_mode)
        empty = (not any(p.iterdir())) if isfolder else (st.st_size == 0 if isfile else False)
        return {"name": p.name, "path": str(p.resolve()), "type": "file" if isfile else "folder" if isfolder else "other", "size": st.st_size, "extension": p.suffix if isfile else "", "created": st.st_ctime, "modified": st.st_mtime, "accessed": st.st_atime, "is_file": isfile, "is_folder": isfolder, "is_empty": empty}
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc

def permissions(path): return stat.S_IMODE(_existing(path).stat().st_mode)
def name_of(path): return _existing(path).name
def stem_of(path): return _existing(path).stem

def path_kind(path):
    p = to_path(path)
    try:
        if p.is_file(): return "file"
        if p.is_dir(): return "folder"
        if p.exists(): return "other"
        return "missing"
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc

def same_type(first, second):
    a, b = path_kind(first), path_kind(second)
    return a == b and a in {"file", "folder"}

file_size = size_of
file_extension = extension_of
file_name = name_of
file_stem = stem_of
