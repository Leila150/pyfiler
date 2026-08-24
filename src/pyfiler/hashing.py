"""Hashing utilities."""
import hashlib
from .utils import ensure_file
from .exceptions import UnsupportedHashAlgorithmError, HashingError


def available_hash_algorithms(): return sorted(hashlib.algorithms_available)

def hash_file(path, algorithm="sha256", chunk_size=1024*1024):
    if algorithm not in hashlib.algorithms_available: raise UnsupportedHashAlgorithmError(algorithm)
    if not isinstance(chunk_size,int) or chunk_size<=0: raise ValueError("chunk_size must be positive")
    try:
        digest=hashlib.new(algorithm)
        with ensure_file(path).open("rb") as file:
            for chunk in iter(lambda:file.read(chunk_size),b""): digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc: raise HashingError(str(path)) from exc
