"""Streaming hashing utilities."""
from __future__ import annotations

import hashlib

from .exceptions import HashingError, UnsupportedHashAlgorithmError
from .utils import ensure_file


def hash_algorithms():
    """Return normalized, deterministic hashlib algorithm names."""
    return sorted({name.lower().replace("-", "").replace("_", "") for name in hashlib.algorithms_available})


def _normalize_algorithm(algorithm):
    if not isinstance(algorithm, str) or not algorithm.strip():
        raise UnsupportedHashAlgorithmError(algorithm)
    requested = algorithm.strip().lower().replace("-", "").replace("_", "")
    aliases = {
        "sha1": "sha1",
        "sha224": "sha224",
        "sha256": "sha256",
        "sha384": "sha384",
        "sha512": "sha512",
        "sha512224": "sha512_224",
        "sha512256": "sha512_256",
        "sha3224": "sha3_224",
        "sha3256": "sha3_256",
        "sha3384": "sha3_384",
        "sha3512": "sha3_512",
        "md5": "md5",
        "blake2b": "blake2b",
        "blake2s": "blake2s",
    }
    if requested in aliases:
        return aliases[requested]
    available = {
        name.lower().replace("-", "").replace("_", ""): name
        for name in hashlib.algorithms_available
    }
    try:
        return available[requested]
    except KeyError as exc:
        raise UnsupportedHashAlgorithmError(algorithm) from exc


def file_hash(path, algorithm="sha256", chunk_size=1024 * 1024):
    normalized = _normalize_algorithm(algorithm)
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    try:
        digest = hashlib.new(normalized)
        with ensure_file(path).open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (UnsupportedHashAlgorithmError,):
        raise
    except OSError as exc:
        raise HashingError(str(path)) from exc


available_hash_algorithms = hash_algorithms
hash_file = file_hash
