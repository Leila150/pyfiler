"""Validation, path, and safety helpers."""
from __future__ import annotations
import os
from pathlib import Path
from .exceptions import EmptyPathError, InvalidPathError, PathOutsideRootError, InvalidLineListError, InvalidLineError, ContentTypeError, PyFilerFileNotFoundError, NotAFileError, FolderNotFoundError, NotAFolderError

def to_path(value):
    if value is None or (isinstance(value,str) and not value.strip()): raise EmptyPathError("A path is required.")
    try: return Path(value).expanduser()
    except (TypeError,ValueError,OSError) as exc: raise InvalidPathError(f"Invalid path: {value!r}") from exc

def ensure_file(value):
    path=to_path(value)
    try:
        if not path.exists(): raise PyFilerFileNotFoundError(str(path))
        if not path.is_file(): raise NotAFileError(str(path))
    except (PyFilerFileNotFoundError,NotAFileError): raise
    except OSError as exc: raise NotAFileError(str(path)) from exc
    return path

def ensure_folder(value):
    path=to_path(value)
    try:
        if not path.exists(): raise FolderNotFoundError(str(path))
        if not path.is_dir(): raise NotAFolderError(str(path))
    except (FolderNotFoundError,NotAFolderError): raise
    except OSError as exc: raise NotAFolderError(str(path)) from exc
    return path

def validate_lines(lines):
    if not isinstance(lines,list) or not all(isinstance(x,int) and not isinstance(x,bool) for x in lines): raise InvalidLineListError("line_num/lines must be a list of integers.")
    if any(x<1 for x in lines): raise InvalidLineError("Line numbers are 1-based and must be positive.")
    return lines

def validate_contents(contents):
    if not isinstance(contents,str): raise ContentTypeError("contents must be a string.")

def safe_inside(path, root, reject_symlinks=False):
    """Resolve and enforce a root boundary; optionally reject symlink components."""
    raw=to_path(path); base=to_path(root).resolve()
    candidate=raw if raw.is_absolute() else base/raw
    if reject_symlinks:
        current=Path(candidate.anchor) if candidate.anchor else Path('.')
        for part in candidate.parts:
            if part == candidate.anchor: continue
            current=current/part
            try:
                if current.is_symlink(): raise PathOutsideRootError(f"Symlink path component is not allowed: {current}")
            except OSError as exc: raise PathOutsideRootError(f"Unable to inspect path component: {current}") from exc
    candidate=raw.resolve()
    try: candidate.relative_to(base)
    except ValueError as exc: raise PathOutsideRootError(f"{candidate} is outside {base}") from exc
    return candidate

def is_pathlike(value): return isinstance(value,(str,bytes,os.PathLike))
