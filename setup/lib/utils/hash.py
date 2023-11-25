import os
import hashlib

from typing import Set


def sha512(filepath):
    hash_handler = hashlib.sha512()
    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            hash_handler.update(chunk)

    return hash_handler.hexdigest()


def file_hashes(dir_path: str) -> Set[str]:
    hashes: Set[str] = set()
    for entry_path in os.listdir(dir_path):
        entry_path = os.path.join(dir_path, entry_path)
        if os.path.isdir(entry_path):
            hashes = hashes.union(file_hashes(entry_path))
        elif os.path.isfile(entry_path):
            hashes.add(sha512(entry_path))

    return hashes
