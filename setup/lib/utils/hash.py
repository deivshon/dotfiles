import hashlib


def sha256_checksum(filepath):
    hashHandler = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hashHandler.update(chunk)

    return hashHandler.hexdigest()
