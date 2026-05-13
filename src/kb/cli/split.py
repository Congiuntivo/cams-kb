from __future__ import annotations

from pathlib import Path

import typer

from kb.config import Config
from kb.pipeline.split import run_split

app = typer.Typer(help="Split pre-processed documents into chunks.")


@app.callback(invoke_without_command=True)
def split(
    ctx: typer.Context,
    source: list[str] = typer.Option(
        [], "--source", "-s", help="Source name to split (repeatable)."
    ),
) -> None:
    config: Config = ctx.obj["config"]
    repo_root: Path = ctx.obj["repo_root"]
    run_split(config, source or None, repo_root)
