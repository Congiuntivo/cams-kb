import hashlib


def document_id(source_name: str, source_path: str) -> str:
    raw = f"{source_name}:{source_path}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def chunk_id(doc_id: str, chunk_index: int) -> str:
    raw = f"{doc_id}:{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
