import hashlib


def sha256_checksum(filepath):
    hash_handler = hashlib.sha256()
    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            hash_handler.update(chunk)

    return hash_handler.hexdigest()
