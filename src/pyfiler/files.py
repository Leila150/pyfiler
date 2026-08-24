"""File creation, reading, editing, copying and deletion."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .utils import to_path, ensure_file, validate_lines, validate_contents
from .exceptions import *


def _validate_encoding(encoding):
    if not isinstance(encoding, str) or not encoding.strip():
        raise InvalidEncodingError("encoding must be a non-empty string")
    return encoding


def _atomic_write_text(path, contents, encoding):
    """Write text through a same-directory temporary file, then replace atomically."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding=encoding, dir=path.parent, prefix=f".{path.name}.",
            suffix=".pyfiler-tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def read_contents(name, line_num=None, trajectory=None, encoding="utf-8"):
    encoding = _validate_encoding(encoding)
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        text = path.read_text(encoding=encoding)
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
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
    encoding = _validate_encoding(encoding)
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        with path.open("a", encoding=encoding) as file:
            file.write(contents)
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
        raise FileAppendError(str(path)) from exc
    return path


def remove_contents(name, line_num=None, trajectory=None, encoding="utf-8"):
    encoding = _validate_encoding(encoding)
    path = ensure_file(trajectory if trajectory is not None else name)
    if line_num is None:
        return replace_contents(name, "", trajectory, encoding)
    validate_lines(line_num)
    try:
        lines = path.read_text(encoding=encoding).splitlines(keepends=True)
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
        raise FileReadError(str(path)) from exc
    requested = sorted(set(line_num), reverse=True)
    for number in requested:
        if number > len(lines):
            raise LineOutOfRangeError(f"Line {number} does not exist in {path}.")
    for number in requested:
        del lines[number - 1]
    try:
        _atomic_write_text(path, "".join(lines), encoding)
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
        raise FileWriteError(str(path)) from exc
    return path


def replace_contents(name, contents, trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    encoding = _validate_encoding(encoding)
    path = ensure_file(trajectory if trajectory is not None else name)
    try:
        _atomic_write_text(path, contents, encoding)
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
        raise FileWriteError(str(path)) from exc
    return path


def create_file(name, contents="", trajectory=None, encoding="utf-8"):
    validate_contents(contents)
    encoding = _validate_encoding(encoding)
    path = to_path(trajectory if trajectory is not None else name)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding=encoding) as handle:
            handle.write(contents)
    except FileExistsError as exc:
        raise PyFilerFileExistsError(str(path)) from exc
    except UnicodeError as exc:
        raise InvalidEncodingError(str(exc)) from exc
    except OSError as exc:
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
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a boolean")
    src, dst = ensure_file(source), to_path(destination)
    if src.resolve() == dst.resolve():
        raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite:
        raise DestinationExistsError(str(dst))
    if dst.exists() and not dst.is_file():
        raise NotAFileError(str(dst))
    temporary = None
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=dst.parent, prefix=f".{dst.name}.", suffix=".pyfiler-tmp", delete=False) as handle:
            temporary = Path(handle.name)
        shutil.copy2(src, temporary)
        if not overwrite and dst.exists():
            raise DestinationExistsError(str(dst))
        os.replace(temporary, dst)
        temporary = None
    except DestinationExistsError:
        raise
    except OSError as exc:
        raise FileCopyError(str(src)) from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
    return dst


def move_file(source, destination, overwrite=False):
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a boolean")
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
            backup = Path(tempfile.mkstemp(prefix=f".{dst.name}.", suffix=".pyfiler-backup", dir=dst.parent)[1])
            backup.unlink()
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


def clear_file(name, trajectory=None, encoding="utf-8"):
    return replace_contents(name, "", trajectory, encoding)


get_contents = read_contents
add_contents = append_contents
edit_contents = replace_contents
read_file = read_contents
write_file = replace_contents
append_file = append_contents
