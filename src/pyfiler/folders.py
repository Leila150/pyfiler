"""Folder creation, inspection and organization."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .utils import to_path, ensure_folder
from .exceptions import *


def _validate_overwrite(overwrite):
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a boolean")


def _direct_child_name(name):
    if not isinstance(name, str) or not name.strip() or name in {".", ".."}:
        raise InvalidPathError("name must be a non-empty direct child name")
    if Path(name).name != name or Path(name).is_absolute():
        raise InvalidPathError("name must not contain directory separators")


def _temporary_destination(parent, prefix):
    handle = tempfile.NamedTemporaryFile(
        dir=parent,
        prefix=prefix,
        suffix=".pyfiler-stage",
        delete=False,
    )
    candidate = Path(handle.name)
    handle.close()
    candidate.unlink(missing_ok=True)
    return candidate


def _copy_tree_staged(source, parent, name):
    stage = _temporary_destination(parent, f".{name}.")
    try:
        shutil.copytree(source, stage, symlinks=True)
        return stage
    except Exception:
        try:
            shutil.rmtree(stage)
        except OSError:
            pass
        raise


def _restore_backup(backup, destination):
    if backup is None or not backup.exists() or destination.exists():
        return False
    try:
        os.replace(backup, destination)
        return True
    except OSError:
        return False


def create_folder(name, contents=None, trajectory=None):
    path = to_path(trajectory if trajectory is not None else name)
    if path.exists():
        raise FolderExistsError(str(path))
    if contents is None:
        children = []
    elif isinstance(contents, (list, tuple)):
        children = list(contents)
    elif isinstance(contents, (str, Path)):
        children = [contents]
    else:
        raise ContentTypeError("contents must be a path or a list/tuple of paths.")

    sources = []
    target = path.resolve()
    for child in children:
        source = to_path(child)
        source_resolved = source.resolve()
        if not source.exists():
            raise PathNotFoundError(str(source))
        if source_resolved == target:
            raise SourceEqualsDestinationError(str(source))
        if source.is_dir() and target.is_relative_to(source_resolved):
            raise RecursiveOperationError(
                f"Cannot copy {source} into its own descendant {path}."
            )
        sources.append(source)

    stage = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        stage = _temporary_destination(path.parent, f".{path.name}.")
        stage.mkdir()
        for source in sources:
            destination = stage / source.name
            if destination.exists():
                raise DestinationExistsError(str(destination))
            if source.is_file():
                shutil.copy2(source, destination, follow_symlinks=False)
            elif source.is_dir():
                shutil.copytree(source, destination, symlinks=True)
            else:
                raise InvalidOperationError(f"Unsupported source type: {source}")
        if path.exists():
            raise FolderExistsError(str(path))
        stage.rename(path)
        stage = None
    except PyFilerError:
        raise
    except OSError as exc:
        raise FolderCreateError(str(path)) from exc
    finally:
        if stage is not None:
            try:
                shutil.rmtree(stage)
            except OSError:
                pass
    return path


def move_into(child, parent):
    source = to_path(child)
    destination_folder = ensure_folder(parent)
    if not source.exists():
        raise PathNotFoundError(str(source))
    destination = destination_folder / source.name
    source_resolved = source.resolve()
    parent_resolved = destination_folder.resolve()
    if source_resolved == destination.resolve():
        raise SourceEqualsDestinationError(str(source))
    if destination.exists():
        raise DestinationExistsError(str(destination))
    if source.is_dir() and parent_resolved.is_relative_to(source_resolved):
        raise RecursiveOperationError(
            f"Cannot move {source} into its own descendant {destination_folder}."
        )
    try:
        return to_path(shutil.move(str(source), str(destination)))
    except OSError as exc:
        raise OperationError(str(source)) from exc


def list_folder(path):
    return sorted(
        ensure_folder(path).iterdir(),
        key=lambda p: (p.name.casefold(), p.name),
    )


def _validate_children(folder, children):
    if not isinstance(children, list) or not all(isinstance(x, str) for x in children):
        raise ContentTypeError("children must be a list of strings.")
    targets = []
    seen = set()
    for name in children:
        _direct_child_name(name)
        if name in seen:
            continue
        seen.add(name)
        target = folder / name
        if not target.exists():
            raise PathNotFoundError(str(target))
        targets.append(target)
    return targets


def remove_from_folder(path, children):
    folder = ensure_folder(path).resolve()
    targets = _validate_children(folder, children)
    removed = []
    for target in targets:
        try:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        except OSError as exc:
            raise FolderDeleteError(str(target)) from exc
        removed.append(target)
    return removed


def delete_folder(path, recursive=False):
    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean")
    folder = ensure_folder(path)
    try:
        if any(folder.iterdir()) and not recursive:
            raise FolderNotEmptyError(str(folder))
        if recursive:
            shutil.rmtree(folder)
        else:
            folder.rmdir()
    except FolderNotEmptyError:
        raise
    except OSError as exc:
        raise FolderDeleteError(str(folder)) from exc
    return True


def list_files(path):
    return [p for p in list_folder(path) if p.is_file()]


def list_folders(path):
    return [p for p in list_folder(path) if p.is_dir()]


def clear_folder(path):
    folder = ensure_folder(path).resolve()
    children = [p.name for p in folder.iterdir()]
    return remove_from_folder(folder, children) if children else []


def copy_folder(source, destination, overwrite=False):
    _validate_overwrite(overwrite)
    src, dst = ensure_folder(source), to_path(destination)
    sr, dr = src.resolve(), dst.resolve()
    if sr == dr:
        raise SourceEqualsDestinationError(str(src))
    if dr.is_relative_to(sr):
        raise RecursiveOperationError(
            f"Cannot copy {src} into its own descendant {dst}."
        )
    if dst.exists() and not overwrite:
        raise DestinationExistsError(str(dst))
    if dst.exists() and not dst.is_dir():
        raise NotAFolderError(str(dst))

    stage = backup = None
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        stage = _copy_tree_staged(src, dst.parent, dst.name)
        if dst.exists():
            if not overwrite:
                raise DestinationExistsError(str(dst))
            backup = _temporary_destination(dst.parent, f".{dst.name}.")
            os.replace(dst, backup)
        try:
            os.replace(stage, dst)
            stage = None
        except OSError:
            _restore_backup(backup, dst)
            raise
        if backup is not None:
            try:
                shutil.rmtree(backup)
            except OSError:
                # Successful copy; retain the backup rather than falsely
                # reporting failure and encouraging an unsafe retry.
                pass
            backup = None
    except DestinationExistsError:
        raise
    except OSError as exc:
        raise FolderCopyError(str(src)) from exc
    finally:
        if stage is not None:
            try:
                shutil.rmtree(stage)
            except OSError:
                pass
        if backup is not None and backup.exists() and not dst.exists():
            _restore_backup(backup, dst)
    return dst


def move_folder(source, destination, overwrite=False):
    """Move a folder with staged cross-device and overwrite recovery."""
    _validate_overwrite(overwrite)
    src, dst = ensure_folder(source), to_path(destination)
    sr, dr = src.resolve(), dst.resolve()
    if sr == dr:
        raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite:
        raise DestinationExistsError(str(dst))
    if dst.exists() and not dst.is_dir():
        raise NotAFolderError(str(dst))
    if dr.is_relative_to(sr):
        raise RecursiveOperationError(
            f"Cannot move {src} into its own descendant {dst}."
        )

    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        same_device = src.stat().st_dev == dst.parent.stat().st_dev
    except OSError:
        same_device = False

    stage = backup = None
    try:
        if same_device:
            if overwrite and dst.exists():
                backup = _temporary_destination(dst.parent, f".{dst.name}.")
                os.replace(dst, backup)
            try:
                os.replace(src, dst)
            except OSError:
                _restore_backup(backup, dst)
                raise
        else:
            stage = _copy_tree_staged(src, dst.parent, dst.name)
            if dst.exists():
                if not overwrite:
                    raise DestinationExistsError(str(dst))
                backup = _temporary_destination(dst.parent, f".{dst.name}.")
                os.replace(dst, backup)
            try:
                os.replace(stage, dst)
                stage = None
                shutil.rmtree(src)
            except OSError:
                if not dst.exists():
                    _restore_backup(backup, dst)
                raise

        if backup is not None:
            try:
                shutil.rmtree(backup)
            except OSError:
                pass
            backup = None
        return dst
    except DestinationExistsError:
        raise
    except OSError as exc:
        raise FolderMoveError(str(src)) from exc
    finally:
        if stage is not None:
            try:
                shutil.rmtree(stage)
            except OSError:
                pass
        if backup is not None and backup.exists() and not dst.exists():
            _restore_backup(backup, dst)


def rename_folder(path, new_name):
    src = ensure_folder(path)
    _direct_child_name(new_name)
    dst = src.with_name(new_name)
    if dst.exists():
        raise DestinationExistsError(str(dst))
    try:
        return src.rename(dst)
    except OSError as exc:
        raise FolderRenameError(str(src)) from exc


add_parent = move_into
folder_contents = list_folder
folder_remove_contents = remove_from_folder
list_dir = list_folder
