from __future__ import annotations

from collections.abc import Generator, Iterable
from pathlib import Path

from kb.models import Chunk, IndexPoint, RawDocument


def save_documents(documents: Iterable[RawDocument], path: Path) -> int:
    if not path.suffix == ".jsonl":
        raise ValueError("Output path must have .jsonl extension")

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(doc.model_dump_json())
            f.write("\n")
            count += 1
    return count


def load_documents(path: Path) -> Generator[RawDocument, None, None]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield RawDocument.model_validate_json(line)


def save_chunks(chunks: Iterable[Chunk], path: Path) -> int:
    if not path.suffix == ".jsonl":
        raise ValueError("Output path must have .jsonl extension")

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk.model_dump_json())
            f.write("\n")
            count += 1
    return count


def load_chunks(path: Path) -> Generator[Chunk, None, None]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield Chunk.model_validate_json(line)


def save_index_points(points: Iterable[IndexPoint], path: Path) -> int:
    if not path.suffix == ".jsonl":
        raise ValueError("Output path must have .jsonl extension")

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for point in points:
            f.write(point.model_dump_json())
            f.write("\n")
            count += 1
    return count


def load_index_points(path: Path) -> Generator[IndexPoint, None, None]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield IndexPoint.model_validate_json(line)
