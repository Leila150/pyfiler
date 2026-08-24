"""Path manipulation helpers with consistent validation and normalization."""
from __future__ import annotations
import os
from pathlib import Path
from .utils import to_path


def _path(value):
    if value is None:
        raise TypeError("path cannot be None")
    return to_path(value)


def _lexical(path):
    """Normalize a path lexically without filesystem canonicalization.

    In particular, this preserves Android prefixes such as /data/user/0
    instead of allowing platform-specific realpath mappings to rewrite them.
    """
    return Path(os.path.normpath(os.path.expanduser(str(_path(path)))))


def absolute_path(path):
    p = _lexical(path)
    if not p.is_absolute():
        p = Path(os.path.abspath(str(p)))
    return str(p)


def relative_path(path, start=None):
    target = Path(absolute_path(path))
    base = Path(absolute_path(start if start is not None else Path.cwd()))
    try:
        return os.path.relpath(str(target), str(base))
    except ValueError as exc:
        raise ValueError(f"Paths cannot be made relative: {target!s}, {base!s}") from exc


def parent_path(path):
    return str(_lexical(path).parent)


def file_name(path): return _path(path).name

def file_extension(path): return _path(path).suffix

def file_stem(path): return _path(path).stem


def join_paths(*parts):
    if not parts:
        raise ValueError("at least one path component is required")
    if any(part is None for part in parts):
        raise TypeError("path components cannot be None")
    result = _path(parts[0])
    for part in parts[1:]:
        if not isinstance(part, (str, Path, os.PathLike)):
            raise TypeError("path components must be path-like")
        component = Path(part)
        if component.is_absolute() or component.anchor:
            raise ValueError(f"Absolute component would discard previous path: {part!r}")
        result /= component
    return str(result)


def normalize_path(path):
    return str(_lexical(path))


def is_absolute(path): return _path(path).is_absolute()

def is_relative(path): return not _path(path).is_absolute()

def has_parent(path):
    p = _path(path)
    return p.parent != p

def path_parts(path): return _path(path).parts


def with_name(path, name):
    if not isinstance(name, str) or not name or name in {".", ".."}:
        raise ValueError("name must be a non-empty filename")
    if Path(name).name != name:
        raise ValueError("name must not contain directory separators")
    return str(_path(path).with_name(name))


def with_extension(path, extension):
    if not isinstance(extension, str) or not extension.strip():
        raise ValueError("extension must be a non-empty string")
    extension = extension.strip()
    extension = extension if extension.startswith(".") else "." + extension
    if extension == ".":
        raise ValueError("extension must contain characters")
    return str(_path(path).with_suffix(extension))


def is_root(path):
    p = _lexical(path)
    return p.parent == p


def common_path(*paths):
    if not paths:
        raise ValueError("at least one path is required")
    values = [absolute_path(path) for path in paths]
    try:
        return os.path.commonpath(values)
    except ValueError as exc:
        raise ValueError("paths do not share a common root") from exc


def relative_to(path, base):
    target = _lexical(path)
    root = _lexical(base)
    if not target.is_absolute() and root.is_absolute():
        target = Path(absolute_path(target))
    if not root.is_absolute() and target.is_absolute():
        root = Path(absolute_path(root))
    try:
        return str(target.relative_to(root))
    except ValueError as exc:
        raise ValueError(f"{target} is not inside {root}") from exc


def add_suffix(path, suffix):
    if not isinstance(suffix, str):
        raise TypeError("suffix must be a string")
    p = _path(path)
    return str(p.with_name(p.stem + suffix + p.suffix))


absolute = absolute_path
relative = relative_path
parent = parent_path
filename = file_name
extension = file_extension
stem = file_stem
join = join_paths
normalize = normalize_path
parts = path_parts
