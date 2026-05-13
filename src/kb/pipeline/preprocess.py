from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from kb.config import Config
from kb.models import RawDocument
from kb.sources.registry import get_adapter
from kb.utils.console import info, success
from kb.utils.storage import save_documents


def run_preprocess(config: Config, repo_root: Path) -> None:
    output_path = repo_root / config.pipeline.documents_path
    info("Reading raw sources...")
    count = save_documents(_extract_all(config, repo_root), output_path)
    success(f"Saved [bold]{count}[/bold] documents → {output_path}")


def _extract_all(config: Config, repo_root: Path) -> Generator[RawDocument, None, None]:
    for source in config.enabled_sources:
        adapter = get_adapter(source, repo_root)
        yield from adapter.extract_all()
