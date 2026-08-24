"""Cross-platform storage setup abstraction.

pyfiler cannot itself display native Android/iOS permission dialogs. The host
application must request platform permissions; this function verifies the
resulting filesystem access.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path

from .exceptions import StoragePermissionError, StorageUnavailableError, StorageSetupError
from .utils import to_path


@dataclass(frozen=True)
class StorageInfo:
    platform: str
    path: str
    permission_granted: bool
    available: bool


def setup_storage(path=None, request_permission=True, create=True):
    """Prepare accessible storage and report its status.

    ``request_permission`` controls whether inaccessible storage raises an
    error. It does not and cannot open native permission dialogs by itself.
    """
    if not isinstance(request_permission, bool):
        raise TypeError("request_permission must be a boolean")
    if not isinstance(create, bool):
        raise TypeError("create must be a boolean")

    target = to_path(path) if path is not None else Path.home()
    try:
        if target.exists() and not target.is_dir():
            raise StorageUnavailableError(str(target))
        if create:
            target.mkdir(parents=True, exist_ok=True)
        available = target.is_dir()
        if not available:
            raise StorageUnavailableError(str(target))
        granted = os.access(target, os.R_OK | os.W_OK)
        if request_permission and not granted:
            raise StoragePermissionError(str(target))
        return StorageInfo(
            platform=platform.system().lower() or "unknown",
            path=str(target.resolve()),
            permission_granted=granted,
            available=available,
        )
    except (StoragePermissionError, StorageUnavailableError):
        raise
    except OSError as exc:
        raise StorageSetupError(str(target)) from exc
