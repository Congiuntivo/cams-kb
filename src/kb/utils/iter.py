from __future__ import annotations

from itertools import islice
from typing import Generator, TypeVar

T = TypeVar("T")


def batched(items: list[T], size: int) -> Generator[list[T], None, None]:
    it = iter(items)
    while batch := list(islice(it, size)):
        yield batch
