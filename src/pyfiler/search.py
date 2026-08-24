"""Recursive file, folder and content search."""

from __future__ import annotations

import re

from .exceptions import InvalidExtensionError, InvalidPatternError
from .utils import ensure_folder


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("name must be a non-empty string")
    return name


def find_paths(path, name="*"):
    """Find files and folders recursively by glob name."""
    return list(ensure_folder(path).rglob(_validate_name(name)))


def find_files(path, name="*"):
    """Find files recursively by glob name."""
    return [p for p in find_paths(path, name) if p.is_file()]


def find_folders(path, name="*"):
    """Find folders recursively by glob name."""
    return [p for p in find_paths(path, name) if p.is_dir()]


def find_text(path, text, encoding="utf-8"):
    """Find files containing the supplied text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(encoding, str) or not encoding:
        raise ValueError("encoding must be a non-empty string")
    results = []
    for item in ensure_folder(path).rglob("*"):
        if item.is_file():
            try:
                if text in item.read_text(encoding=encoding):
                    results.append(item)
            except (OSError, UnicodeError):
                continue
    return results


def find_pattern(path, pattern, encoding="utf-8"):
    """Find files whose contents match a regular expression."""
    if not isinstance(pattern, str) or not pattern:
        raise InvalidPatternError("Pattern is required.")
    if not isinstance(encoding, str) or not encoding:
        raise ValueError("encoding must be a non-empty string")
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        raise InvalidPatternError(str(exc)) from exc
    results = []
    for item in ensure_folder(path).rglob("*"):
        if item.is_file():
            try:
                if regex.search(item.read_text(encoding=encoding)):
                    results.append(item)
            except (OSError, UnicodeError):
                continue
    return results


def find_by_extension(path, extension):
    """Find files recursively by extension."""
    if not isinstance(extension, str) or not extension.strip():
        raise InvalidExtensionError("Extension is required.")
    extension = extension.strip()
    extension = extension if extension.startswith(".") else "." + extension
    if extension == ".":
        raise InvalidExtensionError("Extension is required.")
    return [
        item
        for item in ensure_folder(path).rglob("*")
        if item.is_file() and item.suffix.lower() == extension.lower()
    ]


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
    for item in ensure_folder(path).rglob("*"):
        if not item.is_file():
            continue
        try:
            size = item.stat().st_size
        except OSError:
            continue
        if minimum is not None and size < minimum:
            continue
        if maximum is not None and size > maximum:
            continue
        results.append(item)
    return results


# Backwards-compatible aliases.
find = find_paths
search_contents = find_text
search_regex = find_pattern
find_extension = find_by_extension
