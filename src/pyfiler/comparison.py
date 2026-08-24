"""File comparison helpers."""
import filecmp
from .utils import ensure_file
from .exceptions import ComparisonError


def files_equal(first, second, shallow=False):
    """Return whether two files have equal contents."""
    try:
        return filecmp.cmp(ensure_file(first), ensure_file(second), shallow=shallow)
    except OSError as exc:
        raise ComparisonError(str(exc)) from exc


# Backwards-compatible alias.
compare_files = files_equal
