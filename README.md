# kb — CARP Knowledge Base

Pipeline for ingesting and indexing CARP documentation, built for retrieval. Supports vector, hybrid, and classic TF-IDF indexes. Documents pass through four stages: pre-processing (extraction), splitting (chunking), indexing (embedding), and upload (Qdrant).

## Commands

```bash
# Extract clean documents from every enabled source and write them to JSONL.
uv run kb pre-process
```

```bash
# Chunk the pre-processed documents into retrievable units.
uv run kb split
```

```bash
# Embed chunks with dense, sparse, and multi-vector models and serialize the resulting points.
uv run kb index
```

```bash
# Push the serialized points into Qdrant; pass `--recreate` to rebuild the collection from scratch.
uv run kb upload
```

All commands accept `--config` / `-c` to point at a non-default config file (default: `kb.toml`).

## Configuration

`kb.toml` has three top-level tables: `sources` (one entry per documentation source), `pipeline` (extraction and chunking), and `indexing` (embeddings and Qdrant). The `pipeline` and `indexing` tables are optional — the snippet below shows the defaults.

```toml
# kb.toml

[[sources]]
name    = "carp-docs-mintlify"
type    = "mintlify"
path    = "sources/carp-docs-mintlify"          # relative to this file
enabled = true
ignore  = ["api-reference", "docs/index.mdx"]   # optional, gitignore-style patterns

[pipeline]
documents_path = "data/preprocessed/documents.jsonl"
chunks_path    = "data/split/chunks.jsonl"

[pipeline.chunking]
chunk_size    = 1000
chunk_overlap = 150

[indexing]
dense_model       = "openai/text-embedding-3-small"
sparse_model      = "Qdrant/bm25"
multi_model       = "colbert-ir/colbertv2.0"
points_path       = "data/indexes/points.jsonl"
batch_size        = 64
upload_batch_size = 32
collection_name   = "knowledge-base"
qdrant_url        = "http://localhost:6333"
```

Each source entry requires `name`, `type`, and `path`. Set `enabled = false` to skip a source without removing it. `ignore` accepts gitignore-style patterns matched against paths relative to the source root.

## Pipeline

### Pre-process

Each source `type` is bound to an adapter (`MintlifyAdapter`, …) via a registry. The adapter walks its root, applies the configured `ignore` patterns, parses each file into a `RawDocument` (id, title, body, source path, metadata), and runs a source-specific `post_process` hook for cleanup — for Mintlify, that means stripping YAML frontmatter and rewriting MDX components into plain markdown. Documents are streamed straight to `documents.jsonl`.

### Split

A two-pass strategy backed by LangChain splitters:

1. `MarkdownHeaderTextSplitter` splits on headers h1–h3, preserving the header trail in each chunk's metadata so context is not lost.
2. `RecursiveCharacterTextSplitter` enforces `chunk_size` characters with `chunk_overlap` overlap, falling back through paragraph, sentence, and word boundaries.

Chunk ids are derived deterministically from the parent document id, so re-runs are stable.

### Index

Each chunk is embedded into three complementary representations and written to `points.jsonl`.

1. Dense vectors (configured `dense_model`) capture semantic similarity;
2. sparse vectors (BM25 via `Qdrant/bm25`) provide IDF-weighted lexical recall;
3. multi-vector embeddings (`colbert-ir/colbertv2.0`) emit one vector per token for late-interaction MaxSim scoring.

Chunks are processed in batches of `batch_size`, and each point carries its full payload — text, source, headers, package, and chunk index — so retrieval has everything it needs without a second lookup.

### Upload

Connects to Qdrant at `qdrant_url` and ensures the target collection exists with three named vector configs: `dense` (cosine), `sparse` (with the `IDF` modifier so Qdrant computes BM25-style scoring), and `multi` (cosine + `MaxSim` comparator, with HNSW disabled since multi-vectors are reranked rather than ANN-searched).

Points are read from `points.jsonl` and upserted in batches of `upload_batch_size`. Passing `--recreate` drops the existing collection before rebuilding it.
