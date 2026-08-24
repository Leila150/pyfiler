"""Backward-compatible operation namespace.

The implementation is split into files.py and folders.py; this module keeps
older imports working without duplicating implementation logic.
"""
from .files import *
from .folders import *
from .paths import *
from .search import *
from .metadata import *
from .hashing import *
from .comparison import *
from .tree import *

__all__ = [name for name in globals() if not name.startswith("_")]
