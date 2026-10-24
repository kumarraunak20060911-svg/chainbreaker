from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RejectedRow:
    row_number: int
    reason: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IngestDiagnostics:
    accepted_rows: int
    rejected_rows: tuple[RejectedRow, ...] = ()
    clock_offsets: dict[str, float] = field(default_factory=dict)
    alias_candidates: dict[str, tuple[str, ...]] = field(default_factory=dict)
    corrections: tuple[str, ...] = ()
    pseudonymized_fields: tuple[str, ...] = ("account", "host", "ip", "device_id", "peer", "domain", "session_id")
