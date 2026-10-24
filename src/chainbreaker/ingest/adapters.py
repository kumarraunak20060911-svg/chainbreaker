from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Protocol

from .service import iter_rows


class LogSourceAdapter(Protocol):
    source_type: str

    def rows(self) -> Iterator[Mapping[str, object]]: ...


class FileLogAdapter:
    def __init__(self, path: str | Path, source_type: str = "file") -> None:
        self.path = Path(path)
        self.source_type = source_type

    def rows(self) -> Iterator[Mapping[str, object]]:
        yield from iter_rows(self.path)


def register_adapters() -> dict[str, type[FileLogAdapter]]:
    return {"csv": FileLogAdapter, "jsonl": FileLogAdapter, "auth": FileLogAdapter, "vpn": FileLogAdapter, "dns": FileLogAdapter, "web": FileLogAdapter, "iot": FileLogAdapter}
