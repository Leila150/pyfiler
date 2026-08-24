"""Folder creation, inspection and organization."""
import shutil
from pathlib import Path
from .utils import to_path, ensure_folder
from .exceptions import *


def create_folder(name, contents=None, trajectory=None):
    path = to_path(trajectory if trajectory is not None else name)
    if path.exists(): raise FolderExistsError(str(path))
    if contents is None: children = []
    elif isinstance(contents, (list, tuple)): children = list(contents)
    elif isinstance(contents, (str, Path)): children = [contents]
    else: raise ContentTypeError("contents must be a path or a list/tuple of paths.")
    sources = []
    for child in children:
        source = to_path(child)
        if not source.exists(): raise PathNotFoundError(str(source))
        if source.resolve() == path.resolve(): raise SourceEqualsDestinationError(str(source))
        if source.is_dir() and path.resolve().is_relative_to(source.resolve()): raise RecursiveOperationError(f"Cannot copy {source} into its own descendant {path}.")
        sources.append(source)
    try:
        path.mkdir(parents=True)
        for source in sources:
            destination = path / source.name
            if destination.exists(): raise DestinationExistsError(str(destination))
            if source.is_file(): shutil.copy2(source, destination)
            else: shutil.copytree(source, destination)
    except PyFilerError:
        try: shutil.rmtree(path)
        except OSError: pass
        raise
    except OSError as exc:
        try: shutil.rmtree(path)
        except OSError: pass
        raise FolderCreateError(str(path)) from exc
    return path


def move_into(child, parent):
    source = to_path(child).resolve(); destination_folder = ensure_folder(parent).resolve()
    if not source.exists(): raise PathNotFoundError(str(source))
    destination = destination_folder / source.name
    if source == destination: raise SourceEqualsDestinationError(str(source))
    if destination.exists(): raise DestinationExistsError(str(destination))
    if source.is_dir() and destination_folder.is_relative_to(source): raise RecursiveOperationError(f"Cannot move {source} into its own descendant {destination_folder}.")
    try: return to_path(shutil.move(str(source), str(destination)))
    except OSError as exc: raise OperationError(str(source)) from exc


def list_folder(path): return list(ensure_folder(path).iterdir())


def _validate_children(folder, children):
    if not isinstance(children, list) or not all(isinstance(x, str) for x in children): raise ContentTypeError("children must be a list of strings.")
    targets, seen = [], set()
    for name in children:
        if not name.strip() or name in {".", ".."}: raise InvalidPathError("child names must be non-empty direct child names")
        candidate = Path(name)
        if candidate.is_absolute() or candidate.name != name: raise InvalidPathError(f"children must contain direct child names: {name!r}")
        if name in seen: continue
        seen.add(name)
        target = folder / name
        if not target.exists(): raise PathNotFoundError(str(target))
        targets.append(target)
    return targets


def remove_from_folder(path, children):
    folder = ensure_folder(path).resolve(); targets = _validate_children(folder, children); removed = []
    for target in targets:
        try:
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()
        except OSError as exc: raise FolderDeleteError(str(target)) from exc
        removed.append(target)
    return removed


def delete_folder(path, recursive=False):
    folder = ensure_folder(path)
    try:
        if any(folder.iterdir()) and not recursive: raise FolderNotEmptyError(str(folder))
        if recursive: shutil.rmtree(folder)
        else: folder.rmdir()
    except FolderNotEmptyError: raise
    except OSError as exc: raise FolderDeleteError(str(folder)) from exc
    return True


def list_files(path): return [p for p in list_folder(path) if p.is_file()]
def list_folders(path): return [p for p in list_folder(path) if p.is_dir()]

def clear_folder(path):
    folder = ensure_folder(path).resolve(); children = [p.name for p in folder.iterdir()]
    return remove_from_folder(folder, children) if children else []


def copy_folder(source, destination, overwrite=False):
    src, dst = ensure_folder(source), to_path(destination); sr, dr = src.resolve(), dst.resolve()
    if sr == dr: raise SourceEqualsDestinationError(str(src))
    if dr.is_relative_to(sr): raise RecursiveOperationError(f"Cannot copy {src} into its own descendant {dst}.")
    if dst.exists() and not overwrite: raise DestinationExistsError(str(dst))
    try:
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(src, dst, dirs_exist_ok=overwrite)
    except OSError as exc: raise FolderCopyError(str(src)) from exc
    return dst


def move_folder(source, destination, overwrite=False):
    src, dst = ensure_folder(source), to_path(destination); sr, dr = src.resolve(), dst.resolve()
    if sr == dr: raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite: raise DestinationExistsError(str(dst))
    if dr.is_relative_to(sr): raise RecursiveOperationError(f"Cannot move {src} into its own descendant {dst}.")
    backup = None
    try:
        if overwrite and dst.exists():
            backup = dst.with_name(dst.name + ".pyfiler-backup"); counter = 1
            while backup.exists(): backup = dst.with_name(f"{dst.name}.pyfiler-backup-{counter}"); counter += 1
            dst.rename(backup)
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(dst))
        if backup is not None: shutil.rmtree(backup)
    except OSError as exc:
        if backup is not None and backup.exists() and not dst.exists():
            try: backup.rename(dst)
            except OSError: pass
        raise FolderMoveError(str(src)) from exc
    return dst


def rename_folder(path, new_name):
    src = ensure_folder(path)
    if not isinstance(new_name, str) or not new_name.strip() or new_name in {".", ".."}: raise InvalidPathError("new_name must be a non-empty folder name")
    if Path(new_name).name != new_name: raise InvalidPathError("new_name must not contain directory separators")
    dst = src.with_name(new_name)
    if dst.exists(): raise DestinationExistsError(str(dst))
    try: return src.rename(dst)
    except OSError as exc: raise FolderRenameError(str(src)) from exc

add_parent = move_into
folder_contents = list_folder
folder_remove_contents = remove_from_folder
list_dir = list_folder
