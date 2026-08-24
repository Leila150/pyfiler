"""Backward-compatible operation namespace.

The implementation is split across focused modules. This module intentionally
re-exports the canonical public operations and legacy compatibility aliases.
"""
from .files import *
from .folders import *
from .search import *
from .paths import *
from .metadata import *
from .hashing import *
from .comparison import *
from .tree import *
from .files import read_file, write_file, append_file, get_contents, add_contents, edit_contents

__all__ = [name for name in globals() if not name.startswith("_")]
