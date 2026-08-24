"""Path manipulation helpers."""
from pathlib import Path
from .utils import to_path


def absolute(path): return str(to_path(path).resolve())
def relative(path, start=None): return str(to_path(path).resolve().relative_to(to_path(start or Path.cwd()).resolve()))
def parent(path): return str(to_path(path).parent)
def filename(path): return to_path(path).name
def extension(path): return to_path(path).suffix
def stem(path): return to_path(path).stem
def join(*parts): return str(Path(parts[0]).joinpath(*parts[1:])) if parts else ""
def normalize(path): return str(to_path(path).resolve())
