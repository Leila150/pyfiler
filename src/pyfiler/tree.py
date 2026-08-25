"""Directory tree and aggregate statistics."""
from __future__ import annotations

from collections import Counter

from .exceptions import TreeDepthError, TreeError
from .utils import ensure_folder


def _children(folder):
    try:
        return sorted(
            folder.iterdir(),
            key=lambda p: (p.is_symlink(), not p.is_dir(), p.name.casefold()),
        )
    except OSError as exc:
        raise TreeError(f"Unable to inspect directory: {folder}") from exc


def directory_tree(path, max_depth=None):
    """Return a deterministic readable tree representation of a directory.

    Symlink entries are shown but never traversed. This prevents a rooted
    Explorer from accidentally walking outside its configured filesystem tree.
    """
    if max_depth is not None and (
        not isinstance(max_depth, int)
        or isinstance(max_depth, bool)
        or max_depth < 0
    ):
        raise TreeDepthError("max_depth must be a non-negative integer or None")

    root = ensure_folder(path)
    lines = [root.name or str(root)]

    def walk(folder, prefix, depth):
        if max_depth is not None and depth >= max_depth:
            return
        children = _children(folder)
        for i, child in enumerate(children):
            last = i == len(children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.name)
            try:
                if child.is_symlink():
                    continue
                is_dir = child.is_dir()
            except OSError as exc:
                raise TreeError(f"Unable to inspect path: {child}") from exc
            if is_dir:
                walk(child, prefix + ("    " if last else "│   "), depth + 1)

    walk(root, "", 0)
    return "\n".join(lines)


def _iter_regular_files(root):
    try:
        for item in root.rglob("*"):
            if item.is_symlink():
                continue
            if item.is_file():
                yield item
    except OSError as exc:
        raise TreeError(f"Unable to inspect directory: {root}") from exc


def directory_size(path):
    root = ensure_folder(path)
    total = 0
    try:
        for item in _iter_regular_files(root):
            total += item.stat().st_size
    except OSError as exc:
        raise TreeError(f"Unable to calculate directory size: {root}") from exc
    return total


def count_files(path):
    root = ensure_folder(path)
    return sum(1 for _ in _iter_regular_files(root))


def count_folders(path):
    root = ensure_folder(path)
    try:
        return sum(
            1
            for p in root.rglob("*")
            if not p.is_symlink() and p.is_dir()
        )
    except OSError as exc:
        raise TreeError(f"Unable to count folders: {root}") from exc


def extension_counts(path):
    root = ensure_folder(path)
    try:
        return dict(
            Counter(
                p.suffix.lower() or "<no extension>"
                for p in _iter_regular_files(root)
            )
        )
    except OSError as exc:
        raise TreeError(f"Unable to calculate extension counts: {root}") from exc


tree = directory_tree
folder_size = directory_size
extension_stats = extension_counts
