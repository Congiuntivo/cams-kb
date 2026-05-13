from __future__ import annotations

from pathlib import Path

from kb.config import Config, SourceConfig
from kb.sources.registry import get_adapter
from kb.utils.console import info, success


def run_preprocess(
    config: Config, source_names: list[str] | None, repo_root: Path
) -> None:
    info("Reading raw sources...")
    sources = _select_sources(config, source_names)
    for source in sources:
        adapter = get_adapter(source, repo_root)
        count = sum(1 for _ in adapter.extract_all())
        success(f"[bold]{source.name}[/bold]: {count} documents")


def _select_sources(config: Config, names: list[str] | None) -> list[SourceConfig]:
    enabled = [s for s in config.sources if s.enabled]
    if not names:
        return enabled
    return [s for s in enabled if s.name in names]
