from __future__ import annotations

from pathlib import Path

from kb.models import RawDocument
from kb.sources.base import SourceAdapter
from kb.sources.mintlify_postprocess import (
    extract_frontmatter,
    strip_frontmatter,
    transform_body,
)
from kb.utils.ids import document_id


def _derive_package(path: Path, docs_root: Path) -> str:
    parts = path.relative_to(docs_root).parts
    if parts[0] == "packages" and len(parts) > 1:
        return parts[1]
    return parts[0]


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
            metadata={
                "length": len(text),
                "format": "markdown",
                "package": _derive_package(path, self.root / "docs"),
            },
        )

    def post_process(self, doc: RawDocument) -> RawDocument:
        fm = extract_frontmatter(doc.body)
        body = strip_frontmatter(doc.body)
        body = transform_body(body)
        updates: dict = {"body": body}
        if fm.get("title"):
            updates["title"] = fm["title"]
        if fm.get("description"):
            updates["metadata"] = {**doc.metadata, "description": fm["description"]}
        return doc.model_copy(update=updates)
