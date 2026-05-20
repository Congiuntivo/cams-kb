from __future__ import annotations

import logging

logging.getLogger("LiteLLM").setLevel(logging.ERROR)

import litellm  # noqa: E402


def embed_dense(texts: list[str], model: str) -> list[list[float]]:
    if not texts:
        return []
    response = litellm.embedding(model=model, input=texts)
    return [item["embedding"] for item in response.data]
