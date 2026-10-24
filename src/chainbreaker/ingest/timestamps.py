from __future__ import annotations

from datetime import timedelta
from statistics import median
from typing import Iterable
from dataclasses import replace

from chainbreaker.domain.models import Event


def estimate_clock_skew(events: Iterable[Event]) -> dict[str, float]:
    by_source: dict[str, list[float]] = {}
    ordered = sorted(events, key=lambda event: event.timestamp)
    if not ordered:
        return {}
    anchor = ordered[0].timestamp
    for event in ordered:
        by_source.setdefault(event.source.value, []).append((event.timestamp - anchor).total_seconds())
    global_median = median(value for values in by_source.values() for value in values)
    return {source: median(values) - global_median for source, values in by_source.items()}


def apply_clock_skew(events: Iterable[Event], offsets: dict[str, float]) -> list[Event]:
    adjusted: list[Event] = []
    for event in events:
        delta = timedelta(seconds=offsets.get(event.source.value, 0.0))
        adjusted.append(replace(event, timestamp=event.timestamp - delta))
    return sorted(adjusted, key=lambda event: (event.timestamp, event.event_id))
