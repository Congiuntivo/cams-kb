from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel


class SourceConfig(BaseModel):
    name: str
    type: str
    path: Path
    enabled: bool = True


class Config(BaseModel):
    sources: list[SourceConfig]


def load_config(path: Path = Path("kb.toml")) -> Config:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Config.model_validate(data)
