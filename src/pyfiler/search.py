"""Recursive file, folder, and content search."""
from __future__ import annotations

import re
from pathlib import Path

from .exceptions import InvalidExtensionError, InvalidPatternError, SearchError
from .utils import ensure_folder


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    return name


def _sorted_paths(paths):
    return sorted(paths, key=lambda p: (str(p).casefold(), str(p)))


def _walk(path, pattern="*"):
    """Yield matching paths while converting traversal failures to SearchError."""
    root = ensure_folder(path)
    try:
        iterator = root.rglob(pattern)
        for item in iterator:
            yield item
    except OSError as exc:
        raise SearchError(f"Unable to search {root}: {exc}") from exc


def find_paths(path, name="*"):
    """Find files and folders recursively by glob name in deterministic order."""
    return _sorted_paths(_walk(path, _validate_name(name)))


def find_files(path, name="*"):
    """Find files recursively by glob name."""
    return _sorted_paths(p for p in find_paths(path, name) if p.is_file())


def find_folders(path, name="*"):
    """Find folders recursively by glob name."""
    return _sorted_paths(p for p in find_paths(path, name) if p.is_dir())


def _validate_encoding(encoding):
    if not isinstance(encoding, str) or not encoding.strip():
        raise ValueError("encoding must be a non-empty string")
    return encoding


def _read_lines(path, encoding):
    try:
        with path.open("r", encoding=encoding, newline="") as handle:
            for line in handle:
                yield line
    except (OSError, UnicodeError) as exc:
        raise SearchError(f"Unable to read {path}: {exc}") from exc


def find_text(path, text, encoding="utf-8"):
    """Find files containing text without loading each file into memory."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    encoding = _validate_encoding(encoding)
    results = []
    for item in _walk(path):
        try:
            is_file = item.is_file()
        except OSError as exc:
            raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if not is_file:
            continue
        if any(text in line for line in _read_lines(item, encoding)):
            results.append(item)
    return _sorted_paths(results)


def find_pattern(path, pattern, encoding="utf-8"):
    """Find files whose individual lines match a regular expression.

    Matching is streamed line-by-line so large files do not need to be loaded
    into memory. Patterns spanning multiple lines are therefore not supported.
    """
    if not isinstance(pattern, str) or not pattern:
        raise InvalidPatternError("Pattern is required.")
    encoding = _validate_encoding(encoding)
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        raise InvalidPatternError(str(exc)) from exc
    results = []
    for item in _walk(path):
        try:
            is_file = item.is_file()
        except OSError as exc:
            raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if not is_file:
            continue
        if any(regex.search(line) for line in _read_lines(item, encoding)):
            results.append(item)
    return _sorted_paths(results)


def find_by_extension(path, extension):
    """Find files by final extension, case-insensitively."""
    if not isinstance(extension, str) or not extension.strip():
        raise InvalidExtensionError("Extension is required.")
    extension = extension.strip()
    extension = extension if extension.startswith(".") else "." + extension
    if extension == ".":
        raise InvalidExtensionError("Extension is required.")
    return _sorted_paths(
        item
        for item in _walk(path)
        if item.is_file() and item.suffix.casefold() == extension.casefold()
    )


def find_by_size(path, minimum=None, maximum=None):
    """Find files within an optional inclusive byte-size range."""
    if minimum is not None:
        if not isinstance(minimum, int) or isinstance(minimum, bool):
            raise TypeError("minimum must be an integer or None")
        if minimum < 0:
            raise ValueError("minimum cannot be negative")
    if maximum is not None:
        if not isinstance(maximum, int) or isinstance(maximum, bool):
            raise TypeError("maximum must be an integer or None")
        if maximum < 0:
            raise ValueError("maximum cannot be negative")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError("minimum cannot be greater than maximum")
    results = []
    for item in _walk(path):
        if not item.is_file():
            continue
        try:
            size = item.stat().st_size
        except OSError as exc:
            raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if minimum is not None and size < minimum:
            continue
        if maximum is not None and size > maximum:
            continue
        results.append(item)
    return _sorted_paths(results)


# Backwards-compatible aliases.
find = find_paths
search_contents = find_text
search_regex = find_pattern
find_extension = find_by_extension
