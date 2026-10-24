from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Iterable


def character_ngram_surprisal(value: str, n: int = 3) -> float:
    text = value.lower().strip()
    if len(text) < n:
        return 0.0
    grams = [text[index:index + n] for index in range(len(text) - n + 1)]
    counts = Counter(grams)
    total = len(grams)
    return sum(-math.log2(count / total) for count in counts.values()) / max(total, 1)


def ewma_z_scores(values: Iterable[float], *, alpha: float = 0.35) -> list[float]:
    scores: list[float] = []
    values = list(values)
    if not values:
        return scores
    mean = values[0]
    variance = 1.0
    for value in values:
        deviation = abs(value - mean) / max(math.sqrt(variance), 1.0)
        scores.append(deviation)
        delta = value - mean
        mean = alpha * value + (1 - alpha) * mean
        variance = alpha * delta * delta + (1 - alpha) * variance
    return scores


class CountMinSketch:
    """Small deterministic sketch used for destination rarity without retaining raw histories."""

    def __init__(self, width: int = 128, depth: int = 4) -> None:
        self.width = width
        self.depth = depth
        self._table = [[0 for _ in range(width)] for _ in range(depth)]

    def _index(self, value: str, row: int) -> int:
        digest = hashlib.blake2b(f"{row}:{value}".encode(), digest_size=8).digest()
        return int.from_bytes(digest, "big") % self.width

    def add(self, value: str, count: int = 1) -> None:
        for row in range(self.depth):
            self._table[row][self._index(value, row)] += count

    def estimate(self, value: str) -> int:
        return min(self._table[row][self._index(value, row)] for row in range(self.depth))
