from __future__ import annotations

from pathlib import Path

from kb.models import RawDocument
from kb.sources.base import SourceAdapter
from kb.sources.mintlify_postprocess import extract_frontmatter, strip_frontmatter
from kb.utils.ids import document_id


class MarkdownAdapter(SourceAdapter):
    SOURCE_TYPE = "markdown"

    def discover(self) -> list[Path]:
        return sorted(self.root.rglob("*.md"))

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
        fm = extract_frontmatter(doc.body)
        body = strip_frontmatter(doc.body)
        updates: dict = {"body": body}
        if fm.get("title"):
            updates["title"] = fm["title"]
        if fm.get("description"):
            updates["metadata"] = {**doc.metadata, "description": fm["description"]}
        return doc.model_copy(update=updates)
