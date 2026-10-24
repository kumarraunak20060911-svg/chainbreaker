from __future__ import annotations

from collections import Counter
from datetime import datetime
from math import comb
from typing import Any, Iterable, Sequence


def precision_recall_f1(expected: set[str], detected: set[str]) -> dict[str, float]:
    true_positive = len(expected & detected)
    precision = true_positive / len(detected) if detected else 0.0
    recall = true_positive / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def adjusted_rand_index(expected: Sequence[str], predicted: Sequence[str]) -> float:
    if len(expected) != len(predicted) or not expected:
        return 0.0
    contingency: Counter[tuple[str, str]] = Counter(zip(expected, predicted))
    expected_counts = Counter(expected)
    predicted_counts = Counter(predicted)
    index = sum(comb(count, 2) for count in contingency.values() if count >= 2)
    expected_pairs = sum(comb(count, 2) for count in expected_counts.values() if count >= 2)
    predicted_pairs = sum(comb(count, 2) for count in predicted_counts.values() if count >= 2)
    total_pairs = comb(len(expected), 2)
    if total_pairs == 0:
        return 1.0
    expected_index = expected_pairs * predicted_pairs / total_pairs
    max_index = (expected_pairs + predicted_pairs) / 2
    denominator = max_index - expected_index
    return (index - expected_index) / denominator if denominator else 1.0


def correct_chain_rate(chains: Iterable[Any], expected_stages: Sequence[str]) -> float:
    expected = tuple(expected_stages)
    if not expected:
        return 1.0
    for chain in chains:
        stages = tuple(getattr(chain, "stage_tags", ()))
        cursor = 0
        for stage in stages:
            if cursor < len(expected) and stage == expected[cursor]:
                cursor += 1
        if cursor == len(expected):
            return 1.0
    return 0.0


def time_to_detect(events: Iterable[Any], findings: Iterable[Any], attack_event_ids: set[str]) -> float:
    by_id = {event.event_id: event for event in events}
    attack_times = [by_id[event_id].timestamp for event_id in attack_event_ids if event_id in by_id]
    detection_times = [by_id[finding.event_id].timestamp for finding in findings if finding.event_id in by_id and finding.event_id in attack_event_ids]
    if not attack_times or not detection_times:
        return float("inf")
    return max(0.0, (min(detection_times) - min(attack_times)).total_seconds())


def events_per_second(event_count: int, started_at: datetime, finished_at: datetime) -> float:
    elapsed = max((finished_at - started_at).total_seconds(), 1e-9)
    return event_count / elapsed
