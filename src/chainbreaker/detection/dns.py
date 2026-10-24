from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

from chainbreaker.domain.enums import Stage
from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event

from .finding import DetectionFinding


def _entropy(value: str) -> float:
    counts = Counter(value)
    size = len(value) or 1
    return -sum((count / size) * math.log2(count / size) for count in counts.values())


def detect_dns(events: Iterable[Event]) -> list[DetectionFinding]:
    findings = []
    for event in events:
        domain = event.domain or ""
        labels = domain.split(".")
        label = labels[0] if labels else domain
        entropy = _entropy(label)
        rare = bool(event.metadata.get("first_seen", False)) or len(label) >= 18
        dga_like = entropy >= 3.5 and len(label) >= 10
        if dga_like or rare:
            findings.append(DetectionFinding(
                stable_id("find", "dns", event.event_id), event.event_id, "DNS-RARE-DOMAIN",
                "Rare or algorithmic-looking domain", "medium", Stage.COMMAND_AND_CONTROL,
                "Domain has elevated label entropy or is marked first-seen",
                {"domain": domain, "entropy": round(entropy, 3), "first_seen": rare},
            ))
    return findings
