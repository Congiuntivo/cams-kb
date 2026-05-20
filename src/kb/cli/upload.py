from __future__ import annotations

from pathlib import Path

import typer

from kb.config import Config
from kb.pipeline.upload import run_upload

app = typer.Typer(help="Create the Qdrant collection and upload index points.")


@app.callback(invoke_without_command=True)
def upload(
    ctx: typer.Context,
    recreate: bool = typer.Option(
        False,
        "--recreate",
        help="Delete and recreate the collection if it already exists.",
    ),
) -> None:
    config: Config = ctx.obj["config"]
    repo_root: Path = ctx.obj["repo_root"]
    run_upload(config, recreate, repo_root)
