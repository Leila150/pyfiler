"""Cross-platform storage setup abstraction."""
from __future__ import annotations
import os
import platform
import tempfile
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

    Native Android/iOS permission dialogs must be requested by the host app.
    This function verifies access by performing a harmless temporary write.
    """
    if not isinstance(request_permission, bool): raise TypeError("request_permission must be a boolean")
    if not isinstance(create, bool): raise TypeError("create must be a boolean")
    target = to_path(path) if path is not None else Path.home()
    try:
        if target.exists() and not target.is_dir(): raise StorageUnavailableError(str(target))
        if create: target.mkdir(parents=True, exist_ok=True)
        if not target.is_dir(): raise StorageUnavailableError(str(target))
        granted = False
        probe = None
        try:
            fd, probe = tempfile.mkstemp(prefix=".pyfiler-", suffix="-permission", dir=target)
            os.close(fd)
            Path(probe).unlink(missing_ok=True)
            granted = True
        except OSError:
            if probe:
                try: Path(probe).unlink(missing_ok=True)
                except OSError: pass
        if request_permission and not granted: raise StoragePermissionError(str(target))
        return StorageInfo(platform=platform.system().lower() or "unknown", path=str(target.resolve()), permission_granted=granted, available=True)
    except (StoragePermissionError, StorageUnavailableError): raise
    except OSError as exc: raise StorageSetupError(str(target)) from exc
