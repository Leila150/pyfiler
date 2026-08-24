"""Validation, path, and safety helpers."""
from __future__ import annotations

import os
from pathlib import Path

from .exceptions import (
    EmptyPathError,
    InvalidPathError,
    PathOutsideRootError,
    InvalidLineListError,
    InvalidLineError,
    ContentTypeError,
    PyFilerFileNotFoundError,
    NotAFileError,
    FolderNotFoundError,
    NotAFolderError,
)


def to_path(value):
    """Convert an os.PathLike/string value to a Path with consistent errors."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise EmptyPathError("A path is required.")
    try:
        return Path(value).expanduser()
    except (TypeError, ValueError, OSError) as exc:
        raise InvalidPathError(f"Invalid path: {value!r}") from exc


def ensure_file(value):
    path = to_path(value)
    try:
        if not path.exists():
            raise PyFilerFileNotFoundError(str(path))
        if not path.is_file():
            raise NotAFileError(str(path))
    except PyFilerFileNotFoundError:
        raise
    except NotAFileError:
        raise
    except OSError as exc:
        raise NotAFileError(str(path)) from exc
    return path


def ensure_folder(value):
    path = to_path(value)
    try:
        if not path.exists():
            raise FolderNotFoundError(str(path))
        if not path.is_dir():
            raise NotAFolderError(str(path))
    except FolderNotFoundError:
        raise
    except NotAFolderError:
        raise
    except OSError as exc:
        raise NotAFolderError(str(path)) from exc
    return path


def validate_lines(lines):
    if not isinstance(lines, list) or not all(
        isinstance(x, int) and not isinstance(x, bool) for x in lines
    ):
        raise InvalidLineListError("line_num/lines must be a list of integers.")
    if any(x < 1 for x in lines):
        raise InvalidLineError("Line numbers are 1-based and must be positive.")
    return lines


def validate_contents(contents):
    if not isinstance(contents, str):
        raise ContentTypeError("contents must be a string.")


def safe_inside(path, root):
    """Resolve both paths and require candidate to be within root."""
    candidate = to_path(path).resolve()
    base = to_path(root).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise PathOutsideRootError(f"{candidate} is outside {base}") from exc
    return candidate


def is_pathlike(value):
    """Return whether a value can be passed to pathlib without coercion."""
    return isinstance(value, (str, bytes, os.PathLike))
