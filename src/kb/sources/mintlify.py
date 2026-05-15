from __future__ import annotations

from pathlib import Path

from kb.models import RawDocument
from kb.sources.base import SourceAdapter
from kb.sources.mintlify_postprocess import transform_body
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
        text = path.read_text(encoding="utf-8")
        return RawDocument(
            id=document_id(self.config.name, source_path),
            source_name=self.config.name,
            source_path=source_path,
            title=path.stem,
            body=text,
            metadata={"length": len(text), "format": "markdown"},
        )

    def post_process(self, doc: RawDocument) -> RawDocument:
        return doc.model_copy(update={"body": transform_body(doc.body)})
