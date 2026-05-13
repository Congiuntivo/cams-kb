from __future__ import annotations

from pathlib import Path

import typer

from kb.cli.index import app as index_app
from kb.cli.preprocess import app as preprocess_app
from kb.cli.split import app as split_app
from kb.config import load_config

app = typer.Typer(name="kb", help="RAG knowledge base pipeline for the CARP system.")
app.add_typer(preprocess_app, name="pre-process")
app.add_typer(split_app, name="split")
app.add_typer(index_app, name="index")


@app.callback()
def main(
    ctx: typer.Context,
    config: Path = typer.Option(
        Path("kb.toml"), "--config", "-c", help="Path to kb.toml."
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)
    ctx.obj["repo_root"] = config.parent.resolve()
