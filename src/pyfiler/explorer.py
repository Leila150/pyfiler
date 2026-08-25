"""High-level rooted filesystem interface."""
from __future__ import annotations
from .utils import to_path, safe_inside
from .files import read_contents, append_contents, remove_contents, replace_contents, create_file, delete_file, copy_file, move_file, rename_file, touch_file, file_exists, clear_file
from .folders import create_folder, move_into, delete_folder, list_folder, remove_from_folder, list_files, list_folders, clear_folder, copy_folder, move_folder, rename_folder
from .search import find_paths, find_files, find_folders, find_text, find_pattern, find_by_extension, find_by_size
from .metadata import metadata, exists, is_file, is_folder, is_empty, size_of, name_of, stem_of, extension_of, path_kind, same_type, permissions, created_at, modified_at, accessed_at
from .hashing import file_hash, hash_algorithms
from .comparison import files_equal
from .tree import directory_tree, directory_size, count_files, count_folders, extension_counts
from .paths import absolute_path, relative_path, parent_path, file_name, file_extension, file_stem, join_paths, normalize_path
from .exceptions import InvalidRootError, RootNotFoundError, PathOutsideRootError

class Explorer:
    """Operate on filesystem paths while enforcing a configured root.

    Explorer rejects symlink components during path preflight. This blocks the
    common deliberate symlink traversal case; descriptor-based platform APIs
    are still required for absolute protection against hostile concurrent swaps.
    """
    def __init__(self, root=".", create=False):
        self.root=to_path(root).resolve()
        if self.root.exists() and not self.root.is_dir(): raise InvalidRootError(str(self.root))
        if not self.root.exists():
            if create: self.root.mkdir(parents=True,exist_ok=True)
            else: raise RootNotFoundError(str(self.root))
    def _path(self,path="."): return safe_inside(path,self.root,reject_symlinks=True)
    def _source(self,path):
        """Validate an Explorer source and require it to remain inside root."""
        return self._path(path)
    def read_contents(self,name,line_num=None): return read_contents(name,line_num,self._path(name))
    def append_contents(self,name,contents): return append_contents(name,contents,self._path(name))
    def remove_contents(self,name,line_num=None): return remove_contents(name,line_num,self._path(name))
    def replace_contents(self,name,contents): return replace_contents(name,contents,self._path(name))
    def create_file(self,name,contents=""): return create_file(name,contents,self._path(name))
    def delete_file(self,name): return delete_file(name,self._path(name))
    def copy_file(self,source,destination,overwrite=False): return copy_file(self._source(source),self._path(destination),overwrite)
    def move_file(self,source,destination,overwrite=False): return move_file(self._source(source),self._path(destination),overwrite)
    def rename_file(self,name,new_name): return rename_file(self._path(name),new_name)
    def touch_file(self,name): return touch_file(name,self._path(name))
    def file_exists(self,name): return file_exists(name,self._path(name))
    def clear_file(self,name): return clear_file(name,self._path(name))
    get_contents=read_contents; add_contents=append_contents; edit_contents=replace_contents; read_file=read_contents; write_file=replace_contents; append_file=append_contents
    def create_folder(self,name,contents=None):
        destination=self._path(name)
        if contents is None: return create_folder(name,None,destination)
        sources=contents if isinstance(contents,(list,tuple)) else [contents]
        validated=[self._source(source) for source in sources]
        return create_folder(name,validated,destination)
    def move_into(self,child,parent): return move_into(self._source(child),self._path(parent))
    def delete_folder(self,name,recursive=False): return delete_folder(self._path(name),recursive)
    def list_folder(self,name="."): return list_folder(self._path(name))
    def remove_from_folder(self,name,child): return remove_from_folder(self._path(name),child)
    def list_files(self,name="."): return list_files(self._path(name))
    def list_folders(self,name="."): return list_folders(self._path(name))
    def clear_folder(self,name="."): return clear_folder(self._path(name))
    def copy_folder(self,source,destination,overwrite=False): return copy_folder(self._source(source),self._path(destination),overwrite)
    def move_folder(self,source,destination,overwrite=False): return move_folder(self._source(source),self._path(destination),overwrite)
    def rename_folder(self,name,new_name): return rename_folder(self._path(name),new_name)
    add_parent=move_into; folder_contents=list_folder; folder_remove_contents=remove_from_folder
    def find_paths(self,name=".",pattern="*"): return find_paths(self._path(name),pattern)
    def find_files(self,name=".",pattern="*"): return find_files(self._path(name),pattern)
    def find_folders(self,name=".",pattern="*"): return find_folders(self._path(name),pattern)
    def find_text(self,name=".",text="",**kwargs): return find_text(self._path(name),text,**kwargs)
    def find_pattern(self,name=".",pattern="",**kwargs): return find_pattern(self._path(name),pattern,**kwargs)
    def find_by_extension(self,name=".",extension=""): return find_by_extension(self._path(name),extension)
    def find_by_size(self,name=".",minimum=None,maximum=None): return find_by_size(self._path(name),minimum,maximum)
    find=find_paths; search_contents=find_text; search_regex=find_pattern; find_extension=find_by_extension
    def exists(self,name="."): return exists(self._path(name))
    def is_file(self,name): return is_file(self._path(name))
    def is_folder(self,name): return is_folder(self._path(name))
    def is_empty(self,name): return is_empty(self._path(name))
    def metadata(self,name): return metadata(self._path(name))
    def size_of(self,name): return size_of(self._path(name))
    def name_of(self,name): return name_of(self._path(name))
    def stem_of(self,name): return stem_of(self._path(name))
    def extension_of(self,name): return extension_of(self._path(name))
    def path_kind(self,name): return path_kind(self._path(name))
    def same_type(self,first,second): return same_type(self._path(first),self._path(second))
    def permissions(self,name): return permissions(self._path(name))
    def created_at(self,name): return created_at(self._path(name))
    def modified_at(self,name): return modified_at(self._path(name))
    def accessed_at(self,name): return accessed_at(self._path(name))
    def file_hash(self,name,algorithm="sha256",chunk_size=1024*1024): return file_hash(self._path(name),algorithm,chunk_size)
    @staticmethod
    def hash_algorithms(): return hash_algorithms()
    def files_equal(self,first,second,shallow=False): return files_equal(self._path(first),self._path(second),shallow)
    def directory_tree(self,name=".",max_depth=None): return directory_tree(self._path(name),max_depth)
    def directory_size(self,name="."): return directory_size(self._path(name))
    def count_files(self,name="."): return count_files(self._path(name))
    def count_folders(self,name="."): return count_folders(self._path(name))
    def extension_counts(self,name="."): return extension_counts(self._path(name))
    def absolute_path(self,name="."): return absolute_path(self._path(name))
    def relative_path(self,name=".",start=None): return relative_path(self._path(name),self._path(start) if start is not None else self.root)
    def parent_path(self,name="."):
        current=self._path(name)
        if current==self.root: return "."
        parent=current.parent
        if parent==self.root or self.root in parent.parents: return str(parent)
        raise PathOutsideRootError(f"Parent of {current} is outside {self.root}")
    def file_name(self,name): return file_name(self._path(name))
    def file_extension(self,name): return file_extension(self._path(name))
    def file_stem(self,name): return file_stem(self._path(name))
    def join_paths(self,*parts):
        if not parts: return str(self.root)
        if any(to_path(part).is_absolute() for part in parts): raise PathOutsideRootError("Explorer.join_paths accepts only relative components")
        return str(self._path(join_paths(*parts)))
    def normalize_path(self,name="."): return normalize_path(self._path(name))
    def path(self,name="."): return self._path(name)
    def relative(self,name="."): return self._path(name).relative_to(self.root)
