"""Streaming hashing utilities with concurrent-change detection."""
from __future__ import annotations
import hashlib
from .exceptions import HashingError, UnsupportedHashAlgorithmError, ConcurrentModificationError
from .utils import ensure_file

def hash_algorithms():
    return sorted({name.lower().replace("-","").replace("_","") for name in hashlib.algorithms_available})

def _normalize_algorithm(algorithm):
    if not isinstance(algorithm,str) or not algorithm.strip(): raise UnsupportedHashAlgorithmError(algorithm)
    requested=algorithm.strip().lower().replace("-","").replace("_","")
    aliases={"sha1":"sha1","sha224":"sha224","sha256":"sha256","sha384":"sha384","sha512":"sha512","sha512224":"sha512_224","sha512256":"sha512_256","sha3224":"sha3_224","sha3256":"sha3_256","sha3384":"sha3_384","sha3512":"sha3_512","md5":"md5","blake2b":"blake2b","blake2s":"blake2s"}
    if requested in aliases: return aliases[requested]
    available={name.lower().replace("-","").replace("_",""):name for name in hashlib.algorithms_available}
    try:
        normalized=available[requested]
    except KeyError as exc: raise UnsupportedHashAlgorithmError(algorithm) from exc
    try:
        probe=hashlib.new(normalized)
        if hasattr(probe,"digest_size") and probe.digest_size == 0:
            raise UnsupportedHashAlgorithmError(algorithm)
        probe.hexdigest()
    except (TypeError,ValueError) as exc: raise UnsupportedHashAlgorithmError(algorithm) from exc
    return normalized

def file_hash(path,algorithm="sha256",chunk_size=1024*1024):
    normalized=_normalize_algorithm(algorithm)
    if not isinstance(chunk_size,int) or isinstance(chunk_size,bool) or chunk_size<=0: raise ValueError("chunk_size must be a positive integer")
    try:
        target=ensure_file(path); before=target.stat()
        if before.st_size<0: raise HashingError(str(path))
        digest=hashlib.new(normalized)
        with target.open("rb") as file:
            while True:
                chunk=file.read(chunk_size)
                if not chunk: break
                digest.update(chunk)
        after=target.stat()
        signature=lambda st:(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
        if signature(before)!=signature(after): raise ConcurrentModificationError("File changed while it was being hashed.")
        return digest.hexdigest()
    except (UnsupportedHashAlgorithmError,ConcurrentModificationError,HashingError): raise
    except OSError as exc: raise HashingError(str(path)) from exc

def hash_bytes(data,algorithm="sha256"):
    if not isinstance(data,(bytes,bytearray,memoryview)): raise TypeError("data must be bytes-like")
    try: digest=hashlib.new(_normalize_algorithm(algorithm)); digest.update(data); return digest.hexdigest()
    except UnsupportedHashAlgorithmError: raise
    except (TypeError,ValueError) as exc: raise HashingError(str(exc)) from exc

available_hash_algorithms=hash_algorithms
hash_file=file_hash
