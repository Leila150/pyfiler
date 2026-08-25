"""Recursive file, folder, and content search."""
from __future__ import annotations
import re
from .exceptions import InvalidExtensionError,InvalidPatternError,SearchError
from .utils import ensure_folder
DEFAULT_MAX_SEARCH_FILE_SIZE=512*1024*1024
DEFAULT_MAX_REGEX_LINE_LENGTH=8*1024*1024

def _validate_name(name):
    if not isinstance(name,str) or not name.strip(): raise ValueError("name must be a non-empty string")
    if "\x00" in name: raise ValueError("name cannot contain a NUL character")
    return name

def _sorted_paths(paths): return sorted(paths,key=lambda p:(str(p).casefold(),str(p)))
def _walk(path,pattern="*"):
    root=ensure_folder(path)
    try: results=list(root.rglob(pattern))
    except (OSError,ValueError) as exc: raise SearchError(f"Unable to search {root}: {exc}") from exc
    return iter(_sorted_paths(p for p in results if not p.is_symlink()))

def find_paths(path,name="*"):
    name=_validate_name(name)
    if any(char in name for char in "*?[]"): return list(_walk(path,name))
    needle=name.casefold(); return _sorted_paths(item for item in _walk(path) if needle in item.name.casefold())

def find_files(path,name="*"):
    results=[]
    for p in _walk(path,_validate_name(name)):
        try:
            if p.is_file(): results.append(p)
        except OSError as exc: raise SearchError(f"Unable to inspect {p}: {exc}") from exc
    return _sorted_paths(results)

def find_folders(path,name="*"):
    results=[]
    for p in _walk(path,_validate_name(name)):
        try:
            if p.is_dir(): results.append(p)
        except OSError as exc: raise SearchError(f"Unable to inspect {p}: {exc}") from exc
    return _sorted_paths(results)

def _validate_encoding(encoding):
    if not isinstance(encoding,str) or not encoding.strip(): raise ValueError("encoding must be a non-empty string")
    return encoding

def _validate_limit(value,name):
    if not isinstance(value,int) or isinstance(value,bool) or value<=0: raise ValueError(f"{name} must be a positive integer")
    return value

def _scan_file(path,encoding,max_file_size,predicate,max_line_length=None):
    max_file_size=_validate_limit(max_file_size,"max_file_size")
    if max_line_length is not None: max_line_length=_validate_limit(max_line_length,"max_line_length")
    try:
        initial=path.stat()
        if initial.st_size>max_file_size: raise SearchError(f"Search file exceeds max_file_size: {path}")
        matched=False
        with path.open("r",encoding=encoding,newline="") as handle:
            for line in handle:
                current=handle.buffer.tell() if hasattr(handle,"buffer") else None
                if current is not None and current>max_file_size: raise SearchError(f"Search file grew beyond max_file_size: {path}")
                if max_line_length is not None and len(line)>max_line_length: raise SearchError(f"Search line exceeds max_line_length: {path}")
                if predicate(line): matched=True
        final=path.stat()
        signature=lambda st:(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
        if signature(initial)!=signature(final): raise SearchError(f"File changed during search: {path}")
        return matched
    except SearchError: raise
    except (OSError,UnicodeError) as exc: raise SearchError(f"Unable to read {path}: {exc}") from exc

def find_text(path,text,encoding="utf-8",max_file_size=DEFAULT_MAX_SEARCH_FILE_SIZE):
    if not isinstance(text,str): raise TypeError("text must be a string")
    encoding=_validate_encoding(encoding); results=[]
    for item in _walk(path):
        try:
            if not item.is_file(): continue
        except OSError as exc: raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if _scan_file(item,encoding,max_file_size,lambda line:text in line): results.append(item)
    return _sorted_paths(results)

def find_pattern(path,pattern,encoding="utf-8",max_file_size=DEFAULT_MAX_SEARCH_FILE_SIZE,max_line_length=DEFAULT_MAX_REGEX_LINE_LENGTH):
    if not isinstance(pattern,str) or not pattern: raise InvalidPatternError("Pattern is required.")
    encoding=_validate_encoding(encoding)
    try: regex=re.compile(pattern)
    except re.error as exc: raise InvalidPatternError(str(exc)) from exc
    results=[]
    for item in _walk(path):
        try:
            if not item.is_file(): continue
        except OSError as exc: raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if _scan_file(item,encoding,max_file_size,regex.search,max_line_length): results.append(item)
    return _sorted_paths(results)

def find_by_extension(path,extension):
    if not isinstance(extension,str) or not extension.strip(): raise InvalidExtensionError("Extension is required.")
    extension=extension.strip(); extension=extension if extension.startswith(".") else "."+extension
    if extension==".": raise InvalidExtensionError("Extension is required.")
    results=[]
    for item in _walk(path):
        try:
            if item.is_file() and item.suffix.casefold()==extension.casefold(): results.append(item)
        except OSError as exc: raise SearchError(f"Unable to inspect {item}: {exc}") from exc
    return _sorted_paths(results)

def find_by_size(path,minimum=None,maximum=None):
    for value,name in ((minimum,"minimum"),(maximum,"maximum")):
        if value is not None and (not isinstance(value,int) or isinstance(value,bool) or value<0): raise ValueError(f"{name} must be a non-negative integer or None")
    if minimum is not None and maximum is not None and minimum>maximum: raise ValueError("minimum cannot be greater than maximum")
    results=[]
    for item in _walk(path):
        try:
            if not item.is_file(): continue
            size=item.stat().st_size
        except OSError as exc: raise SearchError(f"Unable to inspect {item}: {exc}") from exc
        if (minimum is not None and size<minimum) or (maximum is not None and size>maximum): continue
        results.append(item)
    return _sorted_paths(results)

find=find_paths
search_contents=find_text
search_regex=find_pattern
find_extension=find_by_extension
