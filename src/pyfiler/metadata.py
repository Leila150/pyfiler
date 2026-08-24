"""Filesystem metadata helpers."""
from __future__ import annotations
import stat
from .exceptions import PathNotFoundError, MetadataUnavailableError
from .utils import to_path

def _stat(path):
    p=to_path(path)
    try: return p,p.stat()
    except FileNotFoundError as exc: raise PathNotFoundError(str(p)) from exc
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc

def _existing(path): return _stat(path)[0]
def exists(path):
    p=to_path(path)
    try: return p.exists()
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
def is_file(path):
    p=to_path(path)
    try: return p.is_file()
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
def is_folder(path):
    p=to_path(path)
    try: return p.is_dir()
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
def is_empty(path):
    p,st=_stat(path)
    try:
        if stat.S_ISDIR(st.st_mode): return next(iter(p.iterdir()),None) is None
        if stat.S_ISREG(st.st_mode): return st.st_size==0
        return False
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
def size_of(path): return _stat(path)[1].st_size
def extension_of(path):
    p,st=_stat(path); return p.suffix if stat.S_ISREG(st.st_mode) else ""
def created_at(path): return _stat(path)[1].st_ctime
def modified_at(path): return _stat(path)[1].st_mtime
def accessed_at(path): return _stat(path)[1].st_atime
def metadata(path):
    p,st=_stat(path); mode=st.st_mode; isfile=stat.S_ISREG(mode); isfolder=stat.S_ISDIR(mode)
    try: empty=(next(iter(p.iterdir()),None) is None) if isfolder else (st.st_size==0 if isfile else False)
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
    return {"name":p.name,"path":str(p.resolve(strict=False)),"type":"file" if isfile else "folder" if isfolder else "other","size":st.st_size,"extension":p.suffix if isfile else "","created":st.st_ctime,"modified":st.st_mtime,"accessed":st.st_atime,"mode":stat.S_IMODE(mode),"is_file":isfile,"is_folder":isfolder,"is_empty":empty,"is_symlink":p.is_symlink()}
def permissions(path): return stat.S_IMODE(_stat(path)[1].st_mode)
def name_of(path): return _stat(path)[0].name
def stem_of(path): return _stat(path)[0].stem
def path_kind(path):
    p=to_path(path)
    try: st=p.stat()
    except FileNotFoundError: return "missing"
    except OSError as exc: raise MetadataUnavailableError(str(p)) from exc
    mode=st.st_mode
    return "file" if stat.S_ISREG(mode) else "folder" if stat.S_ISDIR(mode) else "other"
def same_type(first,second):
    a,b=path_kind(first),path_kind(second); return a==b and a in {"file","folder"}
def is_symlink(path):
    try: return to_path(path).is_symlink()
    except OSError as exc: raise MetadataUnavailableError(str(path)) from exc
def device_id(path): return _stat(path)[1].st_dev
def inode(path): return _stat(path)[1].st_ino
def mode(path): return stat.S_IMODE(_stat(path)[1].st_mode)
def nlink(path): return _stat(path)[1].st_nlink
def same_filesystem(first,second): return device_id(first)==device_id(second)
file_size=size_of; file_extension=extension_of; file_name=name_of; file_stem=stem_of
