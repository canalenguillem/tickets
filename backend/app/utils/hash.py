import hashlib

def generate_file_hash(file_content: bytes) -> str:
    sha256 = hashlib.sha256()
    sha256.update(file_content)
    return sha256.hexdigest()
