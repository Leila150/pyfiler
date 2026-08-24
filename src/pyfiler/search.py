"""Recursive file, folder and content search."""
import re
from .utils import ensure_folder
from .exceptions import InvalidPatternError, InvalidExtensionError


def find_paths(path, name="*"):
    """Find files and folders recursively by glob name."""
    return list(ensure_folder(path).rglob(name))


def find_files(path, name="*"):
    return [p for p in find_paths(path, name) if p.is_file()]


def find_folders(path, name="*"):
    return [p for p in find_paths(path, name) if p.is_dir()]


def find_text(path, text, encoding="utf-8"):
    """Find files containing the supplied text."""
    results = []
    for p in ensure_folder(path).rglob("*"):
        if p.is_file():
            try:
                if text in p.read_text(encoding=encoding):
                    results.append(p)
            except (OSError, UnicodeError):
                pass
    return results


def find_pattern(path, pattern, encoding="utf-8"):
    """Find files whose contents match a regular expression."""
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        raise InvalidPatternError(str(exc)) from exc
    results = []
    for p in ensure_folder(path).rglob("*"):
        if p.is_file():
            try:
                if regex.search(p.read_text(encoding=encoding)):
                    results.append(p)
            except (OSError, UnicodeError):
                pass
    return results


def find_by_extension(path, extension):
    """Find files recursively by extension."""
    if not isinstance(extension, str) or not extension:
        raise InvalidExtensionError("Extension is required.")
    extension = extension if extension.startswith(".") else "." + extension
    return [
        p for p in ensure_folder(path).rglob("*")
        if p.is_file() and p.suffix.lower() == extension.lower()
    ]


def find_by_size(path, minimum=None, maximum=None):
    """Find files within an optional byte-size range."""
    return [
        p for p in ensure_folder(path).rglob("*")
        if p.is_file()
        and (minimum is None or p.stat().st_size >= minimum)
        and (maximum is None or p.stat().st_size <= maximum)
    ]


# Backwards-compatible aliases.
find = find_paths
search_contents = find_text
search_regex = find_pattern
find_extension = find_by_extension
