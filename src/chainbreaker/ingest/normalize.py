from __future__ import annotations

from collections.abc import Iterable
from datetime import timezone
from dataclasses import replace

from chainbreaker.domain.models import Event


def normalize_events(events: Iterable[Event]) -> list[Event]:
    normalized: list[Event] = []
    for event in events:
        timestamp = event.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        normalized.append(replace(event, timestamp=timestamp))
    return sorted(normalized, key=lambda item: (item.timestamp, item.event_id))
