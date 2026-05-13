from __future__ import annotations

from pathlib import Path

from kb.config import Config


def run_index_qdrant(
    config: Config, source_names: list[str] | None, repo_root: Path
) -> None:
    raise NotImplementedError("index qdrant is not yet implemented")
