"""Filesystem metadata helpers."""
from .utils import to_path
from .exceptions import PathNotFoundError


def exists(path): return to_path(path).exists()
def is_file(path): return to_path(path).is_file()
def is_folder(path): return to_path(path).is_dir()
def is_empty(path):
    p=to_path(path)
    return not any(p.iterdir()) if p.is_dir() else p.stat().st_size==0 if p.is_file() else False
def file_size(path): return to_path(path).stat().st_size
def file_extension(path): return to_path(path).suffix
def created_at(path): return to_path(path).stat().st_ctime
def modified_at(path): return to_path(path).stat().st_mtime
def accessed_at(path): return to_path(path).stat().st_atime

def metadata(path):
    p=to_path(path)
    if not p.exists(): raise PathNotFoundError(str(p))
    stat=p.stat()
    return {"name":p.name,"path":str(p.resolve()),"type":"file" if p.is_file() else "folder" if p.is_dir() else "other","size":stat.st_size,"extension":p.suffix if p.is_file() else "","created":stat.st_ctime,"modified":stat.st_mtime,"accessed":stat.st_atime}

def permissions(path): return to_path(path).stat().st_mode
