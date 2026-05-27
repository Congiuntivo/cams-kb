from __future__ import annotations

from pathlib import Path

from kb.config import SourceConfig
from kb.sources.base import SourceAdapter
from kb.sources.markdown import MarkdownAdapter
from kb.sources.mintlify import MintlifyAdapter

_REGISTRY: dict[str, type[SourceAdapter]] = {
    MintlifyAdapter.SOURCE_TYPE: MintlifyAdapter,
    MarkdownAdapter.SOURCE_TYPE: MarkdownAdapter,
}


def get_adapter(config: SourceConfig, repo_root: Path) -> SourceAdapter:
    cls = _REGISTRY.get(config.type)
    if cls is None:
        raise ValueError(
            f"Unknown source type '{config.type}'. Known: {list(_REGISTRY)}"
        )
    return cls(config, repo_root)
