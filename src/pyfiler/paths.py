"""Path manipulation helpers."""
from pathlib import Path
from .utils import to_path


def absolute_path(path):
    return str(to_path(path).resolve())


def relative_path(path, start=None):
    return str(to_path(path).resolve().relative_to(to_path(start or Path.cwd()).resolve()))


def parent_path(path):
    return str(to_path(path).parent)


def file_name(path):
    return to_path(path).name


def file_extension(path):
    return to_path(path).suffix


def file_stem(path):
    return to_path(path).stem


def join_paths(*parts):
    return str(Path(parts[0]).joinpath(*parts[1:])) if parts else ""


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
