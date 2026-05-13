from __future__ import annotations

from pathlib import Path

import typer

from kb.config import Config
from kb.pipeline.index import run_index_qdrant

app = typer.Typer(help="Build a retrieval index from pre-processed documents.")


@app.callback(invoke_without_command=True)
def index(
    ctx: typer.Context,
    source: list[str] = typer.Option(
        [], "--source", "-s", help="Source name to index (repeatable)."
    ),
) -> None:
    config: Config = ctx.obj["config"]
    repo_root: Path = ctx.obj["repo_root"]
    run_index_qdrant(config, source or None, repo_root)
