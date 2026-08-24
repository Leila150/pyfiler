"""Path manipulation helpers."""

from __future__ import annotations

from pathlib import Path

from .utils import to_path


def absolute_path(path):
    """Return the absolute, normalized path as a string."""
    return str(to_path(path).resolve())


def relative_path(path, start=None):
    """Return ``path`` relative to ``start`` (or the current directory)."""
    target = to_path(path).resolve()
    base = to_path(start if start is not None else Path.cwd()).resolve()
    try:
        return str(target.relative_to(base))
    except ValueError as exc:
        raise ValueError(
            f"Path {target!s} is not inside start path {base!s}"
        ) from exc


def parent_path(path):
    return str(to_path(path).parent)


def file_name(path):
    return to_path(path).name


def file_extension(path):
    return to_path(path).suffix


def file_stem(path):
    return to_path(path).stem


def join_paths(*parts):
    """Join path components without silently dropping earlier components."""
    if not parts:
        return ""
    if any(part is None for part in parts):
        raise TypeError("path components cannot be None")
    return str(Path(parts[0]).joinpath(*(str(part) for part in parts[1:])))


def normalize_path(path):
    return str(to_path(path).resolve())


# Backwards-compatible aliases.
absolute = absolute_path
relative = relative_path
parent = parent_path
filename = file_name
extension = file_extension
stem = file_stem
join = join_paths
normalize = normalize_path
