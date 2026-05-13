from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path

from kb.config import SourceConfig
from kb.models import RawDocument


class SourceAdapter(ABC):
    def __init__(self, config: SourceConfig, repo_root: Path) -> None:
        self.config = config
        self.root = repo_root / config.path

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
            yield self.post_process(self.extract(path))
