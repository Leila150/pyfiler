"""File comparison helpers with concurrent-change detection."""
from __future__ import annotations

import filecmp
from .exceptions import ComparisonError, ConcurrentModificationError
from .utils import ensure_file


def _signature(path):
    st=path.stat()
    return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)


def _equal_contents(first,second,chunk_size=1024*1024):
    with first.open("rb") as left, second.open("rb") as right:
        while True:
            a=left.read(chunk_size); b=right.read(chunk_size)
            if a!=b: return False
            if not a: return True


def files_equal(first,second,shallow=False):
    """Compare files and detect changes made during the comparison."""
    if not isinstance(shallow,bool): raise TypeError("shallow must be a boolean")
    try:
        left,right=ensure_file(first),ensure_file(second)
        before_left,before_right=_signature(left),_signature(right)
        result=filecmp.cmp(left,right,shallow=True) if shallow else _equal_contents(left,right)
        after_left,after_right=_signature(left),_signature(right)
        if before_left!=after_left or before_right!=after_right:
            raise ConcurrentModificationError("A file changed while it was being compared.")
        return result
    except ConcurrentModificationError: raise
    except OSError as exc: raise ComparisonError(str(exc)) from exc


compare_files=files_equal
