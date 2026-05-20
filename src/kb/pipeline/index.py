from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Generator

from kb.config import Config, IndexingConfig
from kb.embeddings.dense import embed_dense
from kb.embeddings.multi import embed_multi
from kb.embeddings.sparse import embed_sparse
from kb.models import Chunk, IndexPoint, IndexPointPayload, IndexPointVectors
from kb.utils.console import error, info, success, warn
from kb.utils.storage import load_chunks, save_index_points


def run_index_qdrant(
    config: Config, source_names: list[str] | None, repo_root: Path
) -> None:
    input_path = repo_root / config.pipeline.chunks_path
    if not input_path.exists():
        error(
            f"Chunks file not found: {input_path}. Run [bold]kb split[/bold] first or check your configuration."
        )
        return

    index_config = config.indexing
    output_path = repo_root / index_config.points_path

    chunks = _filter_chunks(list(load_chunks(input_path)), source_names)

    if not chunks:
        warn("No chunks to index.")
        return

    info(
        f"Indexing [bold]{len(chunks)}[/bold] chunks in batches of {index_config.batch_size}..."
    )

    points: list[IndexPoint] = []
    base_id = 0
    for batch in _batched(chunks, index_config.batch_size):
        batch_points = _embed_batch(batch, base_id, index_config)
        points.extend(batch_points)
        base_id += len(batch)
        info(f"\tEmbedded {base_id}/{len(chunks)} chunks")

    total = save_index_points(points, output_path)
    success(f"Saved [bold]{total}[/bold] points → {output_path}")


def _filter_chunks(chunks: list[Chunk], source_names: list[str] | None) -> list[Chunk]:
    """Filter chunks by source name.

    From the list of all chunks, keep only those whose source_name is in the provided list.
    If the list is empty or None, keep all chunks.

    Args:
        chunks: List of all chunks to filter.
        source_names: List of source names to keep, or None to keep all.

    Returns:
        List of chunks whose source_name is in the provided list, or all chunks if the list is empty or None.

    Raises:
        ValueError: If any source name in the provided list is not found in the chunks.
    """
    if source_names is None:
        return chunks
    available = {c.source_name for c in chunks}
    for name in source_names:
        if name not in available:
            error(
                f"Source [bold]{name}[/bold] not found in chunks "
                f"(available: {', '.join(sorted(available))})."
            )
    requested = set(source_names)
    return [c for c in chunks if c.source_name in requested]


def _embed_batch(
    batch: list[Chunk], base_id: int, cfg: IndexingConfig
) -> list[IndexPoint]:
    """Embed a batch of chunks into index points."""
    texts = [c.text for c in batch]

    dense_vecs = embed_dense(texts, cfg.dense_model)
    sparse_vecs = embed_sparse(texts, cfg.sparse_model)
    multi_vecs = embed_multi(texts, cfg.multi_model)

    return [
        IndexPoint(
            id=base_id + i,
            vectors=IndexPointVectors(
                dense=dense_vecs[i],
                sparse=sparse_vecs[i],
                multi=multi_vecs[i],
            ),
            payload=IndexPointPayload(
                chunk_id=chunk.id,
                doc_id=chunk.doc_id,
                source_name=chunk.source_name,
                package=chunk.metadata.get("package", ""),
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                doc_title=chunk.metadata.get("doc_title", ""),
                source_path=chunk.metadata.get("source_path", ""),
                headers=chunk.metadata.get("headers", {}),
            ),
        )
        for i, chunk in enumerate(batch)
    ]


def _batched(items: list[Chunk], size: int) -> Generator[list[Chunk], None, None]:
    """Yield successive batches of a given size from a list of items."""
    it = iter(items)
    while batch := list(islice(it, size)):
        yield batch
