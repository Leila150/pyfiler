"""Directory tree and aggregate statistics."""
from __future__ import annotations

from collections import Counter

from .exceptions import TreeDepthError, TreeError
from .utils import ensure_folder


def _children(folder):
    try:
        return sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))
    except OSError as exc:
        raise TreeError(f"Unable to inspect directory: {folder}") from exc


def directory_tree(path, max_depth=None):
    """Return a deterministic readable tree representation of a directory."""
    if max_depth is not None and (not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 0):
        raise TreeDepthError("max_depth must be a non-negative integer or None")
    root = ensure_folder(path)
    lines = [root.name or str(root)]

    def walk(folder, prefix, depth):
        if max_depth is not None and depth >= max_depth:
            return
        for i, child in enumerate(_children(folder)):
            last = i == len(_children(folder)) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.name)
            try:
                is_dir = child.is_dir()
            except OSError as exc:
                raise TreeError(f"Unable to inspect path: {child}") from exc
            if is_dir:
                walk(child, prefix + ("    " if last else "│   "), depth + 1)

    walk(root, "", 0)
    return "\n".join(lines)


def directory_size(path):
    root = ensure_folder(path)
    total = 0
    try:
        for item in root.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    except OSError as exc:
        raise TreeError(f"Unable to calculate directory size: {root}") from exc
    return total


def count_files(path):
    root = ensure_folder(path)
    try:
        return sum(1 for p in root.rglob("*") if p.is_file())
    except OSError as exc:
        raise TreeError(f"Unable to count files: {root}") from exc


def count_folders(path):
    root = ensure_folder(path)
    try:
        return sum(1 for p in root.rglob("*") if p.is_dir())
    except OSError as exc:
        raise TreeError(f"Unable to count folders: {root}") from exc


def extension_counts(path):
    root = ensure_folder(path)
    try:
        return dict(Counter(p.suffix.lower() or "<no extension>" for p in root.rglob("*") if p.is_file()))
    except OSError as exc:
        raise TreeError(f"Unable to calculate extension counts: {root}") from exc


tree = directory_tree
folder_size = directory_size
extension_stats = extension_counts
