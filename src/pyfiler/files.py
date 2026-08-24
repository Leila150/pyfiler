"""File creation, reading, editing, copying and deletion."""
from pathlib import Path
import os
import shutil
from .utils import to_path, ensure_file, validate_lines, validate_contents
from .exceptions import *


def read_contents(name, line_num=None, trajectory=None, encoding="utf-8"):
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


def append_contents(name, contents, trajectory=None, encoding="utf-8"):
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
        return replace_contents(name, "", trajectory, encoding)
    validate_lines(line_num)
    try:
        lines = path.read_text(encoding=encoding).splitlines(keepends=True)
        requested = sorted(set(line_num), reverse=True)
        for number in requested:
            if number > len(lines):
                raise LineOutOfRangeError(f"Line {number} does not exist in {path}.")
        for number in requested:
            del lines[number - 1]
        path.write_text("".join(lines), encoding=encoding)
    except LineOutOfRangeError:
        raise
    except (OSError, UnicodeError) as exc:
        raise FileWriteError(str(path)) from exc
    return path


def replace_contents(name, contents, trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    path = ensure_file(trajectory if trajectory is not None else name)
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
    if dst.exists() and not dst.is_file():
        raise NotAFileError(str(dst))
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
    if dst.exists() and not dst.is_file():
        raise NotAFileError(str(dst))

    backup = None
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if overwrite and dst.exists():
            backup = dst.with_name(dst.name + ".pyfiler-backup")
            counter = 1
            while backup.exists():
                backup = dst.with_name(f"{dst.name}.pyfiler-backup-{counter}")
                counter += 1
            dst.rename(backup)
        shutil.move(str(src), str(dst))
        if backup is not None:
            backup.unlink(missing_ok=True)
    except OSError as exc:
        if backup is not None and backup.exists() and not dst.exists():
            try:
                backup.rename(dst)
            except OSError:
                pass
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
    path = to_path(trajectory if trajectory is not None else name)
    return path.is_file()


get_contents = read_contents
add_contents = append_contents
edit_contents = replace_contents
read_file = read_contents
write_file = replace_contents
append_file = append_contents


def clear_file(name, trajectory=None, encoding="utf-8"):
    return replace_contents(name, "", trajectory, encoding)
