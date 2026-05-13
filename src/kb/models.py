from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RawDocument(BaseModel):
    id: str
    source_name: str
    source_path: str
    title: str
    body: str
    metadata: dict[str, Any] = {}


class Chunk(BaseModel):
    id: str
    doc_id: str
    source_name: str
    chunk_index: int
    text: str
    metadata: dict[str, Any] = {}
