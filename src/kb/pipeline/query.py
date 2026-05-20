from __future__ import annotations

import time

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Fusion,
    FusionQuery,
    Prefetch,
    SparseVector,
)
from rich.console import Console
from rich.table import Table

from kb.config import Config, SearchConfig
from kb.embeddings.dense import embed_dense
from kb.embeddings.multi import embed_multi
from kb.embeddings.sparse import embed_sparse
from kb.utils.console import error, info


def run_query(
    config: Config,
    text: str,
    method: str,
    rerank: bool,
    limit: int,
    full: bool = False,
) -> None:
    search_cfg = config.search
    query_cfg = config.query
    client = QdrantClient(url=search_cfg.qdrant_url)

    if not client.collection_exists(search_cfg.collection_name):
        error(
            f"Collection [bold]{search_cfg.collection_name}[/bold] does not exist. "
            "Run [bold]kb upload[/bold] first."
        )
        return

    info(
        f"Querying [bold]{search_cfg.collection_name}[/bold] "
        f"(method=[bold]{method}[/bold], rerank=[bold]{rerank}[/bold], limit=[bold]{limit}[/bold])..."
    )

    t0 = time.perf_counter()
    kwargs = _build_query_kwargs(
        text, method, rerank, limit, query_cfg.prefetch_limit, search_cfg
    )
    t1 = time.perf_counter()
    results = client.query_points(
        collection_name=search_cfg.collection_name,
        **kwargs,
    ).points
    t2 = time.perf_counter()

    embed_ms = (t1 - t0) * 1000
    search_ms = (t2 - t1) * 1000
    total_ms = (t2 - t0) * 1000
    latency_line = (
        f"Latency — embed: [bold]{embed_ms:.0f} ms[/bold]  "
        f"search: [bold]{search_ms:.0f} ms[/bold]  "
        f"total: [bold]{total_ms:.0f} ms[/bold]"
    )

    if not results:
        info("No results found.")
        info(latency_line)
        return

    _display_results(results, full)
    info(latency_line)


def _build_query_kwargs(
    text: str,
    method: str,
    rerank: bool,
    limit: int,
    prefetch_limit: int,
    cfg: SearchConfig,
) -> dict:
    if method == "dense":
        dense_vec = embed_dense([text], cfg.dense_model)[0]
        return {"query": dense_vec, "using": "dense", "limit": limit}

    if method == "sparse":
        sparse_vec = embed_sparse([text], cfg.sparse_model)[0]
        return {
            "query": SparseVector(indices=sparse_vec.indices, values=sparse_vec.values),
            "using": "sparse",
            "limit": limit,
        }

    # hybrid
    dense_vec = embed_dense([text], cfg.dense_model)[0]
    sparse_vec = embed_sparse([text], cfg.sparse_model)[0]

    prefetch = [
        Prefetch(query=dense_vec, using="dense", limit=prefetch_limit),
        Prefetch(
            query=SparseVector(indices=sparse_vec.indices, values=sparse_vec.values),
            using="sparse",
            limit=prefetch_limit,
        ),
    ]

    if rerank:
        multi_vec = embed_multi([text], cfg.multi_model)[0]
        return {
            "prefetch": prefetch,
            "query": multi_vec,
            "using": "multi",
            "limit": limit,
        }

    return {"prefetch": prefetch, "query": FusionQuery(type=Fusion.RRF), "limit": limit}


def _display_results(results: list, full: bool) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=3)
    table.add_column("Score", width=8)
    table.add_column("Title", min_width=20)
    table.add_column("Source", min_width=20)
    table.add_column("Text" if full else "Snippet")

    for rank, point in enumerate(results, start=1):
        payload = point.payload or {}
        score = f"{point.score:.4f}" if point.score is not None else "—"
        title = payload.get("doc_title", "—")
        source = payload.get("source_path", "—")
        text = payload.get("text", "")
        snippet = (
            text.strip()
            if full
            else text[:120].replace("\n", " ") + ("…" if len(text) > 120 else "")
        )
        table.add_row(str(rank), score, title, source, snippet)

    console.print(table)
