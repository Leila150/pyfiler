"""Recursive file, folder and content search."""
import re
from .utils import ensure_folder
from .exceptions import InvalidPatternError, InvalidExtensionError


def find(path, name="*"):
    return list(ensure_folder(path).rglob(name))


def find_files(path, name="*"):
    return [p for p in find(path, name) if p.is_file()]


def find_folders(path, name="*"):
    return [p for p in find(path, name) if p.is_dir()]


def search_contents(path, text, encoding="utf-8"):
    results=[]
    for p in ensure_folder(path).rglob("*"):
        if p.is_file():
            try:
                if text in p.read_text(encoding=encoding): results.append(p)
            except (OSError, UnicodeError): pass
    return results


def search_regex(path, pattern, encoding="utf-8"):
    try: regex=re.compile(pattern)
    except re.error as exc: raise InvalidPatternError(str(exc)) from exc
    results=[]
    for p in ensure_folder(path).rglob("*"):
        if p.is_file():
            try:
                if regex.search(p.read_text(encoding=encoding)): results.append(p)
            except (OSError, UnicodeError): pass
    return results


def find_extension(path, extension):
    if not isinstance(extension, str) or not extension: raise InvalidExtensionError("Extension is required.")
    extension = extension if extension.startswith(".") else "." + extension
    return [p for p in ensure_folder(path).rglob("*") if p.is_file() and p.suffix.lower()==extension.lower()]


def find_by_size(path, minimum=None, maximum=None):
    return [p for p in ensure_folder(path).rglob("*") if p.is_file() and (minimum is None or p.stat().st_size>=minimum) and (maximum is None or p.stat().st_size<=maximum)]
