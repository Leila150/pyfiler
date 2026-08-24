"""Hashing utilities."""

from __future__ import annotations

import hashlib

from .exceptions import HashingError, UnsupportedHashAlgorithmError
from .utils import ensure_file


def hash_algorithms():
    """Return supported hashlib algorithm names in deterministic order."""
    return sorted(hashlib.algorithms_available)


def file_hash(path, algorithm="sha256", chunk_size=1024 * 1024):
    """Return the hexadecimal digest of a file."""
    if not isinstance(algorithm, str) or not algorithm.strip():
        raise UnsupportedHashAlgorithmError(algorithm)
    algorithm = algorithm.strip().lower().replace("-", "_")

    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    try:
        digest = hashlib.new(algorithm)
    except (ValueError, TypeError) as exc:
        raise UnsupportedHashAlgorithmError(algorithm) from exc

    try:
        with ensure_file(path).open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc:
        raise HashingError(str(path)) from exc


# Backwards-compatible aliases.
available_hash_algorithms = hash_algorithms
hash_file = file_hash
