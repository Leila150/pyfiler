"""Storage capability and filesystem information."""
from __future__ import annotations

import os
import platform
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass

from .exceptions import StorageUnavailableError
from .utils import to_path


@dataclass(frozen=True)
class StorageStatus:
    path: str
    available: bool
    readable: bool
    writable: bool
    executable: bool
    total_bytes: int
    free_bytes: int
    used_bytes: int
    filesystem: str
    platform: str

    @property
    def permission_granted(self):
        """Whether the target is accessible through at least one storage permission."""
        return self.available


def _target(path=None):
    target=to_path(path) if path is not None else Path.cwd()
    try: return target.resolve()
    except OSError as exc: raise StorageUnavailableError(str(target)) from exc


def exists(path=None):
    try: return _target(path).exists()
    except StorageUnavailableError: return False


def readable(path=None):
    target=_target(path)
    try: return target.is_dir() and os.access(target, os.R_OK)
    except OSError: return False


def writable(path=None):
    target=_target(path)
    try: return target.is_dir() and os.access(target, os.W_OK)
    except OSError: return False


def executable(path=None):
    target=_target(path)
    try: return target.is_dir() and os.access(target, os.X_OK)
    except OSError: return False


def write_test(path=None):
    """Perform an actual durable temporary write without leaving a probe behind."""
    target=_target(path)
    if not target.is_dir(): return False
    probe=None
    try:
        fd,probe=tempfile.mkstemp(prefix=".pyfiler-storage-test-",dir=target)
        with os.fdopen(fd,"wb") as handle:
            handle.write(b"pyfiler")
            handle.flush()
            os.fsync(handle.fileno())
        Path(probe).unlink(missing_ok=True)
        return True
    except OSError:
        if probe:
            try: Path(probe).unlink(missing_ok=True)
            except OSError: pass
        return False


def storage(path=None):
    """Return whether the target directory is accessible as storage.

    Read-only storage counts as available. Use ``writable()`` or
    ``write_test()`` when write capability is specifically required.
    """
    return readable(path) or writable(path) or executable(path)


def available(path=None): return storage(path)
def permission(path=None): return storage(path)
def permission_granted(path=None): return permission(path)
def can_write(path=None): return writable(path)
def can_read(path=None): return readable(path)
def can_execute(path=None): return executable(path)


def _linux_filesystem(target):
    try:
        best=None
        with open("/proc/mounts","r",encoding="utf-8") as mounts:
            for line in mounts:
                parts=line.split()
                if len(parts)<3: continue
                mount=parts[1].replace("\\040"," ").replace("\\011","\t").replace("\\134","\\")
                mount_path=Path(mount)
                if target==mount_path or mount_path in target.parents:
                    if best is None or len(mount_path.parts)>len(best[0].parts): best=(mount_path,parts[2])
        return best[1] if best else "unknown"
    except (OSError,ValueError): return "unknown"


def filesystem(path=None):
    target=_target(path)
    if platform.system().lower()=="linux": return _linux_filesystem(target)
    return "unknown"


def check(path=None):
    target=_target(path)
    try:
        if not target.is_dir():
            return StorageStatus(str(target),False,False,False,False,0,0,0,"unknown",platform_name())
        total,used,free=shutil.disk_usage(target)
        return StorageStatus(str(target),storage(target),readable(target),writable(target),executable(target),total,free,used,filesystem(target),platform_name())
    except OSError as exc: raise StorageUnavailableError(str(target)) from exc


def info(path=None): return check(path)
def status(path=None): return check(path)
def total_space(path=None): return shutil.disk_usage(_target(path)).total
def free_space(path=None): return shutil.disk_usage(_target(path)).free
def used_space(path=None): return shutil.disk_usage(_target(path)).used

def disk_usage(path=None):
    usage=shutil.disk_usage(_target(path))
    return {"total":usage.total,"used":usage.used,"free":usage.free}

def platform_name(): return platform.system().lower() or "unknown"
def operating_system(): return platform_name()
def home_directory(): return str(Path.home())
def current_directory(): return str(Path.cwd())
def temporary_directory(): return tempfile.gettempdir()
def default_storage(): return current_directory()
def path(path=None): return str(_target(path))

__all__=["StorageStatus","storage","available","exists","readable","writable","executable","permission","permission_granted","can_write","can_read","can_execute","write_test","check","info","status","total_space","free_space","used_space","disk_usage","platform_name","operating_system","home_directory","current_directory","temporary_directory","default_storage","path","filesystem"]
