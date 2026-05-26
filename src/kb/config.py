from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    name: str
    type: str
    path: Path
    enabled: bool = True
    blacklist: list[str] = Field(
        [], description="Gitignore-style patterns to exclude from this source."
    )
    whitelist: list[str] = Field(
        [],
        description="Gitignore-style patterns to include; if non-empty, only matching files are processed.",
    )


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(1000, description="Max characters per chunk (second pass).")
    chunk_overlap: int = Field(
        150, description="Character overlap between consecutive chunks."
    )


class PipelineConfig(BaseModel):
    documents_path: Path = Field(
        Path("data/preprocessed/documents.jsonl"),
        description="Relative path to save pre-processed documents, from the repository root.",
    )
    chunks_path: Path = Field(
        Path("data/split/chunks.jsonl"),
        description="Relative path to save chunks, from the repository root.",
    )
    chunking: ChunkingConfig = ChunkingConfig()


class SearchConfig(BaseModel):
    dense_model: str = Field("openai/text-embedding-3-small")
    sparse_model: str = Field("Qdrant/bm25")
    multi_model: str = Field("colbert-ir/colbertv2.0")
    collection_name: str = Field("knowledge-base")
    qdrant_url: str = Field(
        "http://localhost:6333", description="URL of the Qdrant instance."
    )


class IndexingConfig(BaseModel):
    points_path: Path = Field(
        Path("data/indexes/points.jsonl"),
        description="Relative path to save index points, from the repository root.",
    )
    batch_size: int = Field(64, description="Number of chunks to embed per API call.")
    upload_batch_size: int = Field(
        32, description="Number of points per Qdrant upsert request."
    )


class QueryConfig(BaseModel):
    method: Literal["dense", "sparse", "hybrid"] = Field("hybrid")
    rerank: bool = Field(
        True, description="Apply ColBERT reranking over hybrid results."
    )
    limit: int = Field(10, description="Number of results to return.")
    prefetch_limit: int = Field(
        50, description="Candidates fetched per branch before fusion or reranking."
    )


class Config(BaseModel):
    sources: list[SourceConfig]
    pipeline: PipelineConfig = PipelineConfig()
    search: SearchConfig = SearchConfig()
    indexing: IndexingConfig = IndexingConfig()
    query: QueryConfig = QueryConfig()

    @property
    def enabled_sources(self) -> list[SourceConfig]:
        return [s for s in self.sources if s.enabled]

    @classmethod
    def from_toml(cls, path: Path) -> Config:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls.model_validate(data)
