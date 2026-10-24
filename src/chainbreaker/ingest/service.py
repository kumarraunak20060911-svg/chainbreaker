from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from chainbreaker.domain.models import Event

from .normalize import normalize_events
from .pseudonymize import pseudonymize_events
from .schemas import event_from_row


def read_rows(path: str | Path | io.TextIOBase) -> list[dict[str, Any]]:
    if isinstance(path, io.TextIOBase):
        text = path.read()
        return [json.loads(line) for line in text.splitlines() if line.strip()] if getattr(path, "name", "").endswith(".jsonl") else list(csv.DictReader(io.StringIO(text)))
    source = Path(path)
    if source.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
    with source.open(newline="") as handle:
        return list(csv.DictReader(handle))


def ingest_rows(rows: Iterable[Mapping[str, Any]], *, pseudonym_key: bytes = b"chainbreaker-demo-key") -> list[Event]:
    events = [event_from_row(row, index) for index, row in enumerate(rows)]
    return normalize_events(pseudonymize_events(events, pseudonym_key))


def ingest_file(path: str | Path, *, pseudonym_key: bytes = b"chainbreaker-demo-key") -> list[Event]:
    return ingest_rows(read_rows(path), pseudonym_key=pseudonym_key)
