"""High-level rooted filesystem interface."""
from .utils import to_path, safe_inside
from .files import get_contents,add_contents,remove_contents,edit_contents,create_file,delete_file,copy_file,move_file,rename_file
from .folders import create_folder,delete_folder,folder_contents,folder_remove_contents,list_dir,list_files,list_folders
from .search import find,find_files,find_folders,search_contents,search_regex,find_extension,find_by_size
from .metadata import metadata
from .exceptions import InvalidRootError,RootNotFoundError

class Explorer:
    """Operate on filesystem paths while enforcing a configured root."""
    def __init__(self,root=".",create=False):
        self.root=to_path(root).resolve()
        if self.root.exists() and not self.root.is_dir(): raise InvalidRootError(str(self.root))
        if not self.root.exists():
            if create:self.root.mkdir(parents=True)
            else:raise RootNotFoundError(str(self.root))
    def _path(self,path): return safe_inside(self.root/to_path(path),self.root) if not to_path(path).is_absolute() else safe_inside(path,self.root)
    def get_contents(self,name,line_num=None): return get_contents(name,line_num,self._path(name))
    def add_contents(self,name,contents): return add_contents(name,contents,self._path(name))
    def remove_contents(self,name,line_num=None): return remove_contents(name,line_num,self._path(name))
    def edit_contents(self,name,contents): return edit_contents(name,contents,self._path(name))
    def create_file(self,name,contents=""): return create_file(name,contents,self._path(name))
    def delete_file(self,name): return delete_file(name,self._path(name))
    def create_folder(self,name): return create_folder(name,trajectory=self._path(name))
    def delete_folder(self,name,recursive=False): return delete_folder(self._path(name),recursive)
    def folder_contents(self,name="."): return folder_contents(self._path(name))
    def folder_remove_contents(self,name,child): return folder_remove_contents(self._path(name),child)
    def list_dir(self,name="."): return list_dir(self._path(name))
    def list_files(self,name="."): return list_files(self._path(name))
    def list_folders(self,name="."): return list_folders(self._path(name))
    def find(self,name=".",pattern="*"): return find(self._path(name),pattern)
    def find_files(self,name=".",pattern="*"): return find_files(self._path(name),pattern)
    def find_folders(self,name=".",pattern="*"): return find_folders(self._path(name),pattern)
    def search_contents(self,name=".",text=""): return search_contents(self._path(name),text)
    def search_regex(self,name=".",pattern=""): return search_regex(self._path(name),pattern)
    def find_extension(self,name=".",extension=""): return find_extension(self._path(name),extension)
    def find_by_size(self,name=".",minimum=None,maximum=None): return find_by_size(self._path(name),minimum,maximum)
    def metadata(self,name): return metadata(self._path(name))
