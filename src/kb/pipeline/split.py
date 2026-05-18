from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from kb.config import ChunkingConfig, Config
from kb.models import Chunk, RawDocument
from kb.utils.console import error, info, success
from kb.utils.ids import chunk_id
from kb.utils.storage import load_documents, save_chunks

_HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]


def run_split(config: Config, source_names: list[str] | None, repo_root: Path) -> None:
    input_path = repo_root / config.pipeline.documents_path
    if not input_path.exists():
        error(
            f"Documents file not found: {input_path}. Run [bold]kb pre-process[/bold] first."
        )
        return

    output_path = repo_root / config.pipeline.chunks_path

    documents = _filter_documents(list(load_documents(input_path)), source_names)

    info(f"Splitting [bold]{len(documents)}[/bold] documents...")

    counts: dict[str, int] = defaultdict(int)
    chunks: list[Chunk] = []
    for doc in documents:
        doc_chunks = _split_document(doc, config.pipeline.chunking)
        counts[doc.source_name] += len(doc_chunks)
        chunks.extend(doc_chunks)

    for source_name, count in sorted(counts.items()):
        info(f"  [dim]{source_name}[/dim]: {count} chunks")

    total = save_chunks(chunks, output_path)
    success(f"Saved [bold]{total}[/bold] chunks → {output_path}")


def _filter_documents(
    documents: list[RawDocument], source_names: list[str] | None
) -> list[RawDocument]:
    if source_names is None:
        return documents
    available = {doc.source_name for doc in documents}
    for name in source_names:
        if name not in available:
            error(
                f"Source [bold]{name}[/bold] not found in documents (available: {', '.join(sorted(available))})."
            )
    requested = set(source_names)
    return [doc for doc in documents if doc.source_name in requested]


def _split_document(doc: RawDocument, chunking: ChunkingConfig) -> list[Chunk]:
    header_splitter = MarkdownHeaderTextSplitter(
        _HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunking.chunk_size,
        chunk_overlap=chunking.chunk_overlap,
    )

    header_docs = header_splitter.split_text(doc.body)

    chunks: list[Chunk] = []
    for header_doc in header_docs:
        sub_texts = char_splitter.split_text(header_doc.page_content)
        for text in sub_texts:
            index = len(chunks)
            chunks.append(
                Chunk(
                    id=chunk_id(doc.id, index),
                    doc_id=doc.id,
                    source_name=doc.source_name,
                    chunk_index=index,
                    text=text,
                    metadata={
                        "headers": header_doc.metadata,
                        "doc_title": doc.title,
                        "source_path": doc.source_path,
                    },
                )
            )

    if not chunks:
        chunks.append(
            Chunk(
                id=chunk_id(doc.id, 0),
                doc_id=doc.id,
                source_name=doc.source_name,
                chunk_index=0,
                text=doc.body,
                metadata={
                    "headers": {},
                    "doc_title": doc.title,
                    "source_path": doc.source_path,
                },
            )
        )

    return chunks
