from __future__ import annotations

from collections.abc import Generator, Iterable
from pathlib import Path

from kb.models import RawDocument


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
