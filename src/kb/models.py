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


class SparseVector(BaseModel):
    indices: list[int]
    values: list[float]


class IndexPointVectors(BaseModel):
    dense: list[float]
    sparse: SparseVector
    multi: list[list[float]]


class IndexPointPayload(BaseModel):
    chunk_id: str
    doc_id: str
    source_name: str
    package: str
    chunk_index: int
    text: str
    doc_title: str
    doc_description: str
    source_path: str
    headers: dict[str, Any]


class IndexPoint(BaseModel):
    id: int
    vectors: IndexPointVectors
    payload: IndexPointPayload
