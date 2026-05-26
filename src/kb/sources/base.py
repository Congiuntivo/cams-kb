from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path

import pathspec

from kb.config import SourceConfig
from kb.models import RawDocument


class SourceAdapter(ABC):
    def __init__(self, config: SourceConfig, repo_root: Path) -> None:
        self.config = config
        self.root = repo_root / config.path
        self._blacklist_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", config.blacklist
        )
        self._whitelist_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", config.whitelist
        )

    def _is_excluded(self, path: Path) -> bool:
        rel = str(path.relative_to(self.root))
        if self._blacklist_spec.match_file(rel):
            return True
        if self.config.whitelist and not self._whitelist_spec.match_file(rel):
            return True
        return False

    @abstractmethod
    def discover(self) -> list[Path]:
        """Return all processable file paths in this source."""

    @abstractmethod
    def extract(self, path: Path) -> RawDocument:
        """Parse one source file into a RawDocument."""

    def post_process(self, doc: RawDocument) -> RawDocument:
        """Source-specific cleaning hook. Override to strip source-specific junk."""
        return doc

    def extract_all(self) -> Generator[RawDocument, None, None]:
        for path in self.discover():
            if not self._is_excluded(path):
                yield self.post_process(self.extract(path))
