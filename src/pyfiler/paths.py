"""Path manipulation helpers with consistent validation and normalization."""
from __future__ import annotations
import os
from pathlib import Path
from .utils import to_path

def absolute_path(path): return str(to_path(path).resolve(strict=False))
def relative_path(path, start=None):
    target=to_path(path).resolve(strict=False); base=to_path(start if start is not None else Path.cwd()).resolve(strict=False)
    try: return os.path.relpath(target, base)
    except ValueError as exc: raise ValueError(f"Paths cannot be made relative: {target!s}, {base!s}") from exc
def parent_path(path): return str(to_path(path).resolve(strict=False).parent)
def file_name(path): return to_path(path).name
def file_extension(path): return to_path(path).suffix
def file_stem(path): return to_path(path).stem
def join_paths(*parts):
    if not parts: raise ValueError("at least one path component is required")
    if any(part is None for part in parts): raise TypeError("path components cannot be None")
    result=to_path(parts[0])
    for part in parts[1:]:
        if not isinstance(part,(str,Path,os.PathLike)): raise TypeError("path components must be path-like")
        component=Path(part)
        if component.is_absolute() or component.anchor: raise ValueError(f"Absolute component would discard previous path: {part!r}")
        result/=component
    return str(result)
def normalize_path(path): return str(to_path(path).resolve(strict=False))
absolute=absolute_path; relative=relative_path; parent=parent_path; filename=file_name; extension=file_extension; stem=file_stem; join=join_paths; normalize=normalize_path
