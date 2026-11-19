# kb — CARP Knowledge Base

Pipeline for ingesting and indexing CARP documentation, built for retrieval. Supports vector, hybrid, and classic TF-IDF indexes. Documents pass through four stages: pre-processing (extraction), splitting (chunking), indexing (embedding), and upload (Qdrant).

Once uploaded, the collection can be queried directly with dense, sparse, or hybrid retrieval and optional ColBERT reranking.

## Setup

1. Clone with submodules:
   ```bash
   git clone --recurse-submodules <repo>
   cd knowledge-base
   ```
2. Install dependencies with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync --all-extras
   ```
3. Start a Qdrant instance (default: `http://localhost:6333`):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
4. Set any provider keys the dense model needs in `.env`
   (e.g. `OPENAI_API_KEY`, `HF_TOKEN` for gated FastEmbed models).

Then run the pipeline stages (see Commands).

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

```bash
# Search the Qdrant collection with a text query.
uv run kb query "what is CARP?"                          # hybrid + reranking (defaults from kb.toml)
uv run kb query --method dense --limit 5 "install"       # dense-only, 5 results
uv run kb query --method hybrid --no-rerank "auth"       # hybrid with RRF fusion, no reranking
uv run kb query --method sparse "deploy"                 # BM25-only
```

All commands accept `--config` / `-c` to point at a non-default config file (default: `kb.toml`).

## Configuration

`kb.toml` has four top-level tables: `sources` (one entry per documentation source), `pipeline` (extraction and chunking), `search` (embedding models and Qdrant connection, shared by index and query), and `indexing` (pipeline-only batch and path settings). A `query` table holds retrieval defaults that can be overridden at the CLI. All tables except `sources` are optional — the snippet below shows the defaults.

```toml
# kb.toml

[[sources]]
name    = "carp-docs-mintlify"
type    = "mintlify"
path    = "sources/carp-docs-mintlify"          # relative to this file
enabled = true
blacklist = ["api-reference", "docs/index.mdx"]  # optional, gitignore-style patterns to exclude
whitelist = ["docs/**"]                          # optional, only include matching paths

[pipeline]
documents_path = "data/preprocessed/documents.jsonl"
chunks_path    = "data/split/chunks.jsonl"

[pipeline.chunking]
chunk_size    = 1000
chunk_overlap = 150

[search]
dense_model     = "openai/text-embedding-3-small"
sparse_model    = "Qdrant/bm25"
multi_model     = "colbert-ir/colbertv2.0"
collection_name = "knowledge-base"
qdrant_url      = "http://localhost:6333"

[indexing]
points_path       = "data/indexes/points.jsonl"
batch_size        = 64
upload_batch_size = 32

[query]
method         = "hybrid"   # dense | sparse | hybrid
rerank         = true       # apply ColBERT reranking (hybrid only)
limit          = 10         # results returned
prefetch_limit = 50         # candidates fetched per branch before fusion/reranking
```

Each source entry requires `name`, `type`, and `path`. `type` selects the adapter: `mintlify` for MDX docs with YAML frontmatter and MDX components, `markdown` for plain `.md` files. Set `enabled = false` to skip a source without removing it. `blacklist` and `whitelist` both accept gitignore-style patterns matched against paths relative to the source root. `blacklist` excludes matching paths unconditionally; `whitelist`, when non-empty, restricts processing to paths that match at least one pattern (blacklist still wins).

## Pipeline

### Pre-process

Each source `type` is bound to an adapter (`MintlifyAdapter`, …) via a registry. The adapter walks its root, applies the configured `blacklist`/`whitelist` patterns, parses each file into a `RawDocument` (id, title, body, source path, metadata), and runs a source-specific `post_process` hook for cleanup — for Mintlify, that means stripping YAML frontmatter and rewriting MDX components into plain markdown. Documents are streamed straight to `documents.jsonl`.

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

### Query

Connects to Qdrant and retrieves the top-N results for a text query. Three retrieval strategies are supported:

- **`dense`** — embeds the query with the dense model and retrieves by cosine similarity.
- **`sparse`** — embeds the query with the BM25 model and retrieves by IDF-weighted lexical overlap.
- **`hybrid`** — runs both branches in parallel as prefetch queries, then either fuses them with Reciprocal Rank Fusion (`--no-rerank`) or reranks the fused candidates with ColBERT late-interaction MaxSim (`--rerank`).

Results are displayed as a ranked table with score, document title, source path, and a text snippet.

## License

Licensed under MIT; see [LICENSE](LICENSE).
