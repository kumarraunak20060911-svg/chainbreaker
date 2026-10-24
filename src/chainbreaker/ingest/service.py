from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from chainbreaker.domain.models import Event

from .diagnostics import IngestDiagnostics, RejectedRow
from .normalize import normalize_events
from .pseudonymize import pseudonymize_events
from .schemas import event_from_row
from .timestamps import apply_clock_skew, estimate_clock_skew
from chainbreaker.correlation.aliases import infer_aliases


def read_rows(path: str | Path | io.TextIOBase) -> list[dict[str, Any]]:
    if not isinstance(path, (str, Path)):
        raw = path.read()
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        name = str(getattr(path, "name", "")).lower()
        return [json.loads(line) for line in text.splitlines() if line.strip()] if name.endswith(".jsonl") else list(csv.DictReader(io.StringIO(text)))
    source = Path(path)
    if source.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
    with source.open(newline="") as handle:
        return list(csv.DictReader(handle))


def iter_rows(path: str | Path | io.TextIOBase):
    """Stream CSV/JSONL rows without retaining the complete input in memory."""
    if not isinstance(path, (str, Path)):
        name = str(getattr(path, "name", "")).lower()
        if name.endswith(".jsonl"):
            for line in path:
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.strip():
                    yield json.loads(text)
            return
        yield from csv.DictReader(path)
        return
    source = Path(path)
    if source.suffix.lower() == ".jsonl":
        with source.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
        return
    with source.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def ingest_rows(rows: Iterable[Mapping[str, Any]], *, pseudonym_key: bytes = b"chainbreaker-demo-key") -> list[Event]:
    return ingest_rows_diagnostics(rows, pseudonym_key=pseudonym_key)[0]


def ingest_rows_diagnostics(
    rows: Iterable[Mapping[str, Any]], *, pseudonym_key: bytes = b"chainbreaker-demo-key"
) -> tuple[list[Event], IngestDiagnostics]:
    accepted: list[Event] = []
    rejected: list[RejectedRow] = []
    for index, row in enumerate(rows, start=1):
        try:
            accepted.append(event_from_row(row, index - 1))
        except (KeyError, TypeError, ValueError) as exc:
            rejected.append(RejectedRow(index, str(exc), dict(row)))
    normalized = normalize_events(pseudonymize_events(accepted, pseudonym_key))
    offsets = estimate_clock_skew(normalized)
    corrected = apply_clock_skew(normalized, offsets) if any(abs(value) > 0.001 for value in offsets.values()) else normalized
    aliases = infer_aliases(corrected)
    corrections = tuple(
        [f"applied {source} clock offset of {offset:.3f}s" for source, offset in offsets.items() if abs(offset) > 0.001]
        + ([f"inferred {sum(len(values) for values in aliases.values())} account-to-host alias candidates"] if aliases else [])
    )
    fingerprinted = []
    for event in corrected:
        basis = "|".join(str(value or "") for value in (event.row_id, event.timestamp.isoformat(), event.source.value, event.event_type, event.account, event.host, event.ip, event.device_id, event.domain, event.command, event.session_id))
        fingerprint = hashlib.sha256(basis.encode()).hexdigest()
        metadata = dict(event.metadata)
        metadata["fingerprint"] = fingerprint
        from dataclasses import replace
        fingerprinted.append(replace(event, metadata=metadata))
    corrected = fingerprinted
    diagnostics = IngestDiagnostics(
        accepted_rows=len(corrected),
        rejected_rows=tuple(rejected),
        clock_offsets=offsets,
        alias_candidates={key: tuple(sorted(values)) for key, values in aliases.items()},
        corrections=corrections,
    )
    return corrected, diagnostics


def ingest_file(path: str | Path, *, pseudonym_key: bytes = b"chainbreaker-demo-key") -> list[Event]:
    return ingest_rows(read_rows(path), pseudonym_key=pseudonym_key)


def ingest_file_diagnostics(path: str | Path, *, pseudonym_key: bytes = b"chainbreaker-demo-key") -> tuple[list[Event], IngestDiagnostics]:
    return ingest_rows_diagnostics(read_rows(path), pseudonym_key=pseudonym_key)
