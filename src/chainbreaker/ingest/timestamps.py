from __future__ import annotations

from datetime import timedelta
from statistics import median
from typing import Iterable
from dataclasses import replace

from chainbreaker.domain.models import Event


def estimate_clock_skew(events: Iterable[Event]) -> dict[str, float]:
    items = list(events)
    if not items:
        return {}
    explicit: dict[str, list[float]] = {}
    for event in items:
        value = event.metadata.get("clock_offset_seconds")
        if value not in (None, ""):
            try:
                explicit.setdefault(event.source.value, []).append(float(value))
            except (TypeError, ValueError):
                continue
    return {
        source: round(median(values), 3) if values else 0.0
        for source, values in ((event.source.value, explicit.get(event.source.value, [])) for event in items)
    }


def apply_clock_skew(events: Iterable[Event], offsets: dict[str, float]) -> list[Event]:
    adjusted: list[Event] = []
    for event in events:
        delta = timedelta(seconds=offsets.get(event.source.value, 0.0))
        adjusted.append(replace(event, timestamp=event.timestamp - delta))
    return sorted(adjusted, key=lambda event: (event.timestamp, event.event_id))
