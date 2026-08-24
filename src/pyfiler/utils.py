"""Internal validation and path helpers."""
from pathlib import Path
from .exceptions import EmptyPathError, InvalidPathError, PathOutsideRootError, InvalidLineListError, InvalidLineError, ContentTypeError


def to_path(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        raise EmptyPathError("A path is required.")
    try:
        return Path(value).expanduser()
    except (TypeError, ValueError) as exc:
        raise InvalidPathError(f"Invalid path: {value!r}") from exc


def ensure_file(value):
    from .exceptions import PyFilerFileNotFoundError, NotAFileError
    path = to_path(value)
    if not path.exists():
        raise PyFilerFileNotFoundError(str(path))
    if not path.is_file():
        raise NotAFileError(str(path))
    return path


def ensure_folder(value):
    from .exceptions import FolderNotFoundError, NotAFolderError
    path = to_path(value)
    if not path.exists():
        raise FolderNotFoundError(str(path))
    if not path.is_dir():
        raise NotAFolderError(str(path))
    return path


def validate_lines(lines):
    if not isinstance(lines, list) or not all(isinstance(x, int) and not isinstance(x, bool) for x in lines):
        raise InvalidLineListError("line_num/lines must be a list of integers.")
    if any(x < 1 for x in lines):
        raise InvalidLineError("Line numbers are 1-based and must be positive.")
    return lines


def validate_contents(contents):
    if not isinstance(contents, str):
        raise ContentTypeError("contents must be a string.")


def safe_inside(path, root):
    candidate, base = to_path(path).resolve(), to_path(root).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise PathOutsideRootError(f"{candidate} is outside {base}") from exc
    return candidate
