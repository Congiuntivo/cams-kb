from __future__ import annotations

from typing import Optional

import typer

from kb.config import Config
from kb.pipeline.query import run_query

app = typer.Typer(help="Query the Qdrant collection with a text query.")


@app.callback(invoke_without_command=True)
def query(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Query text."),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-n", help="Number of results."
    ),
    method: Optional[str] = typer.Option(
        None, "--method", "-m", help="Retrieval method: dense, sparse, or hybrid."
    ),
    rerank: Optional[bool] = typer.Option(
        None, "--rerank/--no-rerank", help="Apply ColBERT reranking (hybrid only)."
    ),
    full: bool = typer.Option(
        False, "--full", help="Show full chunk text instead of a snippet."
    ),
) -> None:
    config: Config = ctx.obj["config"]
    run_query(
        config=config,
        text=text,
        method=method or config.query.method,
        rerank=rerank if rerank is not None else config.query.rerank,
        limit=limit or config.query.limit,
        full=full,
    )
