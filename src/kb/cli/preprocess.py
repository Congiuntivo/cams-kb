from __future__ import annotations

from pathlib import Path

import typer

from kb.config import Config
from kb.pipeline.preprocess import run_preprocess

app = typer.Typer(help="Pre-process raw sources into clean text documents.")


@app.callback(invoke_without_command=True)
def preprocess(
    ctx: typer.Context,
    source: list[str] = typer.Option(
        [], "--source", "-s", help="Source name to process (repeatable)."
    ),
    all_sources: bool = typer.Option(
        False, "--all-sources", help="Process all enabled sources."
    ),
) -> None:
    config: Config = ctx.obj["config"]
    repo_root: Path = ctx.obj["repo_root"]
    names = None if all_sources else (source or None)
    run_preprocess(config, names, repo_root)
