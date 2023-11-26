import hashlib


def sha256(content: str | bytes) -> str:
    hash_handler = hashlib.sha256()
    hash_content = content.encode() if isinstance(content, str) else content
    hash_handler.update(hash_content)

    return hash_handler.hexdigest()


def sha256_file(filepath):
    hash_handler = hashlib.sha256()
    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            hash_handler.update(chunk)

    return hash_handler.hexdigest()
