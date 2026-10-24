from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from chainbreaker.domain.enums import EventSource
from chainbreaker.domain.models import Event


@dataclass(frozen=True, slots=True)
class ParsedRow:
    row_id: str
    values: Mapping[str, Any]


def event_from_row(row: Mapping[str, Any], index: int) -> Event:
    timestamp = datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
    source = EventSource(str(row.get("source", "auth")).lower())
    return Event(
        event_id=str(row.get("event_id") or f"evt-{index:05d}"),
        timestamp=timestamp,
        source=source,
        event_type=str(row.get("event_type", "unknown")),
        account=_value(row, "account"),
        host=_value(row, "host"),
        ip=_value(row, "ip"),
        device_id=_value(row, "device_id"),
        device_class=_value(row, "device_class"),
        peer=_value(row, "peer"),
        domain=_value(row, "domain"),
        command=_value(row, "command"),
        topic=_value(row, "topic"),
        session_id=_value(row, "session_id"),
        payload_size=_int_value(row.get("payload_size")),
        success=_bool_value(row.get("success")),
        row_id=str(row.get("row_id") or f"row-{index:05d}"),
        metadata={key: value for key, value in row.items() if key not in {
            "timestamp", "source", "event_id", "event_type", "account", "host", "ip", "device_id",
            "device_class", "peer", "domain", "command", "topic", "session_id", "payload_size", "success", "row_id",
        }},
    )


def _value(row: Mapping[str, Any], key: str) -> str | None:
    value = row.get(key)
    return None if value in (None, "") else str(value)


def _int_value(value: Any) -> int | None:
    return None if value in (None, "") else int(value)


def _bool_value(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "success"}
