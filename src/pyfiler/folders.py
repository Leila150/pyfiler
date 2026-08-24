"""Folder creation, inspection and organization."""
import shutil
from .utils import to_path, ensure_folder
from .exceptions import *


def create_folder(name, contents=None, trajectory=None):
    path = to_path(trajectory if trajectory is not None else name)
    if path.exists():
        raise FolderExistsError(str(path))
    try:
        path.mkdir(parents=True)
        if contents is not None:
            children = [contents] if not isinstance(contents, (list, tuple)) else contents
            for child in children:
                source = to_path(child)
                if not source.exists():
                    raise PathNotFoundError(str(source))
                destination = path / source.name
                if destination.exists():
                    raise DestinationExistsError(str(destination))
                if source.is_file():
                    shutil.copy2(source, destination)
                elif source.is_dir():
                    shutil.copytree(source, destination)
    except PyFilerError:
        raise
    except OSError as exc:
        raise FolderCreateError(str(path)) from exc
    return path


def add_parent(child, parent):
    """Move a file or folder created elsewhere into a parent folder."""
    source = to_path(child)
    destination_folder = ensure_folder(parent)
    if not source.exists():
        raise PathNotFoundError(str(source))
    destination = destination_folder / source.name
    if source.resolve() == destination.resolve():
        raise SourceEqualsDestinationError(str(source))
    if destination.exists():
        raise DestinationExistsError(str(destination))
    try:
        return to_path(shutil.move(str(source), str(destination)))
    except OSError as exc:
        raise OperationError(str(source)) from exc


def folder_contents(trajectory):
    return list(ensure_folder(trajectory).iterdir())


def folder_remove_contents(trajectory, child):
    folder = ensure_folder(trajectory)
    if not isinstance(child, list) or not all(isinstance(x, str) for x in child):
        raise ContentTypeError("child must be a list of strings.")
    removed = []
    for name in child:
        target = folder / name
        if not target.exists():
            raise PathNotFoundError(str(target))
        try:
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()
        except OSError as exc:
            raise FolderDeleteError(str(target)) from exc
        removed.append(target)
    return removed


def delete_folder(path, recursive=False):
    folder = ensure_folder(path)
    try:
        if any(folder.iterdir()) and not recursive:
            raise FolderNotEmptyError(str(folder))
        if recursive: shutil.rmtree(folder)
        else: folder.rmdir()
    except FolderNotEmptyError:
        raise
    except OSError as exc:
        raise FolderDeleteError(str(folder)) from exc
    return True


def list_dir(path): return folder_contents(path)
def list_files(path): return [p for p in folder_contents(path) if p.is_file()]
def list_folders(path): return [p for p in folder_contents(path) if p.is_dir()]
def clear_folder(path): return folder_remove_contents(path, [p.name for p in folder_contents(path)])


def copy_folder(source, destination, overwrite=False):
    src, dst = ensure_folder(source), to_path(destination)
    if src.resolve() == dst.resolve(): raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite: raise DestinationExistsError(str(dst))
    try: shutil.copytree(src, dst, dirs_exist_ok=overwrite)
    except OSError as exc: raise FolderCopyError(str(src)) from exc
    return dst


def move_folder(source, destination, overwrite=False):
    src, dst = ensure_folder(source), to_path(destination)
    if src.resolve() == dst.resolve(): raise SourceEqualsDestinationError(str(src))
    if dst.exists() and not overwrite: raise DestinationExistsError(str(dst))
    try:
        if overwrite and dst.exists(): shutil.rmtree(dst)
        shutil.move(str(src), str(dst))
    except OSError as exc: raise FolderMoveError(str(src)) from exc
    return dst


def rename_folder(path, new_name):
    src = ensure_folder(path); dst = src.with_name(new_name)
    if dst.exists(): raise DestinationExistsError(str(dst))
    try: return src.rename(dst)
    except OSError as exc: raise FolderRenameError(str(src)) from exc
