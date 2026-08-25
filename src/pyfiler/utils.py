"""Validation, path, and safety helpers."""
from __future__ import annotations
import os
from pathlib import Path
from .exceptions import EmptyPathError,InvalidPathError,PathOutsideRootError,InvalidLineListError,InvalidLineError,ContentTypeError,PyFilerFileNotFoundError,NotAFileError,FolderNotFoundError,NotAFolderError,SymlinkTraversalError

def to_path(value):
    if value is None or (isinstance(value,str) and not value.strip()): raise EmptyPathError("A path is required.")
    try: return Path(value).expanduser()
    except (TypeError,ValueError,OSError) as exc: raise InvalidPathError(f"Invalid path: {value!r}") from exc

def ensure_file(value):
    path=to_path(value)
    try: path.stat()
    except FileNotFoundError as exc: raise PyFilerFileNotFoundError(str(path)) from exc
    except OSError as exc: raise NotAFileError(str(path)) from exc
    if not path.is_file(): raise NotAFileError(str(path))
    return path

def ensure_folder(value):
    path=to_path(value)
    try: path.stat()
    except FileNotFoundError as exc: raise FolderNotFoundError(str(path)) from exc
    except OSError as exc: raise NotAFolderError(str(path)) from exc
    if not path.is_dir(): raise NotAFolderError(str(path))
    return path

def validate_lines(lines):
    if not isinstance(lines,list) or not all(isinstance(x,int) and not isinstance(x,bool) for x in lines): raise InvalidLineListError("line_num/lines must be a list of integers.")
    if any(x<1 for x in lines): raise InvalidLineError("Line numbers are 1-based and must be positive.")
    return lines

def validate_contents(contents):
    if not isinstance(contents,str): raise ContentTypeError("contents must be a string.")

def _reject_symlink_components(candidate):
    candidate=Path(candidate); current=Path(candidate.anchor) if candidate.anchor else Path(".")
    for part in candidate.parts:
        if part==candidate.anchor: continue
        current=current/part
        try:
            if current.is_symlink(): raise SymlinkTraversalError(f"Symlink path component is not allowed: {current}")
        except SymlinkTraversalError: raise
        except OSError as exc: raise SymlinkTraversalError(f"Unable to inspect path component: {current}") from exc

def safe_inside(path,root,reject_symlinks=False):
    raw=to_path(path); base=to_path(root).resolve(strict=True); candidate=raw if raw.is_absolute() else base/raw
    if reject_symlinks: _reject_symlink_components(candidate)
    try: resolved=candidate.resolve(strict=False)
    except OSError as exc: raise PathOutsideRootError(f"Unable to resolve path: {candidate}") from exc
    try: resolved.relative_to(base)
    except ValueError as exc: raise PathOutsideRootError(f"{resolved} is outside {base}") from exc
    if reject_symlinks: _reject_symlink_components(candidate)
    try: resolved_again=candidate.resolve(strict=False); resolved_again.relative_to(base)
    except ValueError as exc: raise PathOutsideRootError(f"{resolved_again} is outside {base}") from exc
    except OSError as exc: raise PathOutsideRootError(f"Unable to revalidate path: {candidate}") from exc
    if resolved_again!=resolved: raise PathOutsideRootError(f"Path changed during security validation: {candidate}")
    return resolved_again

def is_pathlike(value):
    """Return True only when the value is a non-empty path accepted by PyFiler."""
    if value is None: return False
    if isinstance(value,str): return bool(value.strip())
    return isinstance(value,os.PathLike)
