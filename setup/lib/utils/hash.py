import os
import hashlib

from typing import Set


def sha512(content: str | bytes) -> str:
    hash_handler = hashlib.sha512()
    hash_content = content.encode() if isinstance(content, str) else content
    hash_handler.update(hash_content)

    return hash_handler.hexdigest()


def sha512_file(filepath):
    hash_handler = hashlib.sha512()
    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            hash_handler.update(chunk)

    return hash_handler.hexdigest()
