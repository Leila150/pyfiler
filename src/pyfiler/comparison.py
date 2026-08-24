"""File comparison helpers."""
import filecmp
from .utils import ensure_file
from .exceptions import ComparisonError


def compare_files(first, second, shallow=False):
    try: return filecmp.cmp(ensure_file(first), ensure_file(second), shallow=shallow)
    except OSError as exc: raise ComparisonError(str(exc)) from exc
