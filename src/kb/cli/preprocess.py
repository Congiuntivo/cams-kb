from __future__ import annotations

from pathlib import Path

import typer

from kb.config import Config
from kb.pipeline.preprocess import run_preprocess

app = typer.Typer(help="Pre-process raw sources into clean text documents.")


@app.callback(invoke_without_command=True)
def preprocess(ctx: typer.Context) -> None:
    config: Config = ctx.obj["config"]
    repo_root: Path = ctx.obj["repo_root"]
    run_preprocess(config, repo_root)
