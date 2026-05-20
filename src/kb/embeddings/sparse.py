from __future__ import annotations

from fastembed import SparseTextEmbedding

from kb.models import SparseVector


def embed_sparse(texts: list[str], model_name: str) -> list[SparseVector]:
    if not texts:
        return []
    model = SparseTextEmbedding(model_name=model_name)
    return [
        SparseVector(indices=list(r.indices), values=list(r.values))
        for r in model.embed(texts)
    ]
