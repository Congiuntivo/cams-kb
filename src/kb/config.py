from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    name: str
    type: str
    path: Path
    enabled: bool = True
    ignore: list[str] = Field(
        [], description="List of gitignore-style patterns to exclude from this source."
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


class IndexingConfig(BaseModel):
    dense_model: str = Field("openai/text-embedding-3-small")
    sparse_model: str = Field("Qdrant/bm25")
    multi_model: str = Field("colbert-ir/colbertv2.0")
    points_path: Path = Field(
        Path("data/indexes/points.jsonl"),
        description="Relative path to save index points, from the repository root.",
    )
    batch_size: int = Field(64, description="Number of chunks to embed per API call.")


class Config(BaseModel):
    sources: list[SourceConfig]
    pipeline: PipelineConfig = PipelineConfig()
    indexing: IndexingConfig = IndexingConfig()

    @property
    def enabled_sources(self) -> list[SourceConfig]:
        return [s for s in self.sources if s.enabled]

    @classmethod
    def from_toml(cls, path: Path) -> Config:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls.model_validate(data)
