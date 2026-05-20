from __future__ import annotations

from fastembed import LateInteractionTextEmbedding


def embed_multi(texts: list[str], model_name: str) -> list[list[list[float]]]:
    if not texts:
        return []
    model = LateInteractionTextEmbedding(model_name=model_name)
    return [r.tolist() for r in model.embed(texts)]
