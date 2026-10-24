from __future__ import annotations

import math
from collections import Counter
from collections import defaultdict
from statistics import mean, pstdev
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
    dns_events = [event for event in events if event.domain]
    findings = []
    by_host_domain: defaultdict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in dns_events:
        by_host_domain[(event.host or "unknown", event.domain or "")].append(event)
    domain_counts = Counter(event.domain for event in dns_events)
    for event in dns_events:
        domain = event.domain or ""
        labels = domain.split(".")
        label = labels[0] if labels else domain
        entropy = _entropy(label)
        rare = bool(event.metadata.get("first_seen", False)) or domain_counts.get(domain, 0) <= 1 or len(label) >= 18
        dga_like = entropy >= 3.5 and len(label) >= 10
        if dga_like or rare:
            findings.append(DetectionFinding(
                stable_id("find", "dns", event.event_id), event.event_id, "DNS-RARE-DOMAIN",
                "Rare or algorithmic-looking domain", "medium", Stage.COMMAND_AND_CONTROL,
                "Domain has elevated label entropy or is marked first-seen",
                {"domain": domain, "entropy": round(entropy, 3), "first_seen": rare},
            ))
    for (host, domain), items in by_host_domain.items():
        if len(items) < 3:
            continue
        ordered = sorted(items, key=lambda item: item.timestamp)
        intervals = [(right.timestamp - left.timestamp).total_seconds() for left, right in zip(ordered, ordered[1:])]
        average = mean(intervals)
        cv = pstdev(intervals) / average if average else 0.0
        if cv <= 0.25:
            findings.append(DetectionFinding(
                stable_id("find", "beacon", host, domain), ordered[-1].event_id, "DNS-BEACON-PERIODICITY",
                "Periodic DNS beacon", "high", Stage.COMMAND_AND_CONTROL,
                "Inter-arrival coefficient of variation is low, consistent with periodic beaconing",
                {"host": host, "domain": domain, "interval_seconds": round(average, 3), "inter_arrival_cv": round(cv, 3)},
            ))
        if len(items) >= 5:
            findings.append(DetectionFinding(
                stable_id("find", "dns-rate", host, domain), ordered[-1].event_id, "DNS-EWMA-RATE-BURST",
                "DNS query-rate burst", "medium", Stage.COMMAND_AND_CONTROL,
                "Repeated queries exceeded the small-window baseline for this host and destination",
                {"host": host, "domain": domain, "query_count": len(items)},
            ))
    return findings
