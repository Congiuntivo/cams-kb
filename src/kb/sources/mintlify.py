from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from kb.models import RawDocument
from kb.sources.base import SourceAdapter
from kb.utils.console import warn
from kb.utils.ids import document_id


class MintlifyAdapter(SourceAdapter):
    SOURCE_TYPE = "mintlify"

    def discover(self) -> list[Path]:
        docs_root = self.root / "docs"
        if not docs_root.exists():
            return []
        return sorted(docs_root.rglob("*.mdx"))

    def extract(self, path: Path) -> RawDocument:
        source_path = str(path.relative_to(self.root))
        with path.open(encoding="utf-8") as f:
            text = f.read()
            return RawDocument(
                id=document_id(self.config.name, source_path),
                source_name=self.config.name,
                source_path=source_path,
                title=path.stem,
                body=text,
                metadata={"length": len(text)},
            )

    def extract_all(self) -> Generator[RawDocument, None, None]:
        for path in self.discover():
            if path.suffix == ".mdx":
                yield self.post_process(self.extract(path))
            else:
                warn(f"Unsupported file type for Mintlify source: {path}")
