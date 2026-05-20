from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Generator

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    Modifier,
    MultiVectorComparator,
    MultiVectorConfig,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from kb.config import Config
from kb.models import IndexPoint
from kb.utils.console import error, info, success, warn
from kb.utils.storage import load_index_points


def run_upload(config: Config, recreate: bool, repo_root: Path) -> None:
    input_path = repo_root / config.indexing.points_path
    if not input_path.exists():
        error(
            f"Points file not found: {input_path}. Run [bold]kb index[/bold] first or check your configuration."
        )
        return

    points = list(load_index_points(input_path))
    if not points:
        warn("No points to upload.")
        return

    dense_dim, multi_dim = _infer_dims(points[0])
    collection_name = config.indexing.collection_name
    client = QdrantClient(url=config.indexing.qdrant_url)

    _ensure_collection(client, collection_name, dense_dim, multi_dim, recreate)

    info(
        f"Uploading [bold]{len(points)}[/bold] points to [bold]{collection_name}[/bold]"
        f" in batches of {config.indexing.upload_batch_size}..."
    )

    uploaded = 0
    for batch in _batched(points, config.indexing.upload_batch_size):
        _upload_batch(client, collection_name, batch)
        uploaded += len(batch)
        info(f"\tUploaded {uploaded}/{len(points)} points")

    success(
        f"Uploaded [bold]{uploaded}[/bold] points → {collection_name} at {config.indexing.qdrant_url}"
    )


def _infer_dims(point: IndexPoint) -> tuple[int, int]:
    dense_dim = len(point.vectors.dense)
    multi_dim = len(point.vectors.multi[0]) if point.vectors.multi else 0
    return dense_dim, multi_dim


def _ensure_collection(
    client: QdrantClient,
    name: str,
    dense_dim: int,
    multi_dim: int,
    recreate: bool,
) -> None:
    exists = client.collection_exists(collection_name=name)
    if exists and not recreate:
        warn(
            f"Collection [bold]{name}[/bold] already exists — upserting into it. "
            "Pass [bold]--recreate[/bold] to delete and recreate it."
        )
        return
    if exists:
        client.delete_collection(collection_name=name)
        info(f"Deleted existing collection [bold]{name}[/bold].")

    client.create_collection(
        collection_name=name,
        vectors_config={
            "dense": VectorParams(size=dense_dim, distance=Distance.COSINE),
            "multi": VectorParams(
                size=multi_dim,
                distance=Distance.COSINE,
                multivector_config=MultiVectorConfig(
                    comparator=MultiVectorComparator.MAX_SIM
                ),
                hnsw_config=HnswConfigDiff(m=0),
            ),
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(modifier=Modifier.IDF),
        },
    )
    info(
        f"Created collection [bold]{name}[/bold] (dense={dense_dim}, multi={multi_dim})."
    )


def _upload_batch(client: QdrantClient, name: str, points: list[IndexPoint]) -> None:
    structs = [
        PointStruct(
            id=p.id,
            vector={
                "dense": p.vectors.dense,
                "sparse": SparseVector(
                    indices=p.vectors.sparse.indices,
                    values=p.vectors.sparse.values,
                ),
                "multi": p.vectors.multi,
            },
            payload=p.payload.model_dump(),
        )
        for p in points
    ]
    client.upsert(collection_name=name, points=structs)


def _batched(
    items: list[IndexPoint], size: int
) -> Generator[list[IndexPoint], None, None]:
    it = iter(items)
    while batch := list(islice(it, size)):
        yield batch
