"""Path manipulation helpers."""
from __future__ import annotations
from pathlib import Path
from .utils import to_path


def absolute_path(path): return str(to_path(path).resolve())

def relative_path(path, start=None):
    target = to_path(path).resolve()
    base = to_path(start if start is not None else Path.cwd()).resolve()
    try: return str(target.relative_to(base))
    except ValueError as exc: raise ValueError(f"Path {target} is not inside start path {base}") from exc

def parent_path(path): return str(to_path(path).parent)
def file_name(path): return to_path(path).name
def file_extension(path): return to_path(path).suffix
def file_stem(path): return to_path(path).stem

def join_paths(*parts):
    """Join path components; absolute later components are rejected to avoid silent resets."""
    if not parts: return ""
    if any(part is None for part in parts): raise TypeError("path components cannot be None")
    first = to_path(parts[0])
    result = first
    for part in parts[1:]:
        if not isinstance(part, (str, Path)):
            raise TypeError("path components must be strings or Path objects")
        component = Path(part)
        if component.is_absolute():
            raise ValueError(f"Absolute component would discard previous path: {part!r}")
        result /= component
    return str(result)

def normalize_path(path): return str(to_path(path).resolve())

absolute = absolute_path
relative = relative_path
parent = parent_path
filename = file_name
extension = file_extension
stem = file_stem
join = join_paths
normalize = normalize_path
