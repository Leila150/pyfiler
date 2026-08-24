"""File creation, reading, editing, copying and deletion."""
from pathlib import Path
import shutil
from .utils import to_path, ensure_file, validate_lines, validate_contents
from .exceptions import *


def get_contents(name, line_num=None, trajectory=None, encoding="utf-8"):
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        text = path.read_text(encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise FileReadError(str(path)) from exc
    if line_num is None:
        return text
    validate_lines(line_num)
    lines = text.splitlines(keepends=True)
    result = []
    for number in line_num:
        if number > len(lines):
            raise LineOutOfRangeError(f"Line {number} does not exist in {path}.")
        result.append(lines[number - 1])
    return "".join(result)


def add_contents(name, contents, trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        with path.open("a", encoding=encoding) as file:
            file.write(contents)
    except (OSError, UnicodeError) as exc:
        raise FileAppendError(str(path)) from exc
    return path


def remove_contents(name, line_num=None, trajectory=None, encoding="utf-8"):
    path = ensure_file(trajectory if trajectory is not None else name)
    if line_num is None:
        return edit_contents(name, "", trajectory, encoding)
    validate_lines(line_num)
    try:
        lines = path.read_text(encoding=encoding).splitlines(keepends=True)
        for number in sorted(set(line_num), reverse=True):
            if number > len(lines):
                raise LineOutOfRangeError(f"Line {number} does not exist in {path}.")
            del lines[number - 1]
        path.write_text("".join(lines), encoding=encoding)
    except LineOutOfRangeError:
        raise
    except (OSError, UnicodeError) as exc:
        raise FileWriteError(str(path)) from exc
    return path


def edit_contents(name, contents, trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    path = to_path(trajectory if trajectory is not None else name)
    if not path.exists():
        raise PyFilerFileNotFoundError(str(path))
    if not path.is_file():
        raise NotAFileError(str(path))
    try:
        path.write_text(contents, encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise FileWriteError(str(path)) from exc
    return path


def create_file(name, contents="", trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    path = to_path(trajectory if trajectory is not None else name)
    if path.exists():
        raise PyFilerFileExistsError(str(path))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise FileWriteError(str(path)) from exc
    return path


def delete_file(name, trajectory=None):
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        path.unlink()
    except OSError as exc:
        raise FileDeleteError(str(path)) from exc
    return True


def copy_file(source, destination, overwrite=False):
    src, dst = ensure_file(source), to_path(destination)
    if src.resolve() == dst.resolve():
        raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite:
        raise DestinationExistsError(str(dst))
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    except OSError as exc:
        raise FileCopyError(str(src)) from exc
    return dst


def move_file(source, destination, overwrite=False):
    src, dst = ensure_file(source), to_path(destination)
    if src.resolve() == dst.resolve():
        raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite:
        raise DestinationExistsError(str(dst))
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if overwrite and dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))
    except OSError as exc:
        raise FileMoveError(str(src)) from exc
    return dst


def rename_file(name, new_name):
    src = ensure_file(name)
    if not isinstance(new_name, str) or not new_name.strip() or new_name in {".", ".."}:
        raise InvalidPathError("new_name must be a non-empty filename")
    if Path(new_name).name != new_name:
        raise InvalidPathError("new_name must not contain directory separators")
    dst = src.with_name(new_name)
    if dst.exists():
        raise DestinationExistsError(str(dst))
    try:
        return src.rename(dst)
    except OSError as exc:
        raise FileRenameError(str(src)) from exc


def touch_file(name, trajectory=None):
    """Create an empty file or update its modification time."""
    path = to_path(trajectory if trajectory is not None else name)
    if path.exists() and not path.is_file():
        raise NotAFileError(str(path))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
    except OSError as exc:
        raise FileWriteError(str(path)) from exc
    return path


def file_exists(name, trajectory=None):
    """Return whether the resolved path exists and is a file."""
    path = to_path(trajectory if trajectory is not None else name)
    return path.is_file()


def read_file(name, line_num=None, trajectory=None, encoding="utf-8"):
    """Compatibility alias for get_contents."""
    return get_contents(name, line_num, trajectory, encoding)


def write_file(name, contents, trajectory=None, encoding="utf-8"):
    """Compatibility alias for edit_contents."""
    return edit_contents(name, contents, trajectory, encoding)


def append_file(name, contents, trajectory=None, encoding="utf-8"):
    """Compatibility alias for add_contents."""
    return add_contents(name, contents, trajectory, encoding)


def clear_file(name, trajectory=None, encoding="utf-8"):
    """Remove all text from an existing file."""
    return edit_contents(name, "", trajectory, encoding)
