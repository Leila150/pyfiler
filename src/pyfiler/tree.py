"""Directory tree and aggregate statistics."""
from collections import Counter
from .utils import ensure_folder
from .exceptions import TreeDepthError


def tree(path, max_depth=None):
    if max_depth is not None and (not isinstance(max_depth,int) or max_depth<0): raise TreeDepthError("max_depth must be non-negative")
    root=ensure_folder(path); lines=[root.name or str(root)]
    def walk(folder,prefix,depth):
        if max_depth is not None and depth>=max_depth:return
        children=sorted(folder.iterdir(),key=lambda p:(p.is_file(),p.name.lower()))
        for i,child in enumerate(children):
            last=i==len(children)-1; lines.append(prefix+("└── " if last else "├── ")+child.name)
            if child.is_dir(): walk(child,prefix+("    " if last else "│   "),depth+1)
    walk(root,"",0); return "\n".join(lines)

def folder_size(path): return sum(p.stat().st_size for p in ensure_folder(path).rglob("*") if p.is_file())
def count_files(path): return sum(1 for p in ensure_folder(path).rglob("*") if p.is_file())
def count_folders(path): return sum(1 for p in ensure_folder(path).rglob("*") if p.is_dir())
def extension_stats(path):
    return dict(Counter(p.suffix.lower() or "<no extension>" for p in ensure_folder(path).rglob("*") if p.is_file()))
