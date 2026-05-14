# kb — CARP Knowledge Base

Pipeline for ingesting and indexing CARP documentation, built for retrieval. Supports vector, hybrid, and classic TF-IDF indexes. Documents pass through three stages: pre-processing (extraction), splitting (chunking), and indexing.

## Commands

```bash
uv run kb pre-process   # extract raw documents from all enabled sources
uv run kb split         # split documents into chunks
uv run kb index         # embed chunks and upsert into Qdrant
```

All commands accept `--config` / `-c` to point at a non-default config file (default: `kb.toml`).

## Configuration

```toml
# kb.toml

[[sources]]
name    = "carp-docs-mintlify"
type    = "mintlify"
path    = "sources/carp-docs-mintlify"   # path relative to this file
enabled = true
ignore  = ["docs/api-reference/*", "openapi.json"]  # optional, gitignore-style patterns

[pipeline]
documents_path = "data/preprocessed/documents.jsonl"  # optional, this is the default
```

Each source entry requires `name`, `type`, and `path`. Set `enabled = false` to skip a source without removing it. `ignore` accepts gitignore-style patterns matched against paths relative to the source root.
