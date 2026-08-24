"""File comparison helpers."""

from __future__ import annotations

import filecmp

from .exceptions import ComparisonError
from .utils import ensure_file


def files_equal(first, second, shallow=False):
    """Return whether two files have equal contents.

    ``shallow=False`` is the safe default and compares file contents.
    """
    if not isinstance(shallow, bool):
        raise TypeError("shallow must be a boolean")
    try:
        return filecmp.cmp(
            ensure_file(first),
            ensure_file(second),
            shallow=shallow,
        )
    except OSError as exc:
        raise ComparisonError(str(exc)) from exc


# Backwards-compatible alias.
compare_files = files_equal
