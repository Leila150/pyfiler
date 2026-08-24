"""Directory tree and aggregate statistics."""
from __future__ import annotations

from collections import Counter

from .exceptions import TreeDepthError
from .utils import ensure_folder


def directory_tree(path, max_depth=None):
    """Return a readable tree representation of a directory."""
    if max_depth is not None and (
        not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 0
    ):
        raise TreeDepthError("max_depth must be a non-negative integer or None")

    root = ensure_folder(path)
    lines = [root.name or str(root)]

    def walk(folder, prefix, depth):
        if max_depth is not None and depth >= max_depth:
            return
        try:
            children = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            return
        for i, child in enumerate(children):
            last = i == len(children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.name)
            if child.is_dir():
                walk(child, prefix + ("    " if last else "│   "), depth + 1)

    walk(root, "", 0)
    return "\n".join(lines)


def directory_size(path):
    total = 0
    for item in ensure_folder(path).rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total


def count_files(path):
    return sum(1 for p in ensure_folder(path).rglob("*") if p.is_file())


def count_folders(path):
    return sum(1 for p in ensure_folder(path).rglob("*") if p.is_dir())


def extension_counts(path):
    return dict(Counter(
        p.suffix.lower() or "<no extension>"
        for p in ensure_folder(path).rglob("*")
        if p.is_file()
    ))


# Backwards-compatible aliases.
tree = directory_tree
folder_size = directory_size
extension_stats = extension_counts
