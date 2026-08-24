"""Cross-platform storage setup abstraction."""
import os, platform
from pathlib import Path
from dataclasses import dataclass
from .utils import to_path
from .exceptions import StoragePermissionError, StorageUnavailableError, StorageSetupError

@dataclass(frozen=True)
class StorageInfo:
    platform: str
    path: str
    permission_granted: bool
    available: bool


def setup_storage(path=None, request_permission=True, create=True):
    """Prepare accessible storage and report its status.

    Native Android/iOS permission dialogs must be supplied by the host runtime.
    """
    target=to_path(path) if path is not None else Path.home()
    try:
        if create: target.mkdir(parents=True,exist_ok=True)
        available=target.is_dir()
        if not available: raise StorageUnavailableError(str(target))
        granted=os.access(target,os.R_OK|os.W_OK)
        if request_permission and not granted: raise StoragePermissionError(str(target))
        return StorageInfo(platform=platform.system().lower(),path=str(target.resolve()),permission_granted=granted,available=available)
    except (StoragePermissionError,StorageUnavailableError): raise
    except OSError as exc: raise StorageSetupError(str(target)) from exc
